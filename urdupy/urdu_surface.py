"""Opt-in Urdu library spellings, lowered to native CPython source spans.

There are no array/tensor proxies and no mutations to dependency modules.
The directive opts into a reserved vocabulary for all identifier positions.
"""

import ast
import tokenize

from .source_map import build_translation, byte_to_character, line_starts


DIRECTIVE = "# اردوپائی: مکمل"


def enabled(source):
    """Only an actual leading comment opts in; literal contents cannot do so."""
    import io
    try:
        for item in tokenize.generate_tokens(io.StringIO(source.lstrip("\ufeff")).readline):
            if item.type == tokenize.COMMENT:
                if item.string.strip() == DIRECTIVE:
                    return True
            elif item.type not in {tokenize.NL, tokenize.NEWLINE, tokenize.ENCODING}:
                return False
    except (SyntaxError, tokenize.TokenError):
        pass
    return False


def library_edits(source, filename, tokens, keyword_edits):
    """Produce nonoverlapping edits against the original source, without imports."""
    if not enabled(source):
        return []
    from .urdu_catalog import MODULE_ALIASES, canonical_name, decode_identifier, BUILTIN_NAMES

    initial = build_translation(source, filename, keyword_edits)
    body = initial.text.lstrip("\ufeff")
    original_starts = line_starts(source)
    bom = int(source.startswith("\ufeff"))

    def original_position(row, byte):
        column = byte_to_character(initial.translated_line(row), byte)
        old_row, old_column = initial.map_position(row, column)
        return original_starts[old_row - 1] + old_column + (bom if old_row == 1 else 0)

    def token_offset(position):
        row, column = position
        return original_starts[row - 1] + column + (bom if row == 1 else 0)

    def module_path(path):
        first, *tail = path.split(".")
        root = MODULE_ALIASES.get(first) or decode_identifier(first)
        if root is None:
            return path, None
        return ".".join([root, *(canonical_name(name) for name in tail)]), root

    edits, protected = [], []
    try:
        tree = ast.parse(body)
    except SyntaxError:
        # Incomplete REPL input must still reach CPython's completeness checker.
        tree = None
    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    start = original_position(alias.lineno, alias.col_offset)
                    end = original_position(alias.end_lineno, alias.end_col_offset)
                    part = [item for item in tokens if start <= token_offset(item.start) < end]
                    path_tokens = []
                    for item in part:
                        if item.type == tokenize.NAME and item.string in {"as", "بطور"}:
                            break
                        path_tokens.append(item)
                    if not path_tokens:
                        continue
                    path_end = token_offset(path_tokens[-1].end)
                    protected.append((start, path_end))
                    replacement, root = module_path(alias.name)
                    if root is None:
                        continue
                    first, *tail = alias.name.split(".")
                    binding = canonical_name(first)
                    if alias.asname is None:
                        if tail:
                            replacement += f"; import {root} as {binding}"
                        else:
                            replacement += f" as {binding}"
                    edits.append((start, path_end, replacement, "library_import"))
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                start = original_position(node.lineno, node.col_offset)
                end = original_position(node.end_lineno, node.end_col_offset)
                part = [item for item in tokens if start <= token_offset(item.start) < end]
                path = []
                for item in part[1:]:
                    if item.type == tokenize.NAME and item.string in {"import", "درآمد"}:
                        break
                    path.append(item)
                if not path:
                    continue
                path_start, path_end = token_offset(path[0].start), token_offset(path[-1].end)
                protected.append((path_start, path_end))
                replacement, root = module_path(node.module)
                if node.level:
                    replacement = "." * node.level + ".".join(decode_identifier(part) or part for part in node.module.split('.'))
                    if replacement != "." * node.level + node.module:
                        edits.append((path_start, path_end, replacement, "library_import"))
                elif root is not None:
                    edits.append((path_start, path_end, replacement, "library_import"))

    occupied = [(start, end) for start, end, _, _ in keyword_edits]
    for item in tokens:
        if item.type != tokenize.NAME:
            continue
        start, end = token_offset(item.start), token_offset(item.end)
        if any(left <= start < right for left, right in (*protected, *occupied)):
            continue
        # Uniform lowering includes stores, parameter definitions, keyword labels,
        # protocol declarations and attributes. Thus custom Urdu calls agree with
        # their definitions, and native subclasses satisfy Python protocols.
        replacement = BUILTIN_NAMES.get(item.string, canonical_name(item.string))
        if replacement != item.string:
            edits.append((start, end, replacement, "library_identifier"))
    return edits


def original_text(value):
    """Decode an arbitrary backend string written using Urdu codepoint digits."""
    from .urdu_catalog import decode_text
    result = decode_text(value)
    if result is None:
        raise ValueError("اصل متن کی اردو ہندسوں والی املا درست نہیں")
    return result
