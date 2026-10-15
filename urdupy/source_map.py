"""Character-span edits and CPython UTF-8 location conversion for UrduPy."""

import ast
import bisect
import re
from dataclasses import dataclass
from functools import cached_property


def line_starts(text):
    """Physical Python lines; Unicode separators inside literals are not lines."""
    return (0, *(match.end() for match in re.finditer(r"\r\n|\r|\n", text)))


@dataclass(frozen=True)
class Edit:
    original_start: int
    original_end: int
    translated_start: int
    translated_end: int
    original: str
    replacement: str
    kind: str = "keyword"


@dataclass(frozen=True)
class Translation:
    """Source plus intermediate text; raw spans use Python string characters.

    Public line/column helpers use 1-based lines and 0-based character columns.
    An initial BOM is a transport marker and does not count as a code column.
    Locations inside changed tokens map to the whole original token, using the
    start/end bias. Generated debug-label characters map to their original field.
    """

    source: str
    text: str
    filename: str
    edits: tuple[Edit, ...]

    @cached_property
    def _original_starts(self):
        return line_starts(self.source)

    @cached_property
    def _translated_starts(self):
        return line_starts(self.text)

    def _line(self, row, *, original):
        text = self.source if original else self.text
        starts = self._original_starts if original else self._translated_starts
        if row < 1 or row > len(starts):
            return ""
        end = starts[row] if row < len(starts) else len(text)
        value = text[starts[row - 1]:end]
        return value[1:] if row == 1 and value.startswith("\ufeff") else value

    def original_line(self, row):
        return self._line(row, original=True)

    def translated_line(self, row):
        return self._line(row, original=False)

    def map_offset(self, offset, *, end=False):
        """Map a raw translated character boundary to an original boundary."""
        delta = 0
        for edit in self.edits:
            if offset < edit.translated_start:
                return max(0, min(len(self.source), offset + delta))
            if offset == edit.translated_start:
                if edit.translated_end == offset:
                    # At a deleted span, the next token begins after the
                    # deletion while the preceding token ends before it.
                    return edit.original_start if end else edit.original_end
                return edit.original_start
            if offset < edit.translated_end:
                return edit.original_end if end else edit.original_start
            delta = edit.original_end - edit.translated_end
        return max(0, min(len(self.source), offset + delta))

    def map_position(self, row, column, *, end=False):
        """Map translated (line, character column), with an optional end bias."""
        row = max(1, min(row, len(self._translated_starts)))
        bom = int(row == 1 and self.text.startswith("\ufeff"))
        offset = self._translated_starts[row - 1] + max(0, column) + bom
        mapped = self.map_offset(offset, end=end)
        original_row = bisect.bisect_right(self._original_starts, mapped)
        original_column = mapped - self._original_starts[original_row - 1]
        if original_row == 1 and self.source.startswith("\ufeff"):
            original_column = max(0, original_column - 1)
        return original_row, original_column

    def _error(self, error, *, mapped, byte_columns=False):
        row = error.lineno or 1
        column = max(0, (error.offset or 1) - 1)
        end_row = getattr(error, "end_lineno", None)
        end_column = getattr(error, "end_offset", None)
        if byte_columns:
            column = byte_to_character(self.original_line(row), column)
            if end_row and end_column and end_column > 0:
                end_column = byte_to_character(self.original_line(end_row), end_column - 1) + 1
        if mapped:
            row, column = self.map_position(row, column)
            if end_row and end_column and end_column > 0:
                end_row, end_column = self.map_position(end_row, end_column - 1, end=True)
                end_column += 1
        details = (self.filename, row, column + 1, self.original_line(row))
        if end_row is not None and end_column is not None:
            details += (end_row, end_column)
        result = type(error)(getattr(error, "msg", str(error)), details)
        return result

    def map_error(self, error):
        """Map a parsing SyntaxError's character offsets to original source."""
        return self._error(error, mapped=True)

    def original_error(self, error, *, byte_columns=False):
        """Attach original text to an error already using original AST spans."""
        return self._error(error, mapped=False, byte_columns=byte_columns)

    def remap_ast(self, tree):
        """Change AST UTF-8 byte locations in place to original-source bytes."""
        for node in ast.walk(tree):
            for row_attr, column_attr, end in (
                ("lineno", "col_offset", False),
                ("end_lineno", "end_col_offset", True),
            ):
                row = getattr(node, row_attr, None)
                column = getattr(node, column_attr, None)
                if row is None or column is None:
                    continue
                character = byte_to_character(self.translated_line(row), column)
                original_row, original_character = self.map_position(row, character, end=end)
                original_byte = len(self.original_line(original_row)[:original_character].encode("utf-8"))
                setattr(node, row_attr, original_row)
                setattr(node, column_attr, original_byte)
        return tree


def byte_to_character(line, column):
    return len(line.encode("utf-8")[:max(0, column)].decode("utf-8", errors="ignore"))


def build_translation(source, filename, replacements):
    """Build text and immutable edits from nonoverlapping original ranges."""
    pieces = []
    edits = []
    cursor = translated_cursor = 0
    for start, end, replacement, kind in sorted(replacements):
        if not 0 <= cursor <= start <= end <= len(source):
            raise ValueError("overlapping or invalid source replacements")
        gap = source[cursor:start]
        pieces.extend((gap, replacement))
        translated_start = translated_cursor + len(gap)
        translated_end = translated_start + len(replacement)
        edits.append(Edit(start, end, translated_start, translated_end, source[start:end], replacement, kind))
        cursor, translated_cursor = end, translated_end
    pieces.append(source[cursor:])
    return Translation(source, "".join(pieces), filename, tuple(edits))
