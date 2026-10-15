"""UrduPy's prerelease CPython frontend; supported grammar is in docs/compiler.md.

The M0 laboratory remains separate. This frontend validates its intermediate
with CPython, handles 3.12+ f-string fields, and compiles original-source spans.
"""

import ast
import io
import keyword
import re
import sys
import token
import tokenize
from dataclasses import dataclass
from types import CodeType

from .lexicon import PRODUCTION_KEYWORDS, SOFT_KEYWORDS
from .source_map import Translation, build_translation, byte_to_character, line_starts


_SKIP = {tokenize.COMMENT, tokenize.NL, tokenize.ENCODING, tokenize.ENDMARKER}
_OPEN = {"(", "[", "{"}
_CLOSE = {")", "]", "}"}
# Older PEP-701 implementations remove '#' suffixes even within a debug label's
# string/nested-string spelling. Probe the host's AST rather than assume a patch
# version; later fixes can change this without a language-minor transition.
_LEGACY_DEBUG_HASHES = ast.parse('f"{\'#\'=}"', mode="eval").body.values[0].value != "'#'="


def _require_interpreter():
    if sys.version_info < (3, 12):
        raise RuntimeError("The production UrduPy compiler requires CPython 3.12 or newer")


def _tokens(source):
    # Normalize the tokenizer view only. Output uses untouched original slices,
    # including CRLF, bare CR and multiline literal spelling.
    view = source.replace("\r\n", "\n").replace("\r", "\n")
    result = []
    comments = []
    formatted_depth = 0
    string_starts = {token.FSTRING_START, getattr(token, "TSTRING_START", None)}
    string_ends = {token.FSTRING_END, getattr(token, "TSTRING_END", None)}
    stream = tokenize.generate_tokens(io.StringIO(view).readline)
    try:
        for item in stream:
            if item.type in string_starts:
                formatted_depth += 1
            elif item.type in string_ends:
                formatted_depth -= 1
            elif item.type == tokenize.COMMENT:
                comments.append((item, formatted_depth))
            if item.type not in _SKIP:
                result.append(item)
    except (tokenize.TokenError, SyntaxError, IndentationError):
        # Keep the useful prefix. CPython parsing of the translated source owns
        # invalid/incomplete-input errors, including codeop's compiler flags.
        pass
    return result, comments


def _word(item):
    return PRODUCTION_KEYWORDS.get(item.string, item.string)


def _from_delimiter(tokens, start):
    end = start
    while end < len(tokens) and tokens[end].type != tokenize.NEWLINE and tokens[end].string != ";":
        end += 1
    for candidate in range(start, end):
        if tokens[candidate].type != tokenize.NAME or _word(tokens[candidate]) != "import":
            continue
        path = "".join(item.string for item in tokens[start:candidate])
        words = []
        expect = "symbol"
        for item in tokens[candidate + 1:end]:
            text = item.string
            if item.type == tokenize.NAME:
                if expect == "symbol":
                    expect = "after_symbol"
                elif expect == "alias":
                    expect = "after_alias"
                elif expect == "after_symbol" and _word(item) == "as":
                    text, expect = "as", "alias"
            elif text == ",":
                expect = "symbol"
            words.append(text)
        try:
            tree = ast.parse("from " + path + " import " + " ".join(words))
        except SyntaxError:
            continue
        if len(tree.body) == 1 and isinstance(tree.body[0], ast.ImportFrom):
            return candidate
    return None


def _match_block_indent(tokens, start):
    """Return the INDENT index for a block-shaped match header, if present."""
    depth = 0
    for index in range(start + 1, len(tokens)):
        item = tokens[index]
        if item.type == tokenize.NEWLINE:
            return None
        if item.string in _OPEN:
            depth += 1
        elif item.string in _CLOSE:
            depth -= 1
        elif depth == 0 and item.string in {"=", ";"}:
            return None
        elif depth == 0 and item.string == ":":
            if index + 2 < len(tokens) and tokens[index + 1].type == tokenize.NEWLINE and tokens[index + 2].type == tokenize.INDENT:
                return index + 2
    return None


@dataclass
class _Field:
    opening: object
    formatted_depth: int = 0
    mode: str = "expression"
    debug: object = None
    debug_end: object = None
    closed: bool = False


def _debug_fields(tokens):
    """Track native f-string field delimiters separately from dict/call braces."""
    stack = []
    fields = []
    formatted_depth = 0
    string_starts = {token.FSTRING_START, getattr(token, "TSTRING_START", None)}
    string_ends = {token.FSTRING_END, getattr(token, "TSTRING_END", None)}
    for index, item in enumerate(tokens):
        if item.type in string_starts:
            formatted_depth += 1
        elif item.type in string_ends:
            formatted_depth -= 1
        if item.type == token.FSTRING_START:
            stack.append("fstring")
        elif item.type == token.FSTRING_END:
            if stack and stack[-1] == "fstring":
                stack.pop()
        elif item.type == tokenize.OP:
            top = stack[-1] if stack else None
            if item.string in _OPEN:
                if item.string == "{" and (top == "fstring" or isinstance(top, _Field) and top.mode == "format"):
                    field = _Field(item, formatted_depth)
                    fields.append(field)
                    stack.append(field)
                else:
                    stack.append(item.string)
            elif item.string in _CLOSE and stack:
                if isinstance(top, _Field):
                    top.closed = True
                stack.pop()
            elif item.string == ":" and isinstance(top, _Field):
                top.mode = "format"
            elif item.string == "=" and isinstance(top, _Field) and top.mode == "expression":
                top.debug = item
                if index + 1 < len(tokens):
                    top.debug_end = tokens[index + 1]
    return fields


def _template_ranges(tokens):
    start_type = getattr(token, "TSTRING_START", None)
    end_type = getattr(token, "TSTRING_END", None)
    opened = []
    ranges = []
    if start_type is None:
        return ranges
    for item in tokens:
        if item.type == start_type:
            opened.append(item)
        elif item.type == end_type and opened:
            ranges.append((opened.pop(), item))
    return ranges


def translate_with_map(source: str, filename: str = "<urdupy>") -> Translation:
    """Translate without executing; return original text and a location map."""
    _require_interpreter()
    if not isinstance(source, str):
        raise TypeError("source must be a str decoded from UTF-8")
    bom = int(source.startswith("\ufeff"))
    body = source[bom:]
    starts = line_starts(body)

    def offset(position):
        row, column = position
        return bom + starts[row - 1] + column

    tokens, comments = _tokens(body)
    replacements = []
    brackets = []
    previous = previous_type = previous_python = None
    statement_start = True
    import_mode = None
    import_expect = "symbol"
    delimiter = None
    definition_header = False
    indent = 0
    match_levels = set()
    match_indents = set()

    for index, item in enumerate(tokens):
        if item.type == tokenize.INDENT:
            indent += 1
            if index in match_indents:
                match_levels.add(indent)
            continue
        if item.type == tokenize.DEDENT:
            indent = max(0, indent - 1)
            match_levels = {level for level in match_levels if level <= indent}
            continue
        text = item.string
        mapped = _word(item) if item.type == tokenize.NAME else text
        next_text = tokens[index + 1].string if index + 1 < len(tokens) else None
        replacement = text

        if item.type == tokenize.NEWLINE or text == ";":
            statement_start = True
            import_mode = None
            definition_header = False
        elif import_mode:
            if import_mode == "path":
                if index == delimiter:
                    replacement, import_mode, import_expect = mapped, "names", "symbol"
            elif item.type == tokenize.NAME:
                if import_expect == "symbol" or previous == ".":
                    import_expect = "after_symbol"
                elif import_expect == "alias":
                    import_expect = "after_alias"
                elif import_expect == "after_symbol" and mapped == "as":
                    replacement, import_expect = mapped, "alias"
            elif text == ",":
                import_expect = "symbol"
        elif item.type == tokenize.NAME:
            attribute = previous == "."
            call_label = next_text == "=" and brackets and brackets[-1] == "call"
            if not attribute and not call_label:
                replacement = mapped
                if statement_start and not brackets and (text == "match" or SOFT_KEYWORDS.get(text) == "match"):
                    block = _match_block_indent(tokens, index)
                    if block is not None:
                        replacement = "match"
                        match_indents.add(block)
                elif statement_start and not brackets and indent in match_levels and SOFT_KEYWORDS.get(text) == "case":
                    replacement = "case"
                if statement_start and mapped in {"import", "from"}:
                    import_mode = "path" if mapped == "from" else "names"
                    import_expect = "symbol"
                    if mapped == "from":
                        delimiter = _from_delimiter(tokens, index + 1)
                if mapped == "def":
                    definition_header = True
            # CPython 3.15's English lazy-import modifier is contextual. Preserve
            # imported API words after it just as for an ordinary import.
            statement_start = bool(
                statement_start and text == "lazy" and index + 1 < len(tokens)
                and _word(tokens[index + 1]) in {"import", "from"}
            )
        elif text == ":" and not brackets:
            statement_start = True
            definition_header = False
        else:
            statement_start = False

        if item.type == tokenize.OP and text in _OPEN:
            callable_before = previous in {")", "]"} or previous_type in {tokenize.STRING, tokenize.NUMBER, token.FSTRING_END} or (
                previous_python is not None and previous_python.isidentifier() and not keyword.iskeyword(previous_python)
            )
            if text == "(" and definition_header and not brackets:
                brackets.append("parameters")
                definition_header = False
            else:
                brackets.append("call" if text == "(" and callable_before else "group")
        elif item.type == tokenize.OP and text in _CLOSE and brackets:
            brackets.pop()

        if replacement != text:
            replacements.append((offset(item.start), offset(item.end), replacement, "keyword"))
        previous, previous_type, previous_python = text, item.type, replacement

    # A translated debug expression must still print the original source label.
    # Explicit constant fields work with raw strings, quote reuse, comments and
    # nested fields, and preserve semantics in the intermediate Python as well.
    keyword_edits = tuple(replacements)
    for first, last in _template_ranges(tokens):
        if any(offset(first.start) <= start < offset(last.end) for start, _, _, _ in keyword_edits):
            row, column = first.start
            identity = build_translation(source, filename, ())
            raise SyntaxError(
                "Urdu syntax inside template-string interpolations is not supported; compute it before the template",
                (filename, row, column + 1, identity.original_line(row)),
            )
    for field in _debug_fields(tokens):
        if not field.closed or field.debug is None or field.debug_end is None:
            continue
        opening = offset(field.opening.start)
        expression_start = offset(field.opening.end)
        debug_start = offset(field.debug.start)
        debug_end = offset(field.debug_end.start)
        if not any(expression_start <= start < debug_start for start, _, _, _ in keyword_edits):
            continue
        # CPython normalizes physical newlines and omits direct expression
        # comments from debug labels. Comments inside a nested formatted string
        # remain part of the enclosing expression's source spelling.
        label_parts = []
        label_cursor = expression_start
        for comment, depth in comments:
            comment_start, comment_end = offset(comment.start), offset(comment.end)
            if depth == field.formatted_depth and expression_start <= comment_start < debug_end:
                label_parts.append(source[label_cursor:comment_start])
                label_cursor = comment_end
        label_parts.append(source[label_cursor:debug_end])
        label = "".join(label_parts).replace("\r\n", "\n").replace("\r", "\n")
        if _LEGACY_DEBUG_HASHES:
            label = re.sub(r"#[^\n]*", "", label)
        replacements.append((opening, expression_start, "{" + repr(label) + "}{", "debug_label"))
        conversion = "!r" if field.debug_end.string == "}" else ""
        replacements.append((debug_start, debug_end, conversion, "debug_marker"))

    return build_translation(source, filename, replacements)


def translate(source: str, filename: str = "<urdupy>") -> str:
    """Return intermediate Python; ordinary Urdu built-in aliases stay names."""
    return translate_with_map(source, filename).text


def _validate_bindings(tree, mapping):
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.arg):
            names.append(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(node.name)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            names.append(node.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            names.extend(node.names)
        elif isinstance(node, ast.Import):
            names.extend(alias.asname or alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.extend(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name:
            names.append(node.name)
        for name in names:
            if name in PRODUCTION_KEYWORDS:
                row = node.lineno
                column = byte_to_character(mapping.translated_line(row), node.col_offset)
                error = SyntaxError(
                    f"Urdu syntax word {name!r} is reserved; use a nonreserved import alias or identifier",
                    (mapping.filename, row, column + 1, mapping.translated_line(row)),
                )
                raise mapping.map_error(error)


def _parse(source, filename, mode, flags, dont_inherit, optimize):
    mapping = translate_with_map(source, filename)
    text = mapping.text[1:] if mapping.text.startswith("\ufeff") else mapping.text
    try:
        tree = compile(text, filename, mode, flags | ast.PyCF_ONLY_AST, dont_inherit, optimize)
    except SyntaxError as error:
        raise mapping.map_error(error) from None
    _validate_bindings(tree, mapping)
    return mapping, mapping.remap_ast(tree)


def parse_urdu(source: str, filename: str = "<urdupy>", mode: str = "exec", *, flags=0, dont_inherit=True, optimize=-1) -> ast.AST:
    """Parse without execution; returned AST locations refer to original source."""
    _, tree = _parse(source, filename, mode, flags, dont_inherit, optimize)
    return tree


def compile_urdu(source: str, filename: str = "<urdupy>", mode: str = "exec", *, flags=0, dont_inherit=True, optimize=-1) -> CodeType | ast.AST:
    """Compile exec/eval/single source with original UTF-8 instruction spans.

    PyCF_ONLY_AST returns a mapped AST just as built-in compile does. No imports,
    alias namespace, linecache registration or user code execute here.
    """
    mapping, tree = _parse(source, filename, mode, flags, dont_inherit, optimize)
    if flags & ast.PyCF_ONLY_AST:
        return tree
    try:
        return compile(tree, filename, mode, flags, dont_inherit, optimize)
    except SyntaxError as error:
        # AST compiler errors (return outside function, invalid scope, etc.)
        # already carry original byte locations but no source text.
        raise mapping.original_error(error, byte_columns=True) from None
