"""Behavior of the additive Urdu command surface; no optional libraries needed."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from urdupy.cli import main, urdu_main


class UrduCliTests(unittest.TestCase):
    def invoke(self, *args):
        output, errors = StringIO(), StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            try:
                status = urdu_main(list(map(str, args)))
            except SystemExit as error:
                status = error.code
        return status, output.getvalue(), errors.getvalue()

    def assert_urdu(self, text):
        self.assertIsNone(re.search(r"[A-Za-z]", text), text)

    def test_help_and_subcommand_help_are_urdu(self):
        for args in [("--مدد",), *((command, "--مدد") for command in
                                   ("چلاؤ", "جانچو", "ترجمہ", "بیٹھک", "نام", "نصب"))]:
            with self.subTest(args=args):
                status, output, errors = self.invoke(*args)
                self.assertEqual(status, 0, errors)
                self.assertIn("طریقہ:", output)
                self.assertIn("--مدد", output)
                self.assert_urdu(output)

    def test_version_has_urdu_product_name(self):
        status, output, errors = self.invoke("--نسخہ")
        self.assertEqual(status, 0, errors)
        self.assertIn("اردوپائی", output)
        self.assertIn("0.1.0a1", output)

    def test_invalid_command_and_missing_argument_are_localized(self):
        for args in [(), ("غلط",), ("چلاؤ",), ("نصب", "غلط")]:
            with self.subTest(args=args):
                status, output, errors = self.invoke(*args)
                self.assertEqual(status, 2)
                self.assertIn("ہدایات درست نہیں", errors)
                self.assert_urdu(errors)

    def test_run_passes_urdu_file_and_script_arguments(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "سلام.urdu"
            source.write_text("درآمد sys\nدکھاؤ('سلام', sys.argv[1:])\n", encoding="utf-8")
            status, output, errors = self.invoke("چلاؤ", source, "--", "ایک", "--دو")
            self.assertEqual(status, 0, errors)
            self.assertEqual(output, "سلام ['ایک', '--دو']\n")

    def test_check_is_localized_and_does_not_import_or_execute(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "جانچ.urdu"
            source.write_text("درآمد _missing_urdu_cli_library\nاٹھاؤ RuntimeError\n", encoding="utf-8")
            with patch("urdupy.cli.subprocess.run") as install:
                status, output, errors = self.invoke("جانچو", source)
            self.assertEqual(status, 0, errors)
            self.assertIn(f"درست {source}", output)
            install.assert_not_called()

    def test_translation_output_option_and_warning(self):
        with TemporaryDirectory() as directory:
            source, target = Path(directory) / "ماخذ.urdu", Path(directory) / "مخرج.py"
            source.write_text("اگر سچ:\n    دکھاؤ('سلام')\n", encoding="utf-8")
            status, output, errors = self.invoke("ترجمہ", source, "--مخرج", target)
            self.assertEqual(status, 0, errors)
            self.assertEqual(target.read_text(encoding="utf-8"), "if True:\n    دکھاؤ('سلام')\n")
            self.assertIn("درمیانی پائتھن", errors)
            self.assert_urdu(errors)
            self.assertEqual(self.invoke("ترجمہ", source, "--مخرج", source)[0], 2)

    def test_existing_english_entry_accepts_additive_aliases(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "سلام.urdu"
            source.write_text("گزر\n", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["جانچو", str(source)]), 0)
            self.assertIn("OK ", output.getvalue())

    def test_catalog_listing_does_not_import_optional_libraries(self):
        with patch("importlib.import_module") as imports:
            status, output, errors = self.invoke("نام")
        self.assertEqual(status, 0, errors)
        imports.assert_not_called()
        self.assertIn("نمپی", output)
        self.assertIn("ٹارچ", output)
        self.assert_urdu(output)

    def test_namespace_discovery_and_unknown_identifiers_round_trip(self):
        from urdupy.urdu_catalog import decode_identifier, encode_identifier
        module = ModuleType("_urdu_cli_fixture")
        module.future_uncommon_operation = lambda future_argument: future_argument
        path = encode_identifier(module.__name__)
        escaped = encode_identifier("future_uncommon_operation")
        with patch("importlib.import_module", return_value=module) as imports:
            status, output, errors = self.invoke("نام", path)
        self.assertEqual(status, 0, errors)
        imports.assert_called_once_with(module.__name__)
        self.assertIn(escaped, output)
        self.assertEqual(decode_identifier(escaped), "future_uncommon_operation")
        self.assert_urdu(output)

        with patch("importlib.import_module", return_value=module):
            status, output, errors = self.invoke("نام", f"{path}.{escaped}")
        self.assertEqual(status, 0, errors)
        self.assertIn("دلائل:", output)
        self.assertIn(encode_identifier("future_argument"), output)
        self.assert_urdu(output)

    def test_original_names_are_only_shown_when_requested(self):
        from urdupy.urdu_catalog import encode_identifier
        module = ModuleType("_urdu_cli_fixture")
        module.future_uncommon_operation = 7
        with patch("importlib.import_module", return_value=module):
            status, output, errors = self.invoke("نام", encode_identifier(module.__name__), "--اصل")
        self.assertEqual(status, 0, errors)
        self.assertIn(" = future_uncommon_operation", output)

    def test_member_alias_does_not_confuse_module_vocabulary(self):
        from urdupy.urdu_catalog import MEMBER_ALIASES, encode_identifier
        module = ModuleType("_urdu_cli_fixture")
        module.random = 7
        alias = next(alias for alias, name in MEMBER_ALIASES.items() if name == "random")
        with patch("importlib.import_module", return_value=module):
            status, output, errors = self.invoke("نام", encode_identifier(module.__name__))
        self.assertEqual(status, 0, errors)
        self.assertIn(f"  {alias} / {encode_identifier('random')}\n", output)

    def test_every_attribute_name_has_lossless_urdu_lookup(self):
        from urdupy.runtime import execute_source
        from urdupy.urdu_catalog import encode_identifier, encode_text
        module = ModuleType("_urdu_cli_fixture")
        names = ["class", "foo-bar", "a space", "😀", "K"]
        for index, name in enumerate(names):
            setattr(module, name, index)
        path = encode_identifier(module.__name__)
        with patch("importlib.import_module", return_value=module):
            status, output, errors = self.invoke("نام", path)
        self.assertEqual(status, 0, errors)
        self.assert_urdu(output)
        for index, name in enumerate(names):
            with self.subTest(name=name):
                expression = f'خاصیت_لو({path}, اصل_متن("{encode_text(name)}"))'
                self.assertIn(expression, output)
                result = execute_source(f"# اردوپائی: مکمل\nجواب = {expression}\n",
                                        globals={module.__name__: module})
                self.assertEqual(result["جواب"], index)

    def test_known_module_path_and_missing_library(self):
        status, output, errors = self.invoke("نام", "ریاضی")
        self.assertEqual(status, 0, errors)
        self.assertIn("ارکان", output)
        self.assert_urdu(output)
        with patch("importlib.import_module", side_effect=ModuleNotFoundError):
            status, output, errors = self.invoke("نام", "نمپی")
        self.assertEqual(status, 1)
        self.assertIn("دستیاب نہیں", errors)
        self.assert_urdu(errors)

    def test_installed_library_discovery_does_not_import_and_escaped_name_runs(self):
        import sys
        from urdupy.runtime import execute_source
        from urdupy.urdu_catalog import encode_identifier, encode_text
        name = "_urdupy_unknown_catalog_package"
        escaped = encode_identifier(name)
        with TemporaryDirectory() as directory, patch.dict(sys.modules), \
                patch.object(sys, "path", [directory, *sys.path]):
            (Path(directory) / f"{name}.py").write_text("VALUE = 42\n", encoding="utf-8")
            with patch("importlib.import_module") as imports:
                status, output, errors = self.invoke("نام", "--کتب_خانے")
            self.assertEqual(status, 0, errors)
            imports.assert_not_called()
            self.assertNotIn(name, sys.modules)
            self.assertIn(escaped, output)
            self.assert_urdu(output)
            source = (f"# اردوپائی: مکمل\nدرآمد {escaped}\n"
                      f"جواب = خاصیت_لو({escaped}, اصل_متن('{encode_text('VALUE')}'))\n")
            self.assert_urdu(source)
            result = execute_source(source)
            self.assertEqual(result["جواب"], 42)

    def test_unusual_library_names_are_discovered_and_imported_exactly(self):
        import sys
        from urdupy.runtime import execute_source
        from urdupy.urdu_catalog import encode_text
        names = ["future-library", "K", "😀", "class"]
        with TemporaryDirectory() as directory, patch.dict(sys.modules), \
                patch.object(sys, "path", [directory, *sys.path]):
            for index, name in enumerate(names):
                (Path(directory) / f"{name}.py").write_text(f"VALUE = {index}\n", encoding="utf-8")
            with patch("importlib.import_module") as imports:
                status, output, errors = self.invoke("نام", "--کتب_خانے")
            self.assertEqual(status, 0, errors)
            imports.assert_not_called()
            self.assert_urdu(output)
            for index, name in enumerate(names):
                with self.subTest(name=name):
                    expression = f'ماڈیول_لاؤ(اصل_متن("{encode_text(name)}"))'
                    self.assertIn(expression, output)
                    source = (f"# اردوپائی: مکمل\nکتاب = {expression}\n"
                              f"جواب = خاصیت_لو(کتاب, اصل_متن('{encode_text('VALUE')}'))\n")
                    self.assertEqual(execute_source(source)["جواب"], index)

    def test_namespace_library_discovery_does_not_execute_children(self):
        import sys
        from urdupy.runtime import execute_source
        from urdupy.urdu_catalog import encode_identifier
        name = "_urdupy_namespace_catalog_fixture"
        escaped = encode_identifier(name)
        with TemporaryDirectory() as directory, patch.dict(sys.modules), \
                patch.object(sys, "path", [directory, *sys.path]):
            package = Path(directory) / name
            package.mkdir()
            sentinel = Path(directory) / "unexpected-import.txt"
            (package / "side_effect.py").write_text(
                f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('unexpected')\n",
                encoding="utf-8")
            with patch("importlib.import_module") as imports:
                status, output, errors = self.invoke("نام", "--کتب_خانے")
            self.assertEqual(status, 0, errors)
            imports.assert_not_called()
            self.assertIn(escaped, output)
            self.assert_urdu(output)
            self.assertNotIn(name, sys.modules)
            self.assertNotIn(f"{name}.side_effect", sys.modules)
            self.assertFalse(sentinel.exists())
            execute_source(f"# اردوپائی: مکمل\nدرآمد {escaped}\n")
            self.assertIn(name, sys.modules)
            self.assertFalse(sentinel.exists())

    def test_library_discovery_requires_no_namespace_and_original_is_optional(self):
        status, output, errors = self.invoke("نام", "ریاضی", "--کتب_خانے")
        self.assertEqual(status, 2)
        self.assert_urdu(errors)
        status, output, errors = self.invoke("نام", "--کتب_خانے", "--اصل")
        self.assertEqual(status, 0, errors)
        self.assertIn(" = sys", output)

    def test_install_profiles_are_explicit_and_use_current_interpreter(self):
        import sys
        root = Path("E:/local/اردوپائی")
        for args, suffix in [((), ""), (("بنیادی",), ""), (("سائنسی",), "[science]"),
                             (("مصنوعی_ذہانت",), "[ai]")]:
            with self.subTest(args=args), patch("urdupy.cli._checkout_root", return_value=root), \
                    patch("urdupy.cli.subprocess.run", return_value=SimpleNamespace(returncode=0)) as install:
                status, output, errors = self.invoke("نصب", *args)
                self.assertEqual(status, 0, errors)
                self.assertEqual(install.call_args.args[0],
                                 [sys.executable, "-m", "pip", "install", f"{root}{suffix}"])
                self.assertNotIn("shell", install.call_args.kwargs)
                self.assertIn("تنصیب مکمل", output)
                self.assert_urdu(output)

    def test_unpublished_installed_package_does_not_guess_registry_install(self):
        with patch("urdupy.cli._checkout_root", return_value=None), patch("urdupy.cli.subprocess.run") as install:
            status, output, errors = self.invoke("نصب", "مصنوعی_ذہانت")
        self.assertEqual(status, 1)
        self.assertIn("شائع نہیں", errors)
        install.assert_not_called()
        self.assert_urdu(errors)

    def test_failed_install_propagates_status_in_urdu(self):
        with patch("urdupy.cli._checkout_root", return_value=Path("E:/local/اردوپائی")), \
                patch("urdupy.cli.subprocess.run", return_value=SimpleNamespace(returncode=3)):
            status, output, errors = self.invoke("نصب", "سائنسی")
        self.assertEqual(status, 3)
        self.assertIn("تنصیب ناکام", errors)
        self.assert_urdu(errors)

    def test_repl_starts_in_complete_urdu_mode(self):
        lines = ["درآمد ریاضی", "دکھاؤ(ریاضی.مربع_جذر(16))", EOFError]
        with patch("builtins.input", side_effect=lines):
            status, output, errors = self.invoke("بیٹھک")
        self.assertEqual(status, 0, errors)
        self.assertIn("4.0", output)
        self.assertIn("اردو نشست", errors)
        self.assertNotIn("Error", errors)


if __name__ == "__main__":
    unittest.main()
