"""Behavioral evidence for the Phase 1 experiment, not a compatibility claim."""

import builtins
import io
import sys
import traceback
import unittest
from contextlib import redirect_stdout
from types import ModuleType
from unittest.mock import patch

from urdupy.experimental import (
    ExperimentalSyntaxError,
    compile_urdu,
    translate,
    translate_with_spans,
)
from urdupy.lexicon import BUILTIN_ALIASES, KEYWORDS


def execute(source, filename="fixture.urdu"):
    namespace = {"__builtins__": dict(vars(builtins))}
    namespace["__builtins__"].update(
        {alias: getattr(builtins, name) for alias, name in BUILTIN_ALIASES.items()}
    )
    exec(compile_urdu(source, filename), namespace)
    return namespace


class TranslationTests(unittest.TestCase):
    def test_function_and_branch_match_python_values(self):
        urdu = (
            "فنکشن مربع(عدد):\n"
            "    اگر عدد >= 0:\n"
            "        واپس عدد * عدد\n"
            "    ورنہ:\n"
            "        واپس کچھ_نہیں\n"
            "نتیجہ = [مربع(x) ہر x میں حد(-1, 4)]\n"
        )
        python = (
            "def مربع(عدد):\n"
            "    if عدد >= 0:\n"
            "        return عدد * عدد\n"
            "    else:\n"
            "        return None\n"
            "نتیجہ = [مربع(x) for x in range(-1, 4)]\n"
        )
        expected = {}
        exec(python, expected)
        self.assertEqual(execute(urdu)["نتیجہ"], expected["نتیجہ"])

    def test_control_flow_and_exception_keywords(self):
        source = (
            "نتیجہ = []\n"
            "ہر x میں حد(5):\n"
            "    اگر x == 0:\n"
            "        جاری\n"
            "    ورنہ_اگر x == 3:\n"
            "        روکو\n"
            "    نتیجہ.append(x)\n"
            "جب_تک جھوٹ:\n"
            "    گزر\n"
            "کوشش:\n"
            "    تصدیق سچ اور نہیں جھوٹ یا جھوٹ\n"
            "    اٹھاؤ ValueError('example')\n"
            "سوائے ValueError بطور error:\n"
            "    نتیجہ.append(str(error))\n"
            "آخرکار:\n"
            "    نتیجہ.append(کچھ_نہیں ہے کچھ_نہیں)\n"
        )
        self.assertEqual(execute(source)["نتیجہ"], [1, 2, "example", True])

    def test_scope_class_context_and_delete_keywords(self):
        source = (
            "درآمد contextlib\n"
            "سے math درآمد sqrt بطور root\n"
            "x = 0\n"
            "فنکشن outer():\n"
            "    y = 0\n"
            "    فنکشن inner():\n"
            "        عالمی x\n"
            "        غیر_مقامی y\n"
            "        x = 3\n"
            "        y = 4\n"
            "    inner()\n"
            "    واپس y\n"
            "کلاس Box:\n"
            "    گزر\n"
            "ساتھ contextlib.nullcontext(root(9)) بطور z:\n"
            "    result = (outer(), x, z, Box.__name__)\n"
            "temporary = 1\n"
            "حذف temporary\n"
        )
        ns = execute(source)
        self.assertEqual(ns["result"], (4, 3, 3.0, "Box"))
        self.assertNotIn("temporary", ns)

    def test_comments_and_string_forms_are_preserved_exactly(self):
        source = (
            '# اگر "واپس" # ورنہ\n'
            'a = "اگر فنکشن واپس # \\""\n'
            "b = r'اگر\\nواپس'\n"
            'c = """اگر\nورنہ # واپس\n"""\n'
            "d = b'English if return'\n"
        )
        self.assertEqual(translate(source), source)
        compile_urdu(source)

    def test_crlf_tabs_and_trailing_space_survive(self):
        source = "اگر سچ:  # اگر\r\n\tگزر  \r\n"
        self.assertEqual(translate(source), "if True:  # اگر\r\n\tpass  \r\n")
        compile_urdu(source)

    def test_bom_is_preserved_for_translation_and_accepted_for_compile(self):
        source = "\ufeffاگر سچ:\n    result = 7\n"
        self.assertEqual(translate(source), "\ufeffif True:\n    result = 7\n")
        self.assertEqual(execute(source)["result"], 7)

    def test_no_final_newline_is_preserved(self):
        self.assertEqual(translate("result = سچ"), "result = True")

    def test_replacement_spans_are_original_character_offsets(self):
        source = "\ufeffعنوان = 'اردو'\r\nاگر سچ: گزر\r\n"
        result = translate_with_spans(source)
        self.assertEqual(result.text, "\ufeffعنوان = 'اردو'\r\nif True: pass\r\n")
        self.assertEqual(len(result.edits), 3)
        for edit in result.edits:
            self.assertEqual(source[edit.original_start:edit.original_end], edit.original)
            self.assertEqual(result.text[edit.translated_start:edit.translated_end], edit.replacement)
        self.assertEqual(result.edits[0].line, 2)
        self.assertEqual(result.edits[0].column, 0)

    def test_source_gaps_are_unchanged_across_multiple_replacements(self):
        source = "اگر سچ اور نہیں جھوٹ:\n    واپس 'اگر' # نہیں\n"
        result = translate_with_spans(source)
        original_cursor = translated_cursor = 0
        for edit in result.edits:
            self.assertEqual(
                source[original_cursor:edit.original_start],
                result.text[translated_cursor:edit.translated_start],
            )
            original_cursor, translated_cursor = edit.original_end, edit.translated_end
        self.assertEqual(source[original_cursor:], result.text[translated_cursor:])

    def test_ordinary_python_is_byte_for_byte_unchanged(self):
        source = (
            "import math\n"
            "def f(x: int = 3, /, *, scale=2):\n"
            "    return math.sqrt(x * x) * scale\n"
            "async def af():\n"
            "    await task()\n"
            "def gen():\n"
            "    yield from range(3)\n"
            "g = lambda x: x + 1\n"
            "match f():\n"
            "    case 6.0:\n"
            "        result = g(1)\n"
        )
        self.assertEqual(translate(source), source)
        compile_urdu(source)

    def test_english_soft_keyword_identifiers_stay_identifiers(self):
        source = "match = 1\ncase = 2\ntype = 3\nresult = match + case + type\n"
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], 6)

    def test_type_statement_passthrough_follows_host_version(self):
        source = "type Item = int\n"
        self.assertEqual(translate(source), source)
        if sys.version_info >= (3, 12):
            compile_urdu(source)
        else:
            with self.assertRaises(SyntaxError):
                compile_urdu(source)

    def test_deferred_urdu_names_are_not_reserved(self):
        source = "منتخب = 1\nصورت = 2\nانتظار = 3\nلامبڈا = 4\nresult = منتخب + صورت\n"
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], 3)

    def test_attribute_words_survive_and_execute(self):
        source = (
            "from types import SimpleNamespace\n"
            "obj = SimpleNamespace(**{'اگر': 4, 'واپس': 5, 'درآمد': 6})\n"
            "result = obj.اگر + obj.واپس + obj.درآمد\n"
        )
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], 15)

    def test_unicode_call_keyword_labels_survive(self):
        source = "def api(**kwargs): return kwargs\nresult = api(اگر=1, واپس=2, سچ=3)\n"
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], {"اگر": 1, "واپس": 2, "سچ": 3})

    def test_nested_and_parenthesized_callable_keyword_labels_survive(self):
        source = (
            "def api(**kwargs): return kwargs\n"
            "result = (api)(اگر=api(واپس=سچ),\n"
            "               جھوٹ=2)\n"
        )
        self.assertEqual(execute(source)["result"], {"اگر": {"واپس": True}, "جھوٹ": 2})

    def test_function_markers_annotations_and_nonreserved_kwargs(self):
        source = (
            "فنکشن f(x: int, /, y=سچ, *args, factor=2, **kwargs):\n"
            "    واپس (x * factor, y, args, kwargs)\n"
            "result = f(3, factor=4, extra='ok')\n"
        )
        self.assertEqual(execute(source)["result"], (12, True, (), {"extra": "ok"}))

    def test_from_import_keyword_shaped_export_is_preserved(self):
        source = "سے api درآمد اگر بطور condition, واپس بطور result\n"
        self.assertEqual(translate(source), "from api import اگر as condition, واپس as result\n")
        compile_urdu(source)

    def test_keyword_shaped_module_paths_are_preserved(self):
        source = "درآمد اگر.واپس بطور library\nسے اگر.درآمد درآمد جھوٹ بطور false_value\n"
        self.assertEqual(
            translate(source),
            "import اگر.واپس as library\nfrom اگر.درآمد import جھوٹ as false_value\n",
        )
        compile_urdu(source)

    def test_reserved_import_binding_requires_nonreserved_alias(self):
        for source in ("from api import اگر\n", "درآمد اگر\n", "from api import x as سچ\n"):
            with self.subTest(source=source):
                with self.assertRaisesRegex(ExperimentalSyntaxError, "reserved.*alias"):
                    compile_urdu(source)

    def test_relative_parenthesized_import_preserves_export_names(self):
        source = "سے .api درآمد (\n    اگر بطور condition, # واپس\n    واپس بطور result,\n)\n"
        expected = "from .api import (\n    اگر as condition, # واپس\n    واپس as result,\n)\n"
        self.assertEqual(translate(source), expected)
        compile_urdu(source)

    def test_relative_only_import_and_keyword_shaped_module(self):
        cases = (
            ("سے . درآمد thing\n", "from . import thing\n"),
            ("سے .. درآمد thing بطور value\n", "from .. import thing as value\n"),
            ("سے .درآمد درآمد thing\n", "from .درآمد import thing\n"),
            ("سے . درآمد درآمد بطور value\n", "from . import درآمد as value\n"),
            ("سے ... درآمد thing\n", "from ... import thing\n"),
        )
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(translate(source), expected)
                compile_urdu(source)

    def test_keyword_shaped_exports_resolve_to_actual_module_objects(self):
        fixture = ModuleType("urdupy_external_fixture")
        setattr(fixture, "اگر", object())
        setattr(fixture, "درآمد", object())
        source = (
            "سے urdupy_external_fixture درآمد اگر بطور condition, درآمد بطور imported_value\n"
            "درآمد urdupy_external_fixture بطور api\n"
            "result = (condition ہے api.اگر, imported_value ہے api.درآمد)\n"
        )
        with patch.dict(sys.modules, {fixture.__name__: fixture}):
            self.assertEqual(execute(source)["result"], (True, True))
        self.assertNotIn(fixture.__name__, sys.modules)

    def test_as_word_can_be_an_imported_export_or_module_name(self):
        source = "سے بطور درآمد بطور بطور alias\nدرآمد درآمد بطور module\n"
        self.assertEqual(translate(source), "from بطور import بطور as alias\nimport درآمد as module\n")
        compile_urdu(source)

    def test_raise_from_is_not_misread_as_import(self):
        source = "کوشش:\n    گزر\nسوائے Exception بطور error:\n    اٹھاؤ RuntimeError() سے error\n"
        self.assertEqual(
            translate(source),
            "try:\n    pass\nexcept Exception as error:\n    raise RuntimeError() from error\n",
        )
        compile_urdu(source)

    def test_inline_and_semicolon_imports(self):
        source = "اگر سچ: درآمد math بطور m; result = m.sqrt(9)\n"
        self.assertEqual(execute(source)["result"], 3.0)

    def test_english_star_import_stays_unchanged(self):
        source = "from math import *\nresult = sqrt(16)\n"
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], 4.0)

    def test_normal_fstrings_are_opaque_and_execute(self):
        source = (
            "value = 4\n"
            "a = f'اگر {value!r:>3} {{واپس}}'\n"
            "b = rf'ورنہ\\n{value}'\n"
            'c = f"""فنکشن\n{value:{2}}\n"""\n'
        )
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["a"], "اگر   4 {واپس}")

    def test_reserved_urdu_fstring_expression_is_explicitly_rejected(self):
        for source in ("x = f'{سچ}'\n", "x = f'{1 اگر سچ else 2}'\n", "x = f'{سچ=}'\n"):
            with self.subTest(source=source):
                with self.assertRaisesRegex(ExperimentalSyntaxError, "f-string.*Python-only"):
                    translate(source)

    def test_fstring_attribute_and_keyword_labels_are_allowed(self):
        source = (
            "from types import SimpleNamespace\n"
            "obj = SimpleNamespace(**{'اگر': 7})\n"
            "def api(**kwargs): return kwargs['واپس']\n"
            "result = f'{obj.اگر}:{api(واپس=3)}'\n"
        )
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], "7:3")

    def test_fstring_urdu_inside_embedded_python_string_is_allowed(self):
        source = 'result = f"{len(\'اگر واپس\')}"\n'
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], "8")

    def test_nested_fstring_is_unchanged(self):
        source = 'x = 3\nresult = f"{f\'{x}\'}"\n'
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], "3")

    def test_nested_fstring_reserved_expression_is_rejected(self):
        with self.assertRaisesRegex(ExperimentalSyntaxError, "f-string.*Python-only"):
            translate('x = f"{f\'{سچ}\'}"\n')

    def test_host_fstring_grammar_is_not_extended(self):
        source = 'x = "ok"\nresult = f"{x.replace("o", "O")}"\n'
        if sys.version_info >= (3, 12):
            self.assertEqual(translate(source), source)
            self.assertEqual(execute(source)["result"], "Ok")
        else:
            with self.assertRaises(SyntaxError):
                compile_urdu(source)

    def test_lambda_parameter_cannot_bypass_reserved_name_rule(self):
        source = "result = list(map(lambda اگر=1: 2, []))\n"
        with self.assertRaises(SyntaxError):
            compile_urdu(source)

    def test_compile_never_executes_imports_or_program(self):
        source = "درآمد module_that_does_not_exist_urdupy_probe\nاٹھاؤ RuntimeError('never run')\n"
        code = compile_urdu(source, "check-only.urdu")
        self.assertEqual(code.co_filename, "check-only.urdu")

    def test_runtime_filename_and_line_are_preserved(self):
        source = "اگر سچ:\n    result = 1 / 0\n"
        try:
            execute(source, "original.urdu")
        except ZeroDivisionError as error:
            frame = traceback.extract_tb(error.__traceback__)[-1]
            self.assertEqual((frame.filename, frame.lineno), ("original.urdu", 2))
        else:
            self.fail("expected normal CPython ZeroDivisionError")

    def test_syntax_error_retains_filename_and_line(self):
        with self.assertRaises(SyntaxError) as caught:
            compile_urdu("اگر سچ:\n    واپس (\n", "syntax.urdu")
        self.assertEqual(caught.exception.filename, "syntax.urdu")
        self.assertIn(caught.exception.lineno, (2, 3))

    def test_reserved_local_name_is_not_silently_allowed(self):
        for source in ("اگر = 2\n", "فنکشن f(واپس=1): گزر\n"):
            with self.subTest(source=source):
                with self.assertRaises(SyntaxError):
                    compile_urdu(source)

    def test_aliases_remain_names_and_can_be_shadowed(self):
        source = "دکھاؤ = lambda x: x + 1\nresult = دکھاؤ(3)\n"
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], 4)

    def test_no_unicode_lookalike_correction(self):
        source = "كلاس = 1\nresult = كلاس\n"
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], 1)

    def test_unicode_line_separator_inside_literal_does_not_shift_spans(self):
        source = "text = 'اگر\u2028واپس'\nاگر سچ: result = 4\n"
        result = translate_with_spans(source)
        self.assertEqual(execute(source)["result"], 4)
        for edit in result.edits:
            self.assertEqual(source[edit.original_start:edit.original_end], edit.original)
            self.assertEqual(edit.line, 2)

    def test_bom_first_line_span_column_counts_original_characters(self):
        result = translate_with_spans("\ufeffاگر سچ: گزر\n")
        self.assertEqual(result.edits[0].original_start, 1)
        self.assertEqual(result.edits[0].column, 1)

    def test_invalid_format_character_is_not_silently_removed(self):
        source = "x\u200b = 1\n"
        self.assertEqual(translate(source), source)
        with self.assertRaises(SyntaxError):
            compile_urdu(source)

    def test_blind_name_substitution_corrupts_three_api_contexts(self):
        # Deliberate negative comparator, never the implementation strategy.
        import tokenize
        for source in ("from api import اگر as condition\n", "obj.واپس\n", "api(سچ=1)\n"):
            with self.subTest(source=source):
                naive = tokenize.untokenize(
                    token._replace(string=KEYWORDS.get(token.string, token.string))
                    if token.type == tokenize.NAME else token
                    for token in tokenize.generate_tokens(io.StringIO(source).readline)
                )
                with self.assertRaises(SyntaxError):
                    compile(naive, "blind.py", "exec")
                self.assertEqual(translate(source), source)
                compile_urdu(source)

    def test_stdout_matches_real_builtin_alias(self):
        output = io.StringIO()
        with redirect_stdout(output):
            execute("دکھاؤ('سلام', 3)\n")
        self.assertEqual(output.getvalue(), "سلام 3\n")

    def test_translation_is_deterministic(self):
        source = "اگر سچ:\n    گزر # اگر\n"
        self.assertEqual(translate_with_spans(source), translate_with_spans(source))

    def test_source_must_be_text(self):
        with self.assertRaises(TypeError):
            translate(b"pass")


if __name__ == "__main__":
    unittest.main()
