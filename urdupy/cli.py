"""The urdupy command line: run, translate, check, and a multiline console."""

import argparse
from contextlib import contextmanager
from pathlib import Path
import subprocess
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


class UrduArgumentParser(argparse.ArgumentParser):
    """Localize our help without modifying argparse's process-wide gettext state."""

    def __init__(self, *args, **kwargs):
        kwargs["add_help"] = False
        super().__init__(*args, **kwargs)
        self._positionals.title = "دلائل"
        self._optionals.title = "اختیارات"
        self.add_argument("--مدد", action="help", help="یہ مدد دکھائیں")

    def format_help(self):
        return super().format_help().replace("usage: ", "طریقہ: ", 1)

    def format_usage(self):
        return super().format_usage().replace("usage: ", "طریقہ: ", 1)

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: ہدایات درست نہیں۔ مدد کے لیے --مدد لکھیں۔\n")


_COMMANDS = {"چلاؤ": "run", "ترجمہ": "translate", "جانچو": "check", "بیٹھک": "repl"}


def build_parser(*, urdu=False):
    choose = lambda english, local: local if urdu else english
    if urdu:
        parser = UrduArgumentParser(prog="اردوپائی", description="اردو میں لکھیں، اصل پائتھن پر چلائیں۔")
        parser.add_argument("--نسخہ", action="version", version=f"اردوپائی {__version__}",
                            help="نصب شدہ نسخہ دکھائیں")
    else:
        parser = argparse.ArgumentParser(prog="urdupy", description="Urdu-first code, real CPython.")
        parser.add_argument("--مدد", action="help", help="Show help in this interface")
        parser.add_argument("--version", "--نسخہ", action="version", version=f"UrduPy {__version__}")
    commands = parser.add_subparsers(dest="command", required=True,
                                    title=choose("commands", "احکام"),
                                    metavar=choose(None, "حکم"))

    def command(english, local, help_english, help_urdu):
        return commands.add_parser(choose(english, local),
                                   aliases=[] if urdu else [local],
                                   help=choose(help_english, help_urdu))

    run = command("run", "چلاؤ", "Execute a UTF-8 Urdu/Python script", "اردو پروگرام چلائیں")
    run.add_argument("file", metavar=choose(None, "فائل"))
    run.add_argument("args", nargs=argparse.REMAINDER, metavar=choose(None, "دلائل"),
                     help=choose("Arguments passed to the script", "پروگرام کو دیے جانے والے دلائل"))
    translation = command("translate", "ترجمہ", "Emit intermediate Python source", "درمیانی پائتھن متن دکھائیں")
    translation.add_argument("file", metavar=choose(None, "فائل"))
    translation.add_argument(*(["--مخرج"] if urdu else ["-o", "--output", "--مخرج"]),
                             dest="output", metavar=choose(None, "فائل"),
                             help=choose("Write UTF-8 Python to this file", "ترجمہ اس فائل میں لکھیں"))
    check = command("check", "جانچو", "Compile files without executing them or their imports",
                    "فائلوں کو چلائے بغیر نحو جانچیں")
    check.add_argument("files", nargs="+", metavar=choose(None, "فائل"))
    command("repl", "بیٹھک", "Start the multiline Urdu console; exit with EOF or exit()",
            "بات چیت کی نشست شروع کریں؛ اختتام کے لیے کنٹرول اور زیڈ، پھر داخلہ دبائیں")
    names = commands.add_parser("نام", help=choose("Discover Urdu library names", "کتب خانوں کے اردو نام دیکھیں"))
    names.add_argument("namespace", nargs="?", metavar=choose(None, "نام"),
                       help=choose("Urdu module or dotted member path", "ماڈیول یا نقطوں سے جڑا اردو نام"))
    names.add_argument("--اصل", action="store_true", dest="original",
                       help=choose("Also show original backend names", "ساتھ اصل نام بھی دکھائیں"))
    names.add_argument("--کتب_خانے", action="store_true", dest="libraries",
                       help=choose("List installed importable library names without importing them",
                                   "کتب خانوں کو درآمد کیے بغیر ان کے اردو نام دیکھیں"))
    install = commands.add_parser("نصب", help=choose("Explicitly install a local dependency profile",
                                                    "اپنی درخواست پر منتخب کتب خانے نصب کریں"))
    install.add_argument("profile", nargs="?", default="بنیادی", metavar=choose(None, "مجموعہ"),
                         choices=["بنیادی", "سائنسی", "مصنوعی_ذہانت"],
                         help=choose("بنیادی / سائنسی / مصنوعی_ذہانت", "بنیادی، سائنسی، یا مصنوعی_ذہانت"))
    return parser


def _discover_names(path=None, original=False):
    """Introspect only the namespace expressly requested by the user."""
    from .urdu_catalog import (BUILTIN_NAMES, MEMBER_ALIASES, MODULE_ALIASES, PROTOCOL_ALIASES,
                               canonical_name, decode_identifier, encode_identifier, encode_text,
                               urdu_name, vocabulary)
    import keyword
    import unicodedata

    def display(name, *, parameter=False):
        # Attribute dictionaries permit arbitrary strings. Python source
        # normalizes identifiers, so a string lookup also preserves e.g. K.
        if (not name.isidentifier() or keyword.iskeyword(name)
                or unicodedata.normalize("NFKC", name) != name):
            literal = f'اصل_متن("{encode_text(name)}")'
            result = literal if parameter else f"خاصیت_لو({path}, {literal})"
            return f"{result} = {name}" if original else result
        alias, escaped = urdu_name(name), encode_identifier(name)
        if canonical_name(alias) != name:
            # A root-module alias is not necessarily valid as a member spelling:
            # random's root is اتفاق but NumPy's .random member is اتفاقی.
            alias = next((local for aliases in (MEMBER_ALIASES, PROTOCOL_ALIASES, BUILTIN_NAMES)
                          for local, backend in aliases.items() if backend == name), escaped)
        result = alias if alias == escaped else f"{alias} / {escaped}"
        return f"{result} = {name}" if original else result

    if path is None:
        titles = {"modules": "ماڈیول", "members": "ارکان", "builtins": "بنیادی نام",
                  "values": "متنی قدریں", "protocols": "خصوصی طریقے"}
        for section, entries in vocabulary().items():
            print(f"{titles[section]}:")
            for alias, backend in sorted(entries.items()):
                print(f"  {alias} = {backend}" if original else f"  {alias}")
        return 0

    import importlib
    import inspect
    parts = path.split(".")
    if not parts or any(not part.isidentifier() for part in parts):
        print("درست ماڈیول یا نقطوں سے جڑا نام لکھیں۔", file=sys.stderr)
        return 2
    first = parts[0]
    backend = MODULE_ALIASES.get(first, decode_identifier(first) or first)
    try:
        namespace = importlib.import_module(backend)
        for part in parts[1:]:
            member = canonical_name(part)
            try:
                namespace = getattr(namespace, member)
            except AttributeError:
                if not isinstance(namespace, ModuleType):
                    raise
                namespace = importlib.import_module(f"{namespace.__name__}.{member}")
    except (ImportError, AttributeError, ValueError):
        print("یہ نام یا کتاب خانہ دستیاب نہیں۔ پہلے متعلقہ کتاب خانہ نصب کریں۔", file=sys.stderr)
        return 1

    print(f"نام: {path}")
    try:
        parameters = inspect.signature(namespace).parameters
    except (TypeError, ValueError):
        parameters = {}
    if parameters:
        print("دلائل:")
        for name in parameters:
            print(f"  {display(name, parameter=True)}")
    print("ارکان (پہلا نام آسان، دوسرا نام ہمیشہ قابل استعمال ہے):")
    print("متنی نام خاصیت_لو اور اصل_متن کے ذریعے عین اپنی املا سے ملتے ہیں۔")
    for name in sorted(dir(namespace)):
        print(f"  {display(name)}")
    return 0


def _discover_libraries(original=False):
    """List built-in and discoverable top-level names without importing them."""
    from importlib.machinery import PathFinder
    import keyword
    import pkgutil
    import unicodedata
    from .urdu_catalog import MODULE_ALIASES, encode_identifier, encode_text

    names = set(sys.builtin_module_names)
    names.update(module.name for module in pkgutil.iter_modules())
    # pkgutil omits PEP 420 namespace directories. Validate filesystem candidates
    # through PathFinder; finding a spec does not execute package initializers.
    for entry in sys.path:
        if not isinstance(entry, str):
            continue
        try:
            directory = Path(entry or ".")
            if not directory.is_dir():
                continue
            for child in directory.iterdir():
                if child.is_dir() and "." not in child.name:
                    if PathFinder.find_spec(child.name, [str(directory)]) is not None:
                        names.add(child.name)
        except (OSError, ValueError):
            continue
    print("فائلوں سے معلوم کتب خانے دکھائے جاتے ہیں؛ بعض خاص درآمد کنندے اپنی فہرست نہیں دیتے۔")
    preferred = {backend: alias for alias, backend in MODULE_ALIASES.items()}
    print("دستیاب کتب خانے (یہ فہرست انہیں درآمد نہیں کرتی):")
    for name in sorted(names):
        if (name.isidentifier() and not keyword.iskeyword(name)
                and unicodedata.normalize("NFKC", name) == name):
            escaped = encode_identifier(name)
            alias = preferred.get(name, escaped)
            display = alias if alias == escaped else f"{alias} / {escaped}"
        else:
            display = f'ماڈیول_لاؤ(اصل_متن("{encode_text(name)}"))'
        print(f"  {display} = {name}" if original else f"  {display}")
    return 0


def _checkout_root():
    """An installed wheel must not guess that an unpublished registry name exists."""
    import tomllib
    for root in (Path.cwd(), Path(__file__).resolve().parents[1]):
        try:
            project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8")).get("project", {})
        except (OSError, ValueError):
            continue
        if project.get("name") == "urdupy-design-lab":
            return root
    return None


def _install_profile(profile):
    root = _checkout_root()
    if root is None:
        print("یہ نسخہ ابھی عوامی پیکیج مرکز پر شائع نہیں ہوا۔ اصل منصوبے کے فولڈر سے تنصیب کریں۔",
              file=sys.stderr)
        return 1
    extra = {"بنیادی": "", "سائنسی": "[science]", "مصنوعی_ذہانت": "[ai]"}[profile]
    print(f"منتخب مجموعہ نصب ہو رہا ہے: {profile}")
    result = subprocess.run([sys.executable, "-m", "pip", "install", f"{root}{extra}"],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode:
        print(f"تنصیب ناکام ہوئی۔ پیکیج منتظم کی اختتامی حالت: {result.returncode}", file=sys.stderr)
    else:
        print("تنصیب مکمل ہو گئی۔")
    return result.returncode


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


def _repl(*, urdu=False):
    from .importer import install_importer
    from .repl import UrduConsole
    module = ModuleType("__console__")
    missing = object()
    previous = sys.modules.get("__console__", missing)
    sys.modules["__console__"] = module
    try:
        with install_importer(), UrduConsole(module.__dict__, complete=urdu) as console:
            banner = f"اردوپائی {__version__} — اردو نشست" if urdu else f"UrduPy {__version__} — UTF-8 console"
            console.interact(banner=banner, exitmsg="")
    finally:
        if previous is missing:
            sys.modules.pop("__console__", None)
        else:
            sys.modules["__console__"] = previous
    return 0


def main(argv=None):
    return _main(argv, urdu=False)


def urdu_main(argv=None):
    """The additive اردوپائی console entry point."""
    return _main(argv, urdu=True)


def _main(argv=None, *, urdu=False):
    with _utf8_streams():
        parser = build_parser(urdu=urdu)
        options = parser.parse_args(argv)
        options.command = _COMMANDS.get(options.command, options.command)
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
                        parser.error("ترجمے کی فائل اصل فائل سے الگ ہونی چاہیے۔" if urdu else
                                     "translation output must differ from the source file")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(text, encoding="utf-8", newline="")
                else:
                    sys.stdout.write(text)
                print("درمیانی پائتھن: اردو ناموں کے لیے اردوپائی کا ماحول درکار ہے۔" if urdu else
                      "Intermediate Python: Urdu built-in aliases require the UrduPy runtime namespace.",
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
                        print(f"{'درست' if urdu else 'OK'} {path}")
                return int(failed)
            if options.command == "نام":
                if options.libraries:
                    if options.namespace:
                        parser.error("کتب خانوں کی فہرست کے ساتھ الگ نام نہیں دیا جا سکتا۔")
                    return _discover_libraries(options.original)
                return _discover_names(options.namespace, options.original)
            if options.command == "نصب":
                return _install_profile(options.profile)
            return _repl(urdu=urdu)
        except SystemExit as error:
            if error.code is None:
                return 0
            if isinstance(error.code, int):
                return error.code
            print(error.code, file=sys.stderr)
            return 1
        except KeyboardInterrupt:
            print("صارف نے عمل روک دیا۔" if urdu else "KeyboardInterrupt", file=sys.stderr)
            return 130
        except Exception as error:
            _print_error(error)
            return 1
