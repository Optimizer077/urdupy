"""Urdu-first CPython frontend. Import hooks are enabled only when requested."""

__version__ = "0.1.0a1"
LANGUAGE_SPEC_VERSION = "1.0-local"

__all__ = [
    "compile_urdu", "translate", "translate_with_map", "execute_source", "execute",
    "run_path", "install_importer", "iter_urdu_modules",
]


def __getattr__(name):
    # Keep package metadata and the historical experiment importable independently
    # of production-version support. Packaging can read __version__ without hooks.
    if name in {"compile_urdu", "translate", "translate_with_map"}:
        from . import compiler
        return getattr(compiler, name)
    if name in {"execute_source", "execute", "run_path"}:
        from . import runtime
        return getattr(runtime, name)
    if name in {"install_importer", "iter_urdu_modules"}:
        from . import importer
        return getattr(importer, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
