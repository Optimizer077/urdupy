"""Dependency-free contracts for complete-Urdu API vocabulary and fallback."""

import ast
import builtins
import json
import keyword
import math
from pathlib import Path
import re
import subprocess
import sys
import unittest

from urdupy import urdu_catalog as catalog
from urdupy.lexicon import BUILTIN_ALIASES, PRODUCTION_KEYWORDS, SOFT_KEYWORDS


class IdentifierSpellingTests(unittest.TestCase):
    def test_unknown_api_name_has_exact_portable_urdu_only_spelling(self):
        self.assertEqual(catalog.encode_identifier("a_Z"), "اصل_۹۷_۹۵_۹۰")
        self.assertEqual(catalog.decode_identifier("اصل_۹۷_۹۵_۹۰"), "a_Z")
        self.assertIsNone(re.search(r"[A-Za-z]", catalog.encode_identifier("future_API42")))
        self.assertTrue(catalog.encode_identifier("future_API42").isidentifier())

    def test_public_private_dunder_and_unicode_identifiers_roundtrip(self):
        for original in (
            "x", "_", "_private", "__init__", "forward", "float32",
            "MyFutureModel2028", "نام", "کلاس_میری", "é", "e\u0301", "K",
            "Δοκιμή", "模型", "a\U00010400", "\U00010400x", "a\u0e50",
        ):
            with self.subTest(original=original):
                alias = catalog.encode_identifier(original)
                self.assertTrue(alias.isidentifier())
                self.assertEqual(catalog.decode_identifier(alias), original)
                self.assertEqual(catalog.canonical_name(alias), original)

    def test_arbitrary_standard_library_api_identifiers_roundtrip(self):
        # Exercise real installed API names without importing optional libraries.
        originals = set(dir(builtins)) | set(dir(math)) | set(dir(Path))
        for original in originals:
            if original.isidentifier() and not keyword.iskeyword(original):
                with self.subTest(original=original):
                    self.assertEqual(catalog.decode_identifier(catalog.encode_identifier(original)), original)

    def test_invalid_identifier_inputs_are_rejected(self):
        for original in ("", "42", "2d", "x.y", "has space", "x-y", "if", "True", "None", "\x00", "\ud800"):
            with self.subTest(original=repr(original)):
                with self.assertRaises(ValueError):
                    catalog.encode_identifier(original)
        for original in (None, 123, b"x", ["x"]):
            with self.subTest(original=original), self.assertRaises(TypeError):
                catalog.encode_identifier(original)

    def test_malformed_and_noncanonical_identifier_spellings_remain_unrecognized(self):
        # No implicit acceptance of ASCII digits, leading zeros or impossible codepoints.
        for alias in (
            None, 123, "نام", "اصل_", "اصل_97", "اصل_۹7", "اصل_۰۹۷",
            "اصل_۹۷_", "اصل__۹۷", "اصل_۱۱۱۴۱۱۲", "اصل_۵۵۲۹۶", "اصل_۰",
            "اصل_۳۲", "اصل_۴۹", "اصل_۹۷_۴۶_۹۸", "اصل_۱۰۵_۱۰۲",
            "اصل_" + "۹" * 10000,
        ):
            with self.subTest(alias=repr(alias)[:80]):
                self.assertIsNone(catalog.decode_identifier(alias))

    def test_unknown_normal_names_are_not_silently_changed(self):
        for name in ("میرا_فنکشن", "some_future_api", "اصل_97"):
            self.assertEqual(catalog.canonical_name(name), name)


class TextSpellingTests(unittest.TestCase):
    def test_empty_nul_and_ascii_have_distinct_exact_spellings(self):
        self.assertEqual(catalog.encode_text(""), "متن_")
        self.assertEqual(catalog.encode_text("\0"), "متن_۰")
        self.assertEqual(catalog.encode_text("cpu"), "متن_۹۹_۱۱۲_۱۱۷")
        self.assertEqual(catalog.decode_text("متن_"), "")
        self.assertEqual(catalog.decode_text("متن_۰"), "\0")
        self.assertEqual(catalog.decode_text("متن_۹۹_۱۱۲_۱۱۷"), "cpu")

    def test_arbitrary_paths_enum_values_keys_and_unicode_roundtrip(self):
        for text in (
            "", "cpu", "cuda:0", "RGB", "torch.float32", "C:\\folder\\file.pt",
            "/tmp/a b/نام.json", "*.png", "a-b.c:d", "utf-8", "\0\r\n\t",
            "انگریزی English اور اردو", "é", "e\u0301", "🙂", "\ud800\udfff",
            "".join(chr(point) for point in (0, 1, 127, 128, 255, 256, 0xD7FF, 0xD800, 0xE000, 0xFFFF, 0x10000, 0x10FFFF)),
        ):
            with self.subTest(text=repr(text)):
                encoded = catalog.encode_text(text)
                self.assertIsNone(re.search(r"[A-Za-z]", encoded))
                encoded.encode("utf-8")
                self.assertEqual(catalog.decode_text(encoded), text)

    def test_identifier_and_text_namespaces_cannot_be_confused(self):
        self.assertIsNone(catalog.decode_identifier(catalog.encode_text("tensor")))
        self.assertIsNone(catalog.decode_text(catalog.encode_identifier("tensor")))

    def test_invalid_text_spellings_and_types_are_rejected(self):
        for alias in (None, 1, "", "cpu", "متن_99", "متن_۹9", "متن_۰۰", "متن_۰_", "متن__۰", "متن_۱۱۱۴۱۱۲", "متن_" + "۹" * 10000):
            with self.subTest(alias=repr(alias)[:80]):
                self.assertIsNone(catalog.decode_text(alias))
        for text in (None, 1, b"text"):
            with self.subTest(text=text), self.assertRaises(TypeError):
                catalog.encode_text(text)


class VocabularyTests(unittest.TestCase):
    def test_native_dependency_paths_and_essential_training_names(self):
        self.assertEqual(catalog.MODULE_ALIASES["ٹارچ"], "torch")
        self.assertEqual(catalog.MODULE_ALIASES["نمپی"], "numpy")
        self.assertEqual(catalog.MODULE_ALIASES["خاکہ"], "matplotlib.pyplot")
        expected = {
            "عصبی": "nn", "جزو": "Module", "خطی": "Linear",
            "پیچش۲": "Conv2d", "ایڈم_ڈبلیو": "AdamW", "اصلاح": "optim",
            "پیرامیٹر": "parameters", "پیچھے": "backward", "قدم": "step",
            "شرح_تعلم": "lr", "شکل": "shape", "قسم_اعداد": "dtype", "آلہ": "device",
            "وزن_پیرامیٹر": "weight", "وزن": "weights", "سرنی": "array",
            "برٹ_ترتیب": "BertConfig", "نام_ماڈیول": "__name__",
        }
        for alias, original in expected.items():
            with self.subTest(alias=alias):
                self.assertEqual(catalog.canonical_name(alias), original)
        self.assertEqual(catalog.PROTOCOL_ALIASES["آغاز"], "__init__")
        self.assertEqual(catalog.PROTOCOL_ALIASES["آگے"], "forward")

    def test_preferred_names_support_discovery_and_unlisted_future_apis(self):
        for original, expected in (
            ("torch", "ٹارچ"), ("numpy", "نمپی"), ("matplotlib.pyplot", "خاکہ"),
            ("Module", "جزو"), ("__init__", "آغاز"), ("super", "بالائی"),
        ):
            self.assertEqual(catalog.urdu_name(original), expected)
        fallback = catalog.urdu_name("FutureDependencyAPI")
        self.assertEqual(catalog.decode_identifier(fallback), "FutureDependencyAPI")
        for helper in (catalog.canonical_name, catalog.urdu_name):
            with self.assertRaises(TypeError):
                helper(None)

    def test_all_curated_aliases_are_urdu_identifiers_without_language_collisions(self):
        reserved = set(PRODUCTION_KEYWORDS) | set(SOFT_KEYWORDS)
        for group, aliases in catalog.vocabulary().items():
            for alias in aliases:
                with self.subTest(group=group, alias=alias):
                    self.assertTrue(alias.isidentifier())
                    self.assertIsNone(re.search(r"[A-Za-z]", alias))
                    self.assertNotIn(alias, reserved)
                    self.assertFalse(alias.startswith("اصل_"))

    def test_dictionary_literals_have_no_silently_overwritten_names(self):
        tree = ast.parse(Path(catalog.__file__).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                keys = [key.value for key in node.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)]
                self.assertEqual(len(keys), len(set(keys)), f"duplicate catalog keys near line {node.lineno}")

    def test_legacy_builtin_spellings_and_native_object_identity_are_preserved(self):
        for alias, original in BUILTIN_ALIASES.items():
            with self.subTest(alias=alias):
                self.assertEqual(catalog.BUILTIN_NAMES[alias], original)
                self.assertEqual(catalog.canonical_name(alias), original)
                self.assertNotIn(alias, catalog.MEMBER_ALIASES)
                self.assertNotIn(alias, catalog.PROTOCOL_ALIASES)
        for alias, original in catalog.BUILTIN_NAMES.items():
            self.assertTrue(hasattr(builtins, original), f"{alias}: missing native builtin {original}")

    def test_shared_names_in_member_protocol_builtin_namespaces_never_disagree(self):
        known = {}
        for aliases in (catalog.MEMBER_ALIASES, catalog.PROTOCOL_ALIASES, catalog.BUILTIN_NAMES):
            for alias, original in aliases.items():
                self.assertEqual(known.setdefault(alias, original), original, alias)

    def test_literal_values_remain_distinct_from_attribute_names(self):
        self.assertEqual(catalog.VALUE_ALIASES["مرکزی_آلہ"], "cpu")
        self.assertEqual(catalog.VALUE_ALIASES["گرافیکی_آلہ"], "cuda")
        self.assertEqual(catalog.VALUE_ALIASES["مرکزی_نام"], "__main__")
        self.assertEqual(catalog.canonical_name("مرکزی"), "cpu")
        self.assertEqual(catalog.canonical_name("مرکزی_آلہ"), "مرکزی_آلہ")
        for value in catalog.VALUE_ALIASES.values():
            self.assertIsInstance(value, (str, int, float, bool, type(None), type(Ellipsis), type(NotImplemented)))

    def test_inventory_is_independent_of_registry_and_other_calls(self):
        first = catalog.vocabulary()
        second = catalog.vocabulary()
        self.assertEqual(set(first), {"modules", "members", "builtins", "values", "protocols"})
        first["modules"]["ٹارچ"] = "not_torch"
        first["members"].clear()
        self.assertEqual(second["modules"]["ٹارچ"], "torch")
        self.assertEqual(catalog.MODULE_ALIASES["ٹارچ"], "torch")
        self.assertIn("جزو", catalog.MEMBER_ALIASES)

    def test_importing_catalog_does_not_import_optional_dependencies(self):
        program = (
            "import json, sys\n"
            "before = set(sys.modules)\n"
            "import urdupy.urdu_catalog\n"
            "print(json.dumps(sorted(set(sys.modules) - before)))\n"
        )
        result = subprocess.run([sys.executable, "-X", "utf8", "-c", program], capture_output=True, text=True, check=True)
        loaded = json.loads(result.stdout)
        heavy = {"torch", "numpy", "cv2", "PIL", "torchvision", "transformers", "matplotlib", "scipy", "pandas"}
        self.assertFalse({name.split(".")[0] for name in loaded} & heavy)


if __name__ == "__main__":
    unittest.main()
