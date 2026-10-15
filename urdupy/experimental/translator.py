"""Bounded M0 translation evidence; see docs/adr/005-translator.md.

This deliberately uses the host tokenizer on extension syntax, outside its
documented valid-Python input guarantee. Passing fixtures are empirical evidence,
not a production parser or cross-version compatibility guarantee.
"""

import ast
import io
import keyword
import token
import tokenize
from dataclasses import dataclass
from types import CodeType

from urdupy.lexicon import KEYWORDS


class ExperimentalSyntaxError(SyntaxError):
    """A deliberately unsupported or ambiguous Phase 1 source form."""


@dataclass(frozen=True)
class Edit:
    """One replacement, in Python string character offsets, not byte offsets."""

    original_start: int
    original_end: int
    translated_start: int
    translated_end: int
    original: str
    replacement: str
    line: int
    column: int


@dataclass(frozen=True)
class Translation:
    text: str
    edits: tuple[Edit, ...]


_IGNORED = {
    tokenize.COMMENT,
    tokenize.NL,
    tokenize.INDENT,
    tokenize.DEDENT,
    tokenize.ENCODING,
    tokenize.ENDMARKER,
}


def _syntax_error(message, filename, position, lines):
    row, column = position
    line = lines[row - 1] if 0 < row <= len(lines) else ""
    return ExperimentalSyntaxError(message, (filename, row, column + 1, line))


def _line_starts(source):
    # splitlines() also splits Unicode separators inside strings; tokenize does
    # not. Count LF only so CRLF and literal Unicode separators retain offsets.
    return [0] + [index + 1 for index, char in enumerate(source) if char == "\n"]


def _offset(position, starts):
    row, column = position
    return starts[row - 1] + column


def _is_fstring(text):
    prefix = text[:min(index for index, char in enumerate(text) if char in "\"'")]
    return "f" in prefix.lower()


def _check_fstring(item, filename, lines):
    """Use CPython to distinguish expression names from attrs/labels/literals."""
    message = "Phase 1 f-string expressions are Python-only; move Urdu syntax outside the f-string"
    try:
        tree = ast.parse(item.string, filename=filename, mode="eval")
    except SyntaxError as error:
        raise _syntax_error(message, filename, item.start, lines) from error
    for node in ast.walk(tree):
        if (isinstance(node, ast.Name) and node.id in KEYWORDS) or (
            isinstance(node, ast.arg) and node.arg in KEYWORDS
        ):
            raise _syntax_error(message, filename, item.start, lines)


def _opaque_tokens(source, filename, starts):
    """Collapse 3.12+ f-string groups to the same opaque unit as 3.11 STRING."""
    lines = source.split("\n")
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError) as error:
        position = getattr(error, "lineno", None)
        if position is not None:
            row, col = position, max(0, (getattr(error, "offset", None) or 1) - 1)
        elif len(error.args) > 1 and isinstance(error.args[1], tuple):
            row, col = error.args[1][:2]
        else:
            row, col = 1, 0
        raise _syntax_error(str(error.args[0]), filename, (row, col), lines) from error

    f_start = getattr(token, "FSTRING_START", None)
    f_end = getattr(token, "FSTRING_END", None)
    result = []
    index = 0
    while index < len(tokens):
        item = tokens[index]
        if f_start is not None and item.type == f_start:
            depth = 1
            end_index = index + 1
            while end_index < len(tokens) and depth:
                depth += tokens[end_index].type == f_start
                depth -= tokens[end_index].type == f_end
                end_index += 1
            if depth:
                raise _syntax_error("Unterminated f-string", filename, item.start, lines)
            end = tokens[end_index - 1].end
            text = source[_offset(item.start, starts):_offset(end, starts)]
            item = tokenize.TokenInfo(tokenize.STRING, text, item.start, end, item.line)
            _check_fstring(item, filename, lines)
            result.append(item)
            index = end_index
            continue
        if item.type == tokenize.STRING and _is_fstring(item.string):
            _check_fstring(item, filename, lines)
        result.append(item)
        index += 1
    return result


def _from_delimiter(tokens, start):
    """Let CPython disambiguate module/export names that spell Urdu 'import'.

    For example, both relative-only '. درآمد x' and '.درآمد درآمد x'
    need an import delimiter, but in different positions. Isolated parse trials
    avoid assuming whitespace separates module names from syntax. They execute
    neither the import nor the original program.
    """
    end = start
    while end < len(tokens) and tokens[end].type != tokenize.NEWLINE and tokens[end].string != ";":
        end += 1
    for candidate in range(start, end):
        item = tokens[candidate]
        if item.type != tokenize.NAME or KEYWORDS.get(item.string, item.string) != "import":
            continue
        path = "".join(part.string for part in tokens[start:candidate])
        suffix = []
        expect = "symbol"
        for part in tokens[candidate + 1:end]:
            text = part.string
            if part.type == tokenize.NAME:
                if expect == "symbol":
                    expect = "after_symbol"
                elif expect == "alias":
                    expect = "after_alias"
                elif expect == "after_symbol" and KEYWORDS.get(text, text) == "as":
                    text = "as"
                    expect = "alias"
            elif text == ",":
                expect = "symbol"
            suffix.append(text)
        try:
            parsed = ast.parse("from " + path + " import " + " ".join(suffix))
        except SyntaxError:
            continue
        if len(parsed.body) == 1 and isinstance(parsed.body[0], ast.ImportFrom):
            return candidate
    return None


def translate_with_spans(source: str, filename: str = "<urdupy>") -> Translation:
    """Return intermediate Python and replaced-token spans without execution.

    All active Urdu words are reserved unqualified, with exceptions for imported
    API names and call keyword labels. Attributes and f-string source are opaque.
    compile_urdu adds CPython parsing and reserved-binding validation. See ADR-005
    for the precise limits; this is not a complete context-sensitive parser.
    """
    if not isinstance(source, str):
        raise TypeError("source must be a str")
    bom = 1 if source.startswith("\ufeff") else 0
    body = source[bom:]
    starts = _line_starts(body)
    tokens = _opaque_tokens(body, filename, starts)
    significant = [item for item in tokens if item.type not in _IGNORED]
    replacements = []
    brackets = []
    previous = None
    previous_type = None
    previous_python = None
    statement_start = True
    import_mode = None
    import_expect = "symbol"
    from_delimiter = None
    definition_header = False

    for index, item in enumerate(significant):
        text = item.string
        mapped = KEYWORDS.get(text, text) if item.type == tokenize.NAME else text
        next_text = significant[index + 1].string if index + 1 < len(significant) else None
        replacement = text

        if item.type == tokenize.NEWLINE or text == ";":
            statement_start = True
            import_mode = None
            definition_header = False
        elif import_mode is not None:
            if import_mode == "from_path":
                if index == from_delimiter:
                    replacement = mapped
                    import_mode = "names"
                    import_expect = "symbol"
            elif item.type == tokenize.NAME:
                if import_expect == "symbol" or previous == ".":
                    import_expect = "after_symbol"
                elif import_expect == "alias":
                    import_expect = "after_alias"
                elif import_expect == "after_symbol" and mapped == "as":
                    replacement = mapped
                    import_expect = "alias"
            elif text == ",":
                import_expect = "symbol"
        elif item.type == tokenize.NAME:
            attribute = previous == "."
            call_label = next_text == "=" and brackets and brackets[-1] == "call"
            if not attribute and not call_label:
                replacement = mapped
                if statement_start and mapped in {"import", "from"}:
                    import_mode = "from_path" if mapped == "from" else "names"
                    import_expect = "symbol"
                    if mapped == "from":
                        from_delimiter = _from_delimiter(significant, index + 1)
                if mapped == "def":
                    definition_header = True
            statement_start = False
        elif text == ":" and not brackets:
            statement_start = True
            definition_header = False
        elif item.type != tokenize.ENDMARKER:
            statement_start = False

        if text in {"(", "[", "{"}:
            callable_before = previous in {")", "]"} or previous_type in {tokenize.NUMBER, tokenize.STRING} or (
                previous_python is not None
                and previous_python.isidentifier()
                and not keyword.iskeyword(previous_python)
            )
            if text == "(" and definition_header:
                brackets.append("parameters")
                definition_header = False
            else:
                brackets.append("call" if text == "(" and callable_before else "group")
        elif text in {")", "]", "}"} and brackets:
            brackets.pop()

        if replacement != text:
            start = bom + _offset(item.start, starts)
            end = bom + _offset(item.end, starts)
            replacements.append((start, end, replacement, item.start))
        previous = text
        previous_type = item.type
        previous_python = replacement

    pieces = []
    edits = []
    cursor = 0
    translated_cursor = 0
    for start, end, replacement, position in replacements:
        gap = source[cursor:start]
        pieces.extend((gap, replacement))
        translated_start = translated_cursor + len(gap)
        translated_end = translated_start + len(replacement)
        row, column = position
        if row == 1:
            column += bom
        edits.append(Edit(start, end, translated_start, translated_end, source[start:end], replacement, row, column))
        cursor, translated_cursor = end, translated_end
    pieces.append(source[cursor:])
    return Translation("".join(pieces), tuple(edits))


def translate(source: str, filename: str = "<urdupy>") -> str:
    """Return intermediate Python text; aliases still require a built-ins policy."""
    return translate_with_spans(source, filename).text


def _check_reserved_bindings(tree, filename, text):
    lines = text.split("\n")
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
        for name in names:
            if name in KEYWORDS:
                raise _syntax_error(
                    f"Urdu syntax word {name!r} is reserved; use a nonreserved import alias or identifier",
                    filename,
                    (
                        node.lineno,
                        len(lines[node.lineno - 1].encode("utf-8")[:node.col_offset].decode("utf-8")),
                    ),
                    lines,
                )


def compile_urdu(source: str, filename: str = "<urdupy>") -> CodeType:
    """Translate and compile without running source, imports, or alias setup.

    Filename and line counts survive. CPython's column offsets refer to the
    translated source; no production diagnostic or traceback source map exists.
    """
    translated = translate(source, filename)
    if translated.startswith("\ufeff"):
        translated = translated[1:]
    tree = ast.parse(translated, filename=filename, mode="exec")
    _check_reserved_bindings(tree, filename, translated)
    return compile(tree, filename, "exec")
