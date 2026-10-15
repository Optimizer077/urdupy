"""Multiline Urdu console using CPython's interactive completeness rules."""

import __future__
import code
from itertools import count
import linecache
from types import ModuleType

from .compiler import compile_urdu, translate
from .runtime import _source_lines, make_builtins


_FUTURE_FLAGS = 0
for _name in __future__.all_feature_names:
    _FUTURE_FLAGS |= getattr(__future__, _name).compiler_flag
_MISSING = object()
_SESSIONS = count(1)


class UrduConsole(code.InteractiveConsole):
    def __init__(self, locals=None, *, complete=False):
        if locals is None:
            locals = ModuleType("__console__").__dict__
        locals.setdefault("__name__", "__console__")
        locals["__builtins__"] = make_builtins(locals.get("__builtins__"), complete=complete)
        super().__init__(locals)
        self._sequence = 1
        self._session = next(_SESSIONS)
        self._sources = {}
        self.complete = complete

    def runsource(self, source, filename=None, symbol="single"):
        from .urdu_surface import DIRECTIVE, enabled
        if enabled(source):
            self.complete = True
            self.locals["__builtins__"] = make_builtins(self.locals["__builtins__"], complete=True)
        elif self.complete:
            source = DIRECTIVE + "\n" + source
        if filename is None or filename == self.filename:
            filename = f"<urdupy-repl-{self._session}-{self._sequence}>"
        try:
            translated = translate(source, filename)
        except SyntaxError as error:
            message = str(error).lower()
            if any(phrase in message for phrase in (
                "eof in multi-line", "unterminated triple-quoted", "was never closed",
            )):
                return True
            self.showsyntaxerror(filename)
            return False
        try:
            tentative = self.compile(translated, filename, symbol)
            if tentative is None:
                return True
            compiled = compile_urdu(
                source, filename, symbol,
                flags=tentative.co_flags & _FUTURE_FLAGS,
            )
        except (OverflowError, SyntaxError, ValueError):
            self.showsyntaxerror(filename)
            return False
        self._sequence += 1
        if filename not in self._sources:
            self._sources[filename] = (linecache.cache.get(filename, _MISSING), None)
        entry = (len(source.encode("utf-8")), None, _source_lines(source), filename)
        previous, _ = self._sources[filename]
        self._sources[filename] = (previous, entry)
        linecache.cache[filename] = entry
        self.runcode(compiled)
        return False

    def close(self):
        for filename, (previous, entry) in self._sources.items():
            if linecache.cache.get(filename) is entry:
                if previous is _MISSING:
                    linecache.cache.pop(filename, None)
                else:
                    linecache.cache[filename] = previous
        self._sources.clear()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
