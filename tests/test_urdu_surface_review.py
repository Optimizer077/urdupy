"""Independent full-Urdu import, protocol, completeness and source-map review."""

import ast
from contextlib import redirect_stderr
from io import StringIO
import importlib
import math
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType
import unittest
from unittest.mock import patch

from urdupy import compile_urdu, execute_source, translate_with_map
from urdupy.runtime import format_exception
from urdupy.repl import UrduConsole
from urdupy.urdu_catalog import encode_identifier, encode_text
from urdupy.urdu_surface import DIRECTIVE


def full_source(text):
    return DIRECTIVE + "\n" + text


class CompleteUrduIndependentReview(unittest.TestCase):
    def test_multiple_dotted_imports_keep_native_root_and_explicit_alias_bindings(self):
        xml, etree, element_tree, dom, minidom = map(encode_identifier, ("xml", "etree", "ElementTree", "dom", "minidom"))
        element, document = map(encode_identifier, ("Element", "Document"))
        source = full_source(
            f"درآمد {xml}.{etree}.{element_tree}, {xml}.{dom}.{minidom} بطور دوسرا # درآمدی تبصرہ\n"
            f"نتیجہ = ({xml}.{etree}.{element_tree}.{element}('جڑ'), دوسرا.{document}())\n"
        )
        translated = translate_with_map(source)
        self.assertIn("# درآمدی تبصرہ", translated.text)
        first, second = execute_source(source)["نتیجہ"]
        self.assertEqual(first.tag, "جڑ")
        self.assertEqual(type(second).__module__, "xml.dom.minidom")

    def test_multiline_dotted_import_lf_crlf_bom_and_original_call_locations(self):
        xml, etree, element_tree, element = map(encode_identifier, ("xml", "etree", "ElementTree", "Element"))
        body = (
            f"درآمد {xml}.\\\n    {etree}.\\\n    {element_tree} # آخر کا تبصرہ\n"
            f"نتیجہ = {xml}.{etree}.{element_tree}.{element}('جڑ')\n"
        )
        for bom, newline in (("", "\n"), ("\ufeff", "\n"), ("", "\r\n"), ("\ufeff", "\r\n")):
            source = bom + full_source(body).replace("\n", newline)
            with self.subTest(bom=bool(bom), newline=repr(newline)):
                self.assertEqual(execute_source(source)["نتیجہ"].tag, "جڑ")
                translated = translate_with_map(source)
                self.assertIn("# آخر کا تبصرہ", translated.text)
                tree = compile_urdu(source, flags=ast.PyCF_ONLY_AST)
                call = next(node for node in ast.walk(tree) if isinstance(node, ast.Call))
                self.assertEqual(call.lineno, 5)
                line = source.splitlines()[call.lineno - 1]
                self.assertEqual(line.encode()[call.col_offset:call.end_col_offset].decode(), body.splitlines()[-1].split(" = ")[1])

    def test_parenthesized_from_import_retains_comments_aliases_and_native_names(self):
        source = full_source(
            "سے ریاضی درآمد (\n"
            "    مربع_جذر بطور جڑ, # پہلا تبصرہ\n"
            "    فرش, # دوسرا تبصرہ\n"
            ")\n"
            "نتیجہ = (جڑ(81), فرش(3.5))\n"
        )
        translated = translate_with_map(source)
        self.assertIn("# پہلا تبصرہ", translated.text)
        self.assertIn("# دوسرا تبصرہ", translated.text)
        self.assertEqual(execute_source(source)["نتیجہ"], (9, 3))

    def test_multiline_from_module_path_and_inline_suite_imports(self):
        for body in (
            "سے \\\n    ریاضی \\\n    درآمد مربع_جذر\nنتیجہ = مربع_جذر(25)\n",
            "اگر سچ: درآمد ریاضی; نتیجہ = ریاضی.مربع_جذر(25)\n",
        ):
            with self.subTest(body=body):
                self.assertEqual(execute_source(full_source(body))["نتیجہ"], 5)

    def test_from_alias_and_star_use_real_export_names(self):
        module = ModuleType("_urdu_review_exports")
        module.shape = 31
        module.backend_future_431 = 47
        module.__all__ = ["shape", "backend_future_431"]
        path = encode_identifier(module.__name__)
        future = encode_identifier("backend_future_431")
        with patch.dict(sys.modules, {module.__name__: module}):
            for imports in (f"سے {path} درآمد شکل, {future}", f"سے {path} درآمد *"):
                with self.subTest(imports=imports):
                    result = execute_source(full_source(f"{imports}\nنتیجہ = (شکل, {future})\n"))
                    self.assertEqual(result["نتیجہ"], (31, 47))

    def test_native_unicode_export_matching_language_keyword_remains_reachable(self):
        module = ModuleType("_urdu_review_unicode")
        setattr(module, "اگر", lambda: 17)
        module.__all__ = ["اگر"]
        path, symbol = map(encode_identifier, (module.__name__, "اگر"))
        with patch.dict(sys.modules, {module.__name__: module}):
            for imports, expression in (
                (f"درآمد {path}", f"{path}.{symbol}()"),
                (f"سے {path} درآمد {symbol}", f"{symbol}()"),
                (f"سے {path} درآمد *", f"{symbol}()"),
            ):
                with self.subTest(imports=imports):
                    self.assertEqual(execute_source(full_source(f"{imports}\nنتیجہ = {expression}\n"))["نتیجہ"], 17)

    def test_reserved_member_alias_as_import_asname_lowers_consistently(self):
        result = execute_source(full_source("درآمد ریاضی بطور شکل\nنتیجہ = شکل.مربع_جذر(64)\n"))
        self.assertEqual(result["نتیجہ"], 8)
        self.assertIs(result["shape"], math)

    def test_relative_encoded_module_path_finds_native_python_module(self):
        package = ModuleType("_urdu_review_relative")
        module = encode_identifier("backend")
        with TemporaryDirectory() as directory:
            package.__path__ = [directory]
            Path(directory, "backend.py").write_text("shape = 37\n", encoding="utf-8")
            try:
                with patch.dict(sys.modules, {package.__name__: package}):
                    namespace = {"__name__": package.__name__ + ".consumer", "__package__": package.__name__}
                    result = execute_source(full_source(f"سے .{module} درآمد شکل\nنتیجہ = شکل\n"), globals=namespace)
                    self.assertEqual(result["نتیجہ"], 37)
            finally:
                sys.modules.pop(package.__name__ + ".backend", None)

    def test_value_names_do_not_rewrite_attributes_or_prevent_lexical_shadowing(self):
        source = full_source(
            "کلاس میری:\n    مرکزی_آلہ = 'میری قدر'\n"
            "نتیجہ = (میری.مرکزی_آلہ, مرکزی_آلہ)\n"
            "فنکشن میری_دلیل(مرکزی_آلہ):\n    واپس مرکزی_آلہ\n"
            "دوسرا = میری_دلیل(مرکزی_آلہ='مقامی قدر')\n"
        )
        result = execute_source(source)
        self.assertEqual(result["نتیجہ"], ("میری قدر", "cpu"))
        self.assertEqual(result["دوسرا"], "مقامی قدر")

    def test_container_protocols_private_name_mangling_and_zero_argument_super(self):
        private = encode_identifier("__hidden")
        source = full_source(
            f"کلاس میری:\n    فنکشن آغاز(خود):\n        خود.{private} = [2, 4, 6]\n"
            f"    فنکشن شے_لمبائی(خود):\n        واپس لمبائی(خود.{private})\n"
            f"    فنکشن جزو_لو(خود, مقام):\n        واپس خود.{private}[مقام]\n"
            "کلاس اولاد(میری):\n    فنکشن آغاز(خود):\n        بالائی().آغاز()\n"
            "نتیجہ = (لمبائی(اولاد()), فہرست(اولاد()))\n"
        )
        self.assertEqual(execute_source(source)["نتیجہ"], (3, [2, 4, 6]))

    def test_arbitrary_nonidentifier_attribute_and_keyword_key_via_text_escape(self):
        name = "not a Python.identifier!"
        key = "kwargs-key.with punctuation"
        module = ModuleType("_urdu_review_nonidentifiers")
        setattr(module, name, lambda **kwargs: kwargs[key])
        path = encode_identifier(module.__name__)
        source = full_source(
            f"درآمد {path}\n"
            f"نتیجہ = خاصیت_لو({path}, اصل_متن('{encode_text(name)}'))"
            f"(**{{اصل_متن('{encode_text(key)}'): 29}})\n"
        )
        self.assertFalse(any(char.isascii() and char.isalpha() for char in source))
        with patch.dict(sys.modules, {module.__name__: module}):
            self.assertEqual(execute_source(source)["نتیجہ"], 29)

    def test_library_edits_preserve_syntax_error_character_columns(self):
        source = full_source("درآمد ریاضی\nنتیجہ = ریاضی.مربع_جذر(9, نام=)\n")
        original = source.splitlines()[2]
        with self.assertRaises(SyntaxError) as caught:
            compile_urdu(source, "مقامی_خطا.urdu")
        self.assertEqual(caught.exception.filename, "مقامی_خطا.urdu")
        self.assertEqual(caught.exception.lineno, 3)
        self.assertEqual(caught.exception.text.rstrip("\r\n"), original)
        # CPython marks the incomplete named argument, including its '='.
        self.assertEqual(caught.exception.offset, original.index("نام") + 1)
        self.assertEqual(caught.exception.end_offset, original.index(")") + 1)

    def test_native_runtime_error_retains_original_urdu_call_in_captured_trace(self):
        original = "نتیجہ = ریاضی.مربع_جذر(-1)"
        source = full_source("درآمد ریاضی\n" + original + "\n")
        with self.assertRaises(ValueError) as caught:
            execute_source(source)
        trace = format_exception(caught.exception)
        self.assertIn(original, trace)
        self.assertIn("line 3", trace)

    def test_context_descriptor_and_iterator_protocols_are_real_cpython_protocols(self):
        source = full_source(
            "کلاس وصف:\n"
            "    فنکشن وصف_لو(خود, مالک, نوع):\n        واپس 23\n"
            "کلاس میری:\n"
            "    قدر_میری = وصف()\n"
            "    فنکشن داخل(خود):\n        واپس خود\n"
            "    فنکشن خارج(خود, نوع, خطا, نقش):\n        واپس جھوٹ\n"
            "    فنکشن تکرار(خود):\n        واپس دہرانے_والا([3, 5])\n"
            "ساتھ میری() بطور نمونہ:\n    نتیجہ = (نمونہ.قدر_میری, فہرست(نمونہ))\n"
        )
        self.assertEqual(execute_source(source)["نتیجہ"], (23, [3, 5]))

    def test_console_incomplete_import_call_and_native_protocol_class(self):
        errors = StringIO()
        with UrduConsole(complete=True) as console, redirect_stderr(errors):
            self.assertTrue(console.push("سے ریاضی درآمد ("))
            self.assertTrue(console.push("مربع_جذر,"))
            self.assertFalse(console.push(")"))
            self.assertTrue(console.push("نتیجہ = مربع_جذر("))
            self.assertFalse(console.push("49)"))
            self.assertEqual(console.locals["نتیجہ"], 7)
            self.assertTrue(console.push("کلاس میری:"))
            self.assertTrue(console.push("    فنکشن شے_لمبائی(خود):"))
            self.assertTrue(console.push("        واپس 4"))
            self.assertFalse(console.push(""))
            self.assertEqual(len(console.locals["میری"]()), 4)
        self.assertEqual(errors.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
