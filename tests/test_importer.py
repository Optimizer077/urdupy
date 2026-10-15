import importlib
import importlib.abc
import importlib.machinery
import importlib.resources
import importlib.util
import linecache
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType
import unittest
from unittest.mock import Mock
from uuid import uuid4
from zipfile import ZipFile

from urdupy.importer import UrduFinder, UrduLoader, install_importer, iter_urdu_modules


class ImporterTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.prefix = "urdu_test_" + uuid4().hex
        self.original_path = sys.path
        sys.path = [str(self.root), *sys.path]

    def tearDown(self):
        sys.path = self.original_path
        for name in list(sys.modules):
            if name.startswith(self.prefix):
                del sys.modules[name]
        for path in list(sys.path_importer_cache):
            if isinstance(path, str) and path.startswith(str(self.root)):
                del sys.path_importer_cache[path]
        self.temp.cleanup()

    def write(self, relative, source):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
        return path

    def test_no_automatic_hook_and_hook_close_identity(self):
        before = list(sys.meta_path)
        self.assertFalse(any(isinstance(finder, UrduFinder) for finder in before))
        first, second = install_importer(), install_importer()
        try:
            self.assertEqual(sum(isinstance(finder, UrduFinder) for finder in sys.meta_path), 1)
            first.close()
            first.close()
            self.assertEqual(sum(isinstance(finder, UrduFinder) for finder in sys.meta_path), 1)
        finally:
            second.close()
        self.assertEqual(sys.meta_path, before)
        with self.assertRaises(RuntimeError):
            first.__enter__()

    def test_module_metadata_aliases_and_repeated_import(self):
        name = self.prefix
        path = self.write(name + ".urdu", "فنکشن double(x):\n    واپس x * 2\nRESULT = حد\n")
        with install_importer():
            module = importlib.import_module(name)
            self.assertIs(importlib.import_module(name), module)
        self.assertEqual(module.double(4), 8)
        self.assertIs(module.RESULT, range)
        self.assertEqual(module.__name__, name)
        self.assertEqual(module.__package__, "")
        self.assertEqual(module.__file__, str(path))
        self.assertEqual(module.__spec__.origin, str(path))
        self.assertNotIn("دکھاؤ", vars(module))

    def test_python_requires_opt_in_and_imports_remain_cached_after_close(self):
        self.write(self.prefix + ".urdu", "value = 7\n")
        with self.assertRaises(ModuleNotFoundError):
            importlib.import_module(self.prefix)
        with install_importer():
            module = importlib.import_module(self.prefix)
        self.assertIs(importlib.import_module(self.prefix), module)

    def test_same_directory_python_module_wins(self):
        self.write(self.prefix + ".urdu", "value = 'Urdu'\n")
        self.write(self.prefix + ".py", "value = 'Python'\n")
        with install_importer():
            self.assertEqual(importlib.import_module(self.prefix).value, "Python")

    def test_later_python_path_wins_over_earlier_urdu(self):
        self.write(self.prefix + ".urdu", "value = 'Urdu'\n")
        second = self.root / "later"
        second.mkdir()
        (second / (self.prefix + ".py")).write_text("value = 'Python'\n", encoding="utf-8")
        sys.path.insert(1, str(second))
        with install_importer():
            self.assertEqual(importlib.import_module(self.prefix).value, "Python")

    def test_later_zip_module_wins_over_earlier_urdu(self):
        self.write(self.prefix + ".urdu", "value = 'Urdu'\n")
        archive = self.root / "standard.zip"
        with ZipFile(archive, "w") as bundle:
            bundle.writestr(self.prefix + ".py", "value = 'zip'\n")
        sys.path.insert(1, str(archive))
        with install_importer():
            self.assertEqual(importlib.import_module(self.prefix).value, "zip")

    def test_standard_native_spec_is_never_displaced(self):
        self.write("_ctypes.urdu", "raise RuntimeError('not native')\n")
        standard = importlib.machinery.PathFinder.find_spec("_ctypes")
        self.assertIsInstance(standard.loader, importlib.machinery.ExtensionFileLoader)
        self.assertIsNone(UrduFinder().find_spec("_ctypes"))

    def test_existing_custom_finder_keeps_its_priority(self):
        self.write(self.prefix + ".urdu", "value = 'Urdu'\n")
        target = self.prefix

        class Loader(importlib.abc.Loader):
            def create_module(self, spec):
                return None

            def exec_module(self, module):
                module.value = "custom"

        class Finder(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if fullname == self.name:
                    return importlib.util.spec_from_loader(fullname, Loader())
                return None

        finder = Finder()
        finder.name = target
        sys.meta_path.insert(0, finder)
        try:
            with install_importer():
                self.assertEqual(importlib.import_module(target).value, "custom")
        finally:
            sys.meta_path.remove(finder)

    def test_regular_urdu_package_relative_children_and_resources(self):
        self.write(self.prefix + "/__init__.urdu", "سے .child درآمد value\n")
        self.write(self.prefix + "/child.urdu", "value = 42\n")
        self.write(self.prefix + "/data.txt", "وسیلہ")
        with install_importer():
            package = importlib.import_module(self.prefix)
            child = importlib.import_module(self.prefix + ".child")
            resource = importlib.resources.files(package).joinpath("data.txt").read_text(encoding="utf-8")
        self.assertEqual((package.value, child.value, resource), (42, 42, "وسیلہ"))
        self.assertEqual(package.__package__, self.prefix)
        self.assertEqual(list(package.__path__), [str(self.root / self.prefix)])
        self.assertIs(package.child, child)

    def test_standard_python_package_initializer_wins(self):
        self.write(self.prefix + "/__init__.urdu", "value = 'Urdu'\n")
        self.write(self.prefix + "/__init__.py", "value = 'Python'\n")
        with install_importer():
            self.assertEqual(importlib.import_module(self.prefix).value, "Python")

    def test_python_package_can_import_urdu_child(self):
        self.write(self.prefix + "/__init__.py", "from .child import value\n")
        self.write(self.prefix + "/child.urdu", "value = 17\n")
        with install_importer():
            self.assertEqual(importlib.import_module(self.prefix).value, 17)

    def test_namespace_parent_and_nested_regular_urdu_package(self):
        self.write(self.prefix + "/nested/__init__.urdu", "سے .child درآمد value\n")
        self.write(self.prefix + "/nested/child.urdu", "value = 11\n")
        with install_importer():
            parent = importlib.import_module(self.prefix)
            nested = importlib.import_module(self.prefix + ".nested")
        self.assertIsNone(parent.__spec__.origin)
        self.assertEqual(nested.value, 11)

    def test_namespace_parent_wins_over_loose_urdu_module(self):
        (self.root / self.prefix).mkdir()
        self.write(self.prefix + ".urdu", "raise RuntimeError('must not execute')\n")
        with install_importer():
            module = importlib.import_module(self.prefix)
        self.assertIsNone(module.__spec__.origin)

    def test_circular_import_partial_initialization(self):
        first, second = self.prefix + "_a", self.prefix + "_b"
        self.write(first + ".urdu", f"value = 3\nدرآمد {second} بطور peer\nRESULT = peer.seen\n")
        self.write(second + ".urdu", f"درآمد {first} بطور peer\nseen = peer.value\n")
        with install_importer():
            self.assertEqual(importlib.import_module(first).RESULT, 3)

    def test_initial_import_failure_cleanup_and_successful_side_effect(self):
        side = self.prefix + "_side"
        self.write(side + ".urdu", "value = 1\n")
        path = self.write(self.prefix + ".urdu", f"درآمد {side}\nاٹھاؤ ValueError('failure')\n")
        previous = linecache.cache.get(str(path))
        with install_importer():
            with self.assertRaises(ValueError):
                importlib.import_module(self.prefix)
        self.assertNotIn(self.prefix, sys.modules)
        self.assertIn(side, sys.modules)
        self.assertIs(linecache.cache.get(str(path)), previous)

    def test_reload_reads_changed_source_and_new_file_discovery(self):
        path = self.write(self.prefix + ".urdu", "value = 1\n")
        with install_importer():
            module = importlib.import_module(self.prefix)
            path.write_text("value = 29\n", encoding="utf-8")
            self.assertIs(importlib.reload(module), module)
            self.assertEqual(module.value, 29)
            extra = self.prefix + "_new"
            self.write(extra + ".urdu", "value = 8\n")
            importlib.invalidate_caches()
            self.assertEqual(importlib.import_module(extra).value, 8)
        self.assertFalse(list(self.root.rglob("*.pyc")))

    def test_unicode_module_filename_and_explicit_discovery(self):
        name = self.prefix + "_حساب"
        self.write(name + ".urdu", "value = 9\n")
        self.write(self.prefix + "_pkg/__init__.urdu", "گزر\n")
        with install_importer():
            self.assertEqual(importlib.import_module(name).value, 9)
        discovered = {item.name: item.ispkg for item in iter_urdu_modules(self.root)}
        self.assertEqual(discovered, {name: False, self.prefix + "_pkg": True})

    def test_loader_compiles_and_displays_one_source_snapshot(self):
        path = self.root / (self.prefix + ".urdu")
        first = "value = 1\nimport linecache\nCACHED = linecache.getline(__file__, 1)\n"
        loader = UrduLoader(self.prefix, path)
        loader.get_source = Mock(side_effect=[first, "value = 2\n"])
        module = ModuleType(self.prefix)
        loader.exec_module(module)
        self.assertEqual(module.value, 1)
        self.assertEqual(module.CACHED, "value = 1\n")
        self.assertEqual(loader.get_source.call_count, 1)


if __name__ == "__main__":
    unittest.main()
