"""Native semantics and full dependency reach without optional libraries."""

import ast
from contextlib import redirect_stdout
from io import StringIO
import math
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType
import unittest

from urdupy import execute_source, compile_urdu, translate_with_map, install_importer
from urdupy.urdu_surface import DIRECTIVE, enabled


class CompleteUrduSurface(unittest.TestCase):
    def source(self, text):
        return DIRECTIVE + "\n" + text

    def encode(self, name):
        from urdupy.urdu_catalog import encode_identifier
        return encode_identifier(name)

    def test_directive_is_explicit_leading_comment_and_not_literal_data(self):
        self.assertTrue(enabled(DIRECTIVE + "\nگزر"))
        self.assertTrue(enabled("\ufeff# آغاز\r\n" + DIRECTIVE + "\r\nگزر"))
        self.assertFalse(enabled(repr(DIRECTIVE)))
        self.assertFalse(enabled("گزر\n" + DIRECTIVE))
        self.assertFalse(enabled("'''\n" + DIRECTIVE + "\n'''"))

    def test_encoded_arbitrary_stdlib_import_export_and_keywords(self):
        mod = self.encode("json")
        dumps = self.encode("dumps")
        ensure = self.encode("ensure_ascii")
        source = self.source(f"درآمد {mod}\nنتیجہ = {mod}.{dumps}({{'نام': 'سلام'}}, {ensure}=جھوٹ)\n")
        self.assertFalse(any(c.isascii() and c.isalpha() for c in source))
        self.assertEqual(execute_source(source)["نتیجہ"], '{"نام": "سلام"}')

    def test_readable_import_is_real_module_and_does_not_mutate_it(self):
        before = set(vars(math))
        result = execute_source(self.source("درآمد ریاضی\nنتیجہ = ریاضی\n"))
        self.assertIs(result["نتیجہ"], math)
        self.assertEqual(set(vars(math)), before)
        self.assertNotIn("ریاضی", sys.modules)

    def test_dotted_encoded_import_binds_native_root_and_alias(self):
        first, second, third = map(self.encode, ("xml", "etree", "ElementTree"))
        element = self.encode("Element")
        for suffix, expression in (("", f"{first}.{second}.{third}"), (" بطور درخت", "درخت")):
            with self.subTest(suffix=suffix):
                source = self.source(f"درآمد {first}.{second}.{third}{suffix}\nنتیجہ = {expression}.{element}('جڑ')\n")
                value = execute_source(source)["نتیجہ"]
                self.assertEqual(value.tag, "جڑ")
                self.assertEqual(type(value).__module__, "xml.etree.ElementTree")

    def test_from_import_exports_and_aliases(self):
        mod, symbol = map(self.encode, ("math", "sqrt"))
        for suffix, expression in (("", symbol), (" بطور جڑ", "جڑ")):
            with self.subTest(suffix=suffix):
                self.assertEqual(execute_source(self.source(f"سے {mod} درآمد {symbol}{suffix}\nنتیجہ = {expression}(81)"))["نتیجہ"], 9)

    def test_unknown_api_all_identifier_positions_and_native_protocols(self):
        name, arg, member, protocol = map(self.encode, ("unlisted_function_987", "unlisted_argument_321", "unlisted_field_654", "__call__"))
        source = self.source(
            f"فنکشن {name}({arg}=3):\n    واپس {arg} * 2\n"
            f"کلاس آزمائش:\n    فنکشن آغاز(خود):\n        خود.{member} = 7\n"
            f"    فنکشن {protocol}(خود):\n        واپس خود.{member}\n"
            f"نتیجہ = ({name}({arg}=9), آزمائش()())\n"
        )
        self.assertEqual(execute_source(source)["نتیجہ"], (18, 7))

    def test_arbitrary_backend_strings_roundtrip_without_english_source(self):
        from urdupy.urdu_catalog import encode_text
        for value in ("cpu", "cuda:0", "state_dict.weight", "RGB", "", "x\x00y", "a/b.ckpt", "نام🌍"):
            with self.subTest(value=value):
                source = self.source(f"نتیجہ = اصل_متن('{encode_text(value)}')\n")
                self.assertFalse(any(c.isascii() and c.isalpha() for c in source))
                self.assertEqual(execute_source(source)["نتیجہ"], value)
        with self.assertRaises(ValueError):
            execute_source(self.source("اصل_متن('غلط')"))

    def test_uniform_keyword_lowering_matches_user_parameter_definition(self):
        # Native argument vocabulary can also appear in ordinary Urdu functions.
        source = self.source("فنکشن حساب(شرح_تعلم=2):\n    واپس شرح_تعلم * 3\nنتیجہ = حساب(شرح_تعلم=5)\n")
        self.assertEqual(execute_source(source)["نتیجہ"], 15)

    def test_legacy_urdu_attributes_and_protocol_names_remain_unmodified(self):
        source = "کلاس آزمائش:\n    شکل = 42\nنتیجہ = آزمائش.شکل\n"
        self.assertEqual(execute_source(source)["نتیجہ"], 42)
        self.assertIn("شکل", translate_with_map(source).text)
        self.assertNotIn("اصل_متن", execute_source("گزر")["__builtins__"])

    def test_string_comment_debug_labels_and_original_positions(self):
        source = self.source("درآمد ریاضی\nنتیجہ = f'{ریاضی.مربع_جذر(9)=}'\nمتن = 'شکل آغاز' # شکل آغاز\n")
        result = execute_source(source)
        self.assertEqual(result["نتیجہ"], "ریاضی.مربع_جذر(9)=3.0")
        translated = translate_with_map(source)
        self.assertIn("'شکل آغاز' # شکل آغاز", translated.text)
        tree = compile_urdu(source, flags=ast.PyCF_ONLY_AST)
        call = next(node for node in ast.walk(tree) if isinstance(node, ast.Call))
        line = source.splitlines()[call.lineno - 1]
        self.assertEqual(line.encode()[call.col_offset:call.end_col_offset].decode(), "ریاضی.مربع_جذر(9)")

    def test_check_never_imports_dependency(self):
        unknown = self.encode("missing_urdupy_dependency_93862")
        self.assertNotIn("missing_urdupy_dependency_93862", sys.modules)
        compile_urdu(self.source(f"درآمد {unknown}\nنتیجہ = 7\n"))
        self.assertNotIn("missing_urdupy_dependency_93862", sys.modules)

    def test_imported_urdu_modules_share_the_mode_and_native_objects(self):
        with TemporaryDirectory() as directory:
            Path(directory, "مکمل_امتحان.urdu").write_text(self.source("درآمد ریاضی\nنتیجہ = ریاضی\n"), encoding="utf-8")
            old = sys.path[:]
            sys.path.insert(0, directory)
            try:
                with install_importer():
                    import importlib
                    module = importlib.import_module("مکمل_امتحان")
                    self.assertIs(module.نتیجہ, math)
            finally:
                sys.path[:] = old
                sys.modules.pop("مکمل_امتحان", None)

    def test_complete_console_persists_across_entries(self):
        from urdupy.repl import UrduConsole
        with UrduConsole(complete=True) as console:
            self.assertFalse(console.runsource("درآمد ریاضی"))
            self.assertFalse(console.runsource("نتیجہ = ریاضی.مربع_جذر(16)"))
            self.assertEqual(console.locals["نتیجہ"], 4)


if __name__ == "__main__":
    unittest.main()
