"""Opt-in Urdu modules/packages, preserving standard concrete Python priority."""

import importlib.abc
import importlib.machinery
import importlib.util
from pathlib import Path
import pkgutil
import sys
from threading import RLock


class UrduLoader(importlib.abc.SourceLoader):
    def __init__(self, fullname, path, is_package=False):
        self.fullname = fullname
        self.path = str(path)
        self._is_package = is_package

    def get_filename(self, fullname):
        return self.path

    def get_data(self, path):
        return Path(path).read_bytes()

    def get_source(self, fullname):
        return self.get_data(self.path).decode("utf-8-sig")

    def is_package(self, fullname):
        return self._is_package

    def get_code(self, fullname):
        from .compiler import compile_urdu
        return compile_urdu(self.get_source(fullname), self.path)

    def exec_module(self, module):
        from .compiler import compile_urdu
        from .runtime import prepare_namespace, source_context
        from .urdu_surface import enabled
        source = self.get_source(module.__name__)
        code = compile_urdu(source, self.path)
        prepare_namespace(module.__dict__, self.path, complete=enabled(source))
        with source_context(source, self.path):
            exec(code, module.__dict__)

    def get_resource_reader(self, fullname):
        if self._is_package:
            from importlib.resources.readers import FileReader
            return FileReader(self)
        return None


class UrduFinder(importlib.abc.MetaPathFinder):
    """Delegate to standard concrete specs, then consider filesystem Urdu files."""

    def find_spec(self, fullname, path=None, target=None):
        standard = importlib.machinery.PathFinder.find_spec(fullname, path)
        if standard is not None and standard.loader is not None:
            return None
        leaf = fullname.rpartition(".")[2]
        for entry in sys.path if path is None else path:
            if not isinstance(entry, (str, bytes)):
                continue
            try:
                directory = Path(entry or ".")
                package = directory / leaf / "__init__.urdu"
                if package.is_file():
                    loader = UrduLoader(fullname, package, is_package=True)
                    return importlib.util.spec_from_file_location(
                        fullname, package, loader=loader,
                        submodule_search_locations=[str(package.parent)],
                    )
                # A standard namespace package wins over a loose Urdu module;
                # an Urdu regular initializer above can resolve its own package.
                module = directory / f"{leaf}.urdu"
                if standard is None and module.is_file():
                    loader = UrduLoader(fullname, module)
                    return importlib.util.spec_from_file_location(fullname, module, loader=loader)
            except (OSError, TypeError, ValueError):
                continue
        return None

    def invalidate_caches(self):
        # No discovery or bytecode cache is maintained by this finder.
        return None


_FINDER = UrduFinder()
_LOCK = RLock()
_USERS = 0


class ImporterHandle:
    """An idempotent owned lease; nested users share one finder."""

    def __init__(self):
        self.closed = False

    def close(self):
        global _USERS
        with _LOCK:
            if self.closed:
                return
            self.closed = True
            _USERS -= 1
            if _USERS == 0:
                sys.meta_path[:] = [finder for finder in sys.meta_path if finder is not _FINDER]

    uninstall = close

    def __enter__(self):
        if self.closed:
            raise RuntimeError("Importer handle is already closed")
        return self

    def __exit__(self, *exc):
        self.close()


def install_importer():
    """Enable Urdu imports until this returned handle closes; never called on import."""
    global _USERS
    with _LOCK:
        if _FINDER not in sys.meta_path:
            try:
                index = sys.meta_path.index(importlib.machinery.PathFinder)
            except ValueError as error:
                raise RuntimeError("UrduPy requires the standard PathFinder to remain installed") from error
            sys.meta_path.insert(index, _FINDER)
        _USERS += 1
    return ImporterHandle()


def iter_urdu_modules(path):
    """Explicit Urdu discovery; standard pkgutil discovery is not monkey-patched."""
    directory = Path(path)
    for child in sorted(directory.iterdir()):
        if child.is_file() and child.suffix == ".urdu" and child.stem != "__init__":
            if child.stem.isidentifier():
                yield pkgutil.ModuleInfo(_FINDER, child.stem, False)
        elif child.is_dir() and child.name.isidentifier() and (child / "__init__.urdu").is_file():
            yield pkgutil.ModuleInfo(_FINDER, child.name, True)
