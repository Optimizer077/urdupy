"""Execute Phase 1 namespace contracts as experiments, not a public runtime."""

import builtins
import sys
import unittest
from types import ModuleType
from unittest.mock import patch

from urdupy.experimental import compile_urdu
from urdupy.lexicon import BUILTIN_ALIASES, DEFERRED_KEYWORDS, KEYWORDS


def execute_design_sample(source):
    """A test-only execution fixture; never mutates process-wide built-ins."""
    module_builtins = vars(builtins).copy()
    module_builtins.update({
        alias: getattr(builtins, name) for alias, name in BUILTIN_ALIASES.items()
    })
    namespace = {"__name__": "design_sample", "__builtins__": module_builtins}
    exec(compile_urdu(source, filename="namespace_contract.urdu"), namespace)
    return namespace


class NamespaceDesignTests(unittest.TestCase):
    def test_aliases_resolve_to_actual_cpython_objects_without_global_exports(self):
        namespace = execute_design_sample(
            "RESULT = (دکھاؤ, حد, فہرست, صحیح_عدد, قسم)\n"
        )
        self.assertEqual(namespace["RESULT"], (print, range, list, int, type))
        self.assertFalse(set(BUILTIN_ALIASES).intersection(namespace))
        self.assertFalse(set(BUILTIN_ALIASES).intersection(vars(builtins)))

    def test_user_function_shadows_output_alias(self):
        namespace = execute_design_sample(
            "فنکشن دکھاؤ(value):\n"
            "    واپس value * 2\n"
            "RESULT = دکھاؤ(7)\n"
        )
        self.assertEqual(namespace["RESULT"], 14)
        self.assertIsNot(namespace["دکھاؤ"], print)

    def test_alias_parameter_obeys_lexical_scoping(self):
        namespace = execute_design_sample(
            "فنکشن ناپ(لمبائی, values):\n"
            "    واپس لمبائی(values)\n"
            "RESULT = ناپ(lambda values: 99, [1, 2])\n"
        )
        self.assertEqual(namespace["RESULT"], 99)

    def test_isolated_builtin_dictionaries_do_not_affect_other_modules(self):
        first = execute_design_sample("RESULT = حد(3)\n")
        second = execute_design_sample("RESULT = حد(3)\n")
        first["__builtins__"]["حد"] = object()
        self.assertIs(second["__builtins__"]["حد"], range)
        self.assertEqual(list(second["RESULT"]), [0, 1, 2])

    def test_real_builtin_conversion_errors_are_preserved(self):
        with self.assertRaises(ValueError):
            execute_design_sample('RESULT = صحیح_عدد("not a number")\n')

    def test_real_python_api_with_keyword_shaped_export_attribute_and_argument(self):
        api = ModuleType("_urdupy_phase1_api")

        def external_function(**kwargs):
            return kwargs["واپس"] * 2

        setattr(api, "اگر", external_function)
        with patch.dict(sys.modules, {api.__name__: api}):
            namespace = execute_design_sample(
                "سے _urdupy_phase1_api درآمد اگر بطور condition\n"
                "درآمد _urdupy_phase1_api بطور api\n"
                "RESULT = (condition(واپس=7), api.اگر(واپس=8))\n"
            )
        self.assertEqual(namespace["RESULT"], (14, 16))
        self.assertIs(namespace["condition"], external_function)

    def test_none_false_and_empty_list_remain_distinct(self):
        namespace = execute_design_sample(
            "RESULT = (کچھ_نہیں, جھوٹ, فہرست())\n"
        )
        nothing, false, empty = namespace["RESULT"]
        self.assertIsNone(nothing)
        self.assertIs(false, False)
        self.assertEqual(empty, [])
        self.assertIsNot(nothing, false)
        self.assertIsNot(nothing, empty)

    def test_identity_word_preserves_identity_not_equality(self):
        namespace = execute_design_sample(
            "left = [1]\n"
            "right = [1]\n"
            "RESULT = (left == right, left ہے right, left ہے left)\n"
        )
        self.assertEqual(namespace["RESULT"], (True, False, True))

    def test_candidates_do_not_silently_become_active_spellings(self):
        # These proposals change language behavior and must not be accepted by
        # merely adding a friendly synonym during unrelated implementation work.
        for candidate in ("پوچھو", "کوئی_نہیں", "یکساں_شے"):
            with self.subTest(candidate=candidate):
                self.assertNotIn(candidate, KEYWORDS)
                self.assertNotIn(candidate, BUILTIN_ALIASES)
        self.assertFalse(set(DEFERRED_KEYWORDS).intersection(KEYWORDS))


if __name__ == "__main__":
    unittest.main()
