"""The urdupy command line: run, translate, check, and a multiline console."""

import argparse
from contextlib import contextmanager
from pathlib import Path
import sys
import traceback
from types import ModuleType

from . import __version__
from .compiler import compile_urdu, translate
from .runtime import format_exception, read_source, run_path


@contextmanager
def _utf8_streams():
    changed = []
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            encoding, errors = stream.encoding, stream.errors
            try:
                stream.reconfigure(encoding="utf-8")
            except (OSError, ValueError):
                continue
            changed.append((stream, encoding, errors))
    try:
        yield
    finally:
        for stream, encoding, errors in reversed(changed):
            try:
                stream.reconfigure(encoding=encoding, errors=errors)
            except (OSError, ValueError):
                pass


def build_parser():
    parser = argparse.ArgumentParser(prog="urdupy", description="Urdu-first code, real CPython.")
    parser.add_argument("--version", action="version", version=f"UrduPy {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Execute a UTF-8 Urdu/Python script")
    run.add_argument("file")
    run.add_argument("args", nargs=argparse.REMAINDER, help="Arguments passed to the script")
    translation = commands.add_parser("translate", help="Emit intermediate Python source")
    translation.add_argument("file")
    translation.add_argument("-o", "--output", help="Write UTF-8 Python to this file")
    check = commands.add_parser("check", help="Compile files without executing them or their imports")
    check.add_argument("files", nargs="+")
    commands.add_parser("repl", help="Start the multiline Urdu console; exit with EOF or exit()")
    return parser


def _print_error(error):
    if isinstance(error, SyntaxError):
        sys.stderr.write("".join(traceback.format_exception_only(error)))
        if "indented block" in error.msg:
            sys.stderr.write("اشارہ: بلاک کی اگلی سطر کو یکساں فاصلے سے آگے لکھیں۔\n")
        elif "expected ':'" in error.msg:
            sys.stderr.write("اشارہ: بلاک کی پہلی سطر کے آخر میں : لکھیں۔\n")
    elif isinstance(error, (OSError, UnicodeError)):
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
    else:
        sys.stderr.write(format_exception(error))


def _repl():
    from .importer import install_importer
    from .repl import UrduConsole
    module = ModuleType("__console__")
    missing = object()
    previous = sys.modules.get("__console__", missing)
    sys.modules["__console__"] = module
    try:
        with install_importer(), UrduConsole(module.__dict__) as console:
            console.interact(banner=f"UrduPy {__version__} — UTF-8 console", exitmsg="")
    finally:
        if previous is missing:
            sys.modules.pop("__console__", None)
        else:
            sys.modules["__console__"] = previous
    return 0


def main(argv=None):
    with _utf8_streams():
        parser = build_parser()
        options = parser.parse_args(argv)
        try:
            if options.command == "run":
                args = options.args[1:] if options.args[:1] == ["--"] else options.args
                run_path(options.file, args)
                return 0
            if options.command == "translate":
                source_path = Path(options.file)
                text = translate(read_source(source_path), str(source_path))
                if options.output:
                    target = Path(options.output)
                    if target.resolve() == source_path.resolve():
                        parser.error("translation output must differ from the source file")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(text, encoding="utf-8", newline="")
                else:
                    sys.stdout.write(text)
                print("Intermediate Python: Urdu built-in aliases require the UrduPy runtime namespace.",
                      file=sys.stderr)
                return 0
            if options.command == "check":
                failed = False
                for path in options.files:
                    try:
                        compile_urdu(read_source(path), str(path))
                    except (SyntaxError, OSError, UnicodeError) as error:
                        _print_error(error)
                        failed = True
                    else:
                        print(f"OK {path}")
                return int(failed)
            return _repl()
        except SystemExit as error:
            if error.code is None:
                return 0
            if isinstance(error.code, int):
                return error.code
            print(error.code, file=sys.stderr)
            return 1
        except KeyboardInterrupt:
            print("KeyboardInterrupt", file=sys.stderr)
            return 130
        except Exception as error:
            _print_error(error)
            return 1
