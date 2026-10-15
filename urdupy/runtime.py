"""CPython execution with owned namespaces and reversible interpreter state."""

from contextlib import contextmanager, nullcontext
import builtins
import io
from itertools import count
import linecache
from pathlib import Path
import sys
from threading import RLock
import traceback
from types import ModuleType

from .compiler import compile_urdu
from .lexicon import BUILTIN_ALIASES


_MISSING = object()
_EXECUTIONS = count(1)
_EXECUTION_LOCK = RLock()


def _source_lines(source):
    # Universal ASCII newlines, without splitting Unicode separators in literals.
    return io.StringIO(source, newline=None).readlines()


def read_source(path):
    """Decode UTF-8 without newline rewriting; the compiler accepts a UTF-8 BOM."""
    return Path(path).read_bytes().decode("utf-8")


def make_builtins(base=None):
    """Return an independent dictionary whose aliases are actual built-in objects."""
    if base is None:
        base = vars(builtins)
    elif isinstance(base, ModuleType):
        base = vars(base)
    if not isinstance(base, dict):
        raise TypeError("__builtins__ must be a dictionary or module")
    result = base.copy()
    for alias, name in BUILTIN_ALIASES.items():
        if name in result:
            result.setdefault(alias, result[name])
    return result


def prepare_namespace(namespace, filename):
    namespace["__builtins__"] = make_builtins(namespace.get("__builtins__"))
    namespace.setdefault("__file__", str(filename))
    namespace.setdefault("__package__", None)
    return namespace


@contextmanager
def source_context(source, filename):
    """Make original text available to traceback formatting, then restore ownership."""
    filename = str(filename)
    cache = linecache.cache
    previous = cache.get(filename, _MISSING)
    lines = _source_lines(source)
    entry = (len(source.encode("utf-8")), None, lines, filename)
    cache[filename] = entry
    try:
        yield
    finally:
        # Do not erase a new entry installed by user code or another owner.
        if cache.get(filename) is entry:
            if previous is _MISSING:
                cache.pop(filename, None)
            else:
                cache[filename] = previous


def format_exception(error):
    """Use a captured original-source traceback for anonymous source if available."""
    captured = getattr(error, "__urdupy_traceback__", None)
    return captured if isinstance(captured, str) else "".join(traceback.format_exception(error))


def execute_source(source, filename="<urdupy>", globals=None, *, install_importer=True):
    """Execute in CPython and return the module dictionary.

    Caller-supplied globals use ordinary exec semantics. An omitted dictionary
    receives a temporary real module during execution, supporting decorators that
    inspect sys.modules. Use an imported module for persistent pickle identities.
    This executes unrestricted Python; it is not a sandbox.
    """
    filename = str(filename)
    execution_id = next(_EXECUTIONS)
    if filename == "<urdupy>":
        filename = f"<urdupy-{execution_id}>"
    code = compile_urdu(source, filename)
    if globals is not None and not isinstance(globals, dict):
        raise TypeError("globals must be a dictionary")
    module = None
    if globals is None:
        module = ModuleType(f"_urdupy_exec_{execution_id}")
        namespace = module.__dict__
    else:
        namespace = globals
        namespace.setdefault("__name__", "__urdupy__")
    prepare_namespace(namespace, filename)
    from .importer import install_importer as enable_importer

    hook = enable_importer() if install_importer else nullcontext()
    with hook, source_context(source, filename):
        previous_module = _MISSING
        if module is not None:
            previous_module = sys.modules.get(module.__name__, _MISSING)
            sys.modules[module.__name__] = module
        try:
            exec(code, namespace)
        except Exception as error:
            # Capture while the original virtual text is available. Keep the
            # original exception object/type and do not suppress interrupts/exits.
            try:
                error.__urdupy_traceback__ = "".join(traceback.format_exception(error))
            except (AttributeError, TypeError):
                pass
            raise
        finally:
            if module is not None and sys.modules.get(module.__name__) is module:
                if previous_module is _MISSING:
                    del sys.modules[module.__name__]
                else:
                    sys.modules[module.__name__] = previous_module
    return namespace


execute = execute_source


def run_path(path, args=None):
    """Run a UTF-8 script as __main__, restoring argv/path/main after every exit."""
    path = Path(path).resolve()
    source = read_source(path)
    module = ModuleType("__main__")
    namespace = module.__dict__
    namespace.update(__file__=str(path), __package__=None, __spec__=None,
                     __cached__=None, __loader__=None)
    with _EXECUTION_LOCK:
        old_argv, old_path = sys.argv, sys.path
        old_main = sys.modules.get("__main__", _MISSING)
        sys.argv = [str(path), *(str(arg) for arg in (args or []))]
        sys.path = [str(path.parent), *old_path]
        sys.modules["__main__"] = module
        try:
            return execute_source(source, str(path), namespace)
        finally:
            sys.argv, sys.path = old_argv, old_path
            if old_main is _MISSING:
                sys.modules.pop("__main__", None)
            else:
                sys.modules["__main__"] = old_main
