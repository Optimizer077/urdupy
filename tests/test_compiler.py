"""Production frontend behavior, differential values, and original locations."""

import ast
import asyncio
import builtins
import codeop
import io
import sys
import traceback
import unittest
from contextlib import redirect_stdout
from types import ModuleType
from unittest.mock import patch

from urdupy.compiler import compile_urdu, parse_urdu, translate, translate_with_map
from urdupy.lexicon import BUILTIN_ALIASES


def namespace():
    aliases = vars(builtins).copy()
    aliases.update({word: getattr(builtins, name) for word, name in BUILTIN_ALIASES.items()})
    return {"__builtins__": aliases}


def execute(source, filename="compiler.urdu"):
    values = namespace()
    exec(compile_urdu(source, filename), values)
    return values


@unittest.skipIf(sys.version_info < (3, 12), "production requires CPython 3.12+")
class CompilerTests(unittest.TestCase):
    def test_core_control_flow_and_functions(self):
        source = (
            "فنکشن مربع(x):\n"
            "    اگر x < 0:\n"
            "        واپس کچھ_نہیں\n"
            "    ورنہ_اگر x ہے کچھ_نہیں:\n"
            "        واپس جھوٹ\n"
            "    ورنہ:\n"
            "        واپس x * x\n"
            "result = [مربع(x) ہر x میں حد(-1, 4)]\n"
        )
        self.assertEqual(execute(source)["result"], [None, 0, 1, 4, 9])

    def test_decorators_parameter_markers_annotations_and_kwargs(self):
        source = (
            "فنکشن twice(fn):\n"
            "    واپس لامبڈا *args, **kwargs: fn(*args, **kwargs) * 2\n"
            "@twice\n"
            "فنکشن add(x: int, /, y=2, *, factor=3):\n"
            "    واپس (x + y) * factor\n"
            "result = add(4, factor=2)\n"
        )
        self.assertEqual(execute(source)["result"], 24)

    def test_comprehensions_generators_walrus_and_loop_else(self):
        source = (
            "values = {x: x*x ہر x میں حد(5) اگر x % 2 == 0}\n"
            "فنکشن gen():\n"
            "    پیدا_کرو سے values.values()\n"
            "result = list(gen())\n"
            "ہر x میں [1]:\n"
            "    result.append(y := x + 9)\n"
            "ورنہ:\n"
            "    result.append(20)\n"
        )
        self.assertEqual(execute(source)["result"], [0, 4, 16, 10, 20])

    def test_async_await_and_async_for(self):
        source = (
            "درآمد asyncio\n"
            "غیر_متزامن فنکشن values():\n"
            "    ہر x میں حد(3):\n"
            "        انتظار asyncio.sleep(0)\n"
            "        پیدا_کرو x\n"
            "غیر_متزامن فنکشن calculate():\n"
            "    واپس [x غیر_متزامن ہر x میں values()]\n"
            "result = asyncio.run(calculate())\n"
        )
        self.assertEqual(execute(source)["result"], [0, 1, 2])

    def test_async_with_uses_real_context_protocols(self):
        source = (
            "درآمد asyncio\n"
            "سے contextlib درآمد asynccontextmanager\n"
            "@asynccontextmanager\n"
            "غیر_متزامن فنکشن resource():\n"
            "    پیدا_کرو 9\n"
            "غیر_متزامن فنکشن calculate():\n"
            "    غیر_متزامن ساتھ resource() بطور value:\n"
            "        واپس value\n"
            "result = asyncio.run(calculate())\n"
        )
        self.assertEqual(execute(source)["result"], 9)

    def test_exception_group_star_syntax(self):
        source = (
            "result = []\n"
            "کوشش:\n"
            "    اٹھاؤ ExceptionGroup('group', [ValueError('v'), TypeError('t')])\n"
            "سوائے* ValueError بطور error:\n"
            "    result.append(type(error.exceptions[0]).__name__)\n"
            "سوائے* TypeError بطور error:\n"
            "    result.append(type(error.exceptions[0]).__name__)\n"
        )
        self.assertEqual(execute(source)["result"], ["ValueError", "TypeError"])

    def test_scopes_regular_context_and_loop_control(self):
        source = (
            "سے contextlib درآمد nullcontext\n"
            "x = 0\n"
            "فنکشن outer():\n"
            "    y = 1\n"
            "    فنکشن change():\n"
            "        عالمی x\n"
            "        غیر_مقامی y\n"
            "        x = 3\n"
            "        y = 4\n"
            "    change()\n"
            "    واپس y\n"
            "کلاس Box:\n"
            "    گزر\n"
            "result = []\n"
            "ساتھ nullcontext(outer()) بطور value:\n"
            "    result.extend([value, x, Box.__name__])\n"
            "count = 0\n"
            "جب_تک سچ:\n"
            "    count += 1\n"
            "    اگر count == 1: جاری\n"
            "    result.append(count)\n"
            "    روکو\n"
            "temporary = 1\n"
            "حذف temporary\n"
            "تصدیق نہیں جھوٹ اور سچ یا جھوٹ\n"
        )
        values = execute(source)
        self.assertEqual(values["result"], [4, 3, "Box", 2])
        self.assertNotIn("temporary", values)

    def test_english_python_stays_exact_including_soft_names(self):
        source = (
            "import math\nmatch = 1\ncase = 2\ntype_name = type(3)\n"
            "type Pair = tuple[int, int]\n"
            "def f[T](x: T, /, *, factor=2):\n    return x * factor\n"
            "result = f(math.sqrt(9))\n"
            "match result:\n    case 6.0:\n        result += case\n"
        )
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], 8)

    def test_soft_urdu_words_remain_regular_identifiers(self):
        source = "منتخب = 2\nصورت: int = 3\nresult = منتخب + صورت\n"
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], 5)

    def test_contextual_match_case_with_capture_guard_and_nested_match(self):
        source = (
            "منتخب = 'ordinary'\n"
            "صورت = 9\n"
            "value = {'x': [2, 3]}\n"
            "منتخب value:\n"
            "    صورت {'x': [first, *rest]} اگر first > 0:\n"
            "        منتخب rest:\n"
            "            صورت [last]:\n"
            "                result = (first, last, منتخب, صورت)\n"
            "    صورت _:\n"
            "        result = کچھ_نہیں\n"
        )
        self.assertEqual(execute(source)["result"], (2, 3, "ordinary", 9))

    def test_mixed_english_match_and_urdu_case(self):
        source = "match 3:\n    صورت 3: result = سچ\n    صورت _: result = جھوٹ\n"
        self.assertTrue(execute(source)["result"])

    def test_case_word_inside_case_body_is_an_identifier(self):
        source = "منتخب 1:\n    صورت 1:\n        صورت = 7\n        result = صورت\n"
        self.assertEqual(execute(source)["result"], 7)

    def test_class_pattern_preserves_keyword_shaped_attributes(self):
        source = (
            "class Box: pass\n"
            "box = Box()\n"
            "setattr(box, 'اگر', 7)\n"
            "منتخب box:\n"
            "    صورت Box(اگر=value): result = value\n"
            "    صورت _: result = کچھ_نہیں\n"
        )
        self.assertEqual(execute(source)["result"], 7)

    def test_type_parameter_bound_calls_preserve_unicode_api_labels(self):
        source = (
            "def bound(**kwargs): return int\n"
            "فنکشن identity[T: bound(اگر=1)](x: T):\n"
            "    واپس x\n"
            "result = (identity(7), identity.__type_params__[0].__bound__)\n"
        )
        self.assertEqual(execute(source)["result"], (7, int))

    def test_strings_comments_raw_and_multiline_remain_exact(self):
        source = (
            "# اگر فنکشن واپس\r\n"
            "a = r'اگر\\nواپس'\r\n"
            "b = '''سچ\r\nجھوٹ\r\n'''\r\n"
            'c = "اگر\u2028واپس"\r\n'
        )
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["b"], "سچ\nجھوٹ\n")

    def test_newline_styles_bom_tabs_and_missing_final_newline(self):
        for newline in ("\n", "\r\n", "\r"):
            with self.subTest(newline=repr(newline)):
                source = "\ufeffاگر سچ:" + newline + "\tresult = 7"
                self.assertEqual(translate(source), "\ufeffif True:" + newline + "\tresult = 7")
                self.assertEqual(execute(source)["result"], 7)

    def test_real_python_export_attribute_and_unicode_keyword_label(self):
        api = ModuleType("_urdupy_compiler_api")
        setattr(api, "اگر", lambda **kw: kw["واپس"])
        source = (
            "سے _urdupy_compiler_api درآمد اگر بطور condition\n"
            "درآمد _urdupy_compiler_api بطور api\n"
            "result = (condition(واپس=سچ), api.اگر(واپس=3))\n"
        )
        with patch.dict(sys.modules, {api.__name__: api}):
            self.assertEqual(execute(source)["result"], (True, 3))
        self.assertNotIn(api.__name__, sys.modules)

    def test_relative_imports_and_keyword_shaped_modules(self):
        cases = (
            ("سے . درآمد thing\n", "from . import thing\n"),
            ("سے .. درآمد thing بطور value\n", "from .. import thing as value\n"),
            ("سے .درآمد درآمد thing\n", "from .درآمد import thing\n"),
            ("سے . درآمد درآمد بطور value\n", "from . import درآمد as value\n"),
            ("درآمد اگر.بطور بطور api\n", "import اگر.بطور as api\n"),
        )
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(translate(source), expected)
                compile_urdu(source)

    def test_import_bindings_that_collide_require_aliases(self):
        for source in ("from api import اگر\n", "درآمد اگر\n", "from api import x as انتظار\n"):
            with self.subTest(source=source):
                with self.assertRaisesRegex(SyntaxError, "reserved.*alias") as caught:
                    compile_urdu(source, "binding.urdu")
                self.assertEqual(caught.exception.filename, "binding.urdu")
                self.assertEqual(caught.exception.text, source)

    def test_nested_call_labels_and_reserved_parameter_rejection(self):
        source = "def api(**kw): return kw\nresult = (api)(اگر=api(واپس=سچ))\n"
        self.assertEqual(execute(source)["result"], {"اگر": {"واپس": True}})
        with self.assertRaises(SyntaxError):
            compile_urdu("result = list(map(lambda اگر=1: 2, []))\n")

    def test_raise_from_and_inline_imports(self):
        source = (
            "اگر سچ: درآمد math بطور m; result = m.sqrt(9)\n"
            "کوشش:\n    گزر\nسوائے Exception بطور error:\n"
            "    اٹھاؤ RuntimeError() سے error\n"
        )
        self.assertEqual(execute(source)["result"], 3)

    def test_fstring_urdu_condition_expressions_and_literal_portions(self):
        source = 'result = f"اگر {1 اگر سچ ورنہ 2}: {{واپس}}"\n'
        self.assertEqual(execute(source)["result"], "اگر 1: {واپس}")
        self.assertIn("اگر ", translate(source))
        self.assertIn("{{واپس}}", translate(source))

    def test_fstring_attributes_keyword_labels_and_embedded_strings(self):
        source = (
            "from types import SimpleNamespace\n"
            "obj = SimpleNamespace(**{'اگر': 7})\n"
            "def api(**kwargs): return kwargs['واپس']\n"
            'result = f"{obj.اگر}:{api(واپس=سچ)}:{len(\'اگر واپس\')}"\n'
        )
        self.assertEqual(execute(source)["result"], "7:True:8")

    def test_nested_fstring_urdu_expressions(self):
        source = 'result = f"outer {f\'inner {سچ}\'}"\n'
        self.assertEqual(execute(source)["result"], "outer inner True")

    def test_nested_format_fields_and_conversion(self):
        source = 'result = f"{7!r:>{3 اگر سچ ورنہ 1}}"\n'
        self.assertEqual(execute(source)["result"], "  7")

    def test_python_fstrings_without_urdu_syntax_are_exact(self):
        source = 'x = 3\nresult = rf"اگر {x= !r:>3} {{واپس}}"\n'
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], "اگر x=   3 {واپس}")

    def test_fstring_debug_preserves_original_expression_label(self):
        source = 'result = f"{سچ=}"\n'
        self.assertEqual(execute(source)["result"], "سچ=True")
        plain = namespace()
        exec(translate(source), plain)
        self.assertEqual(plain["result"], "سچ=True")

    def test_debug_whitespace_format_and_conversion_are_preserved(self):
        cases = (
            ('result = f"{ سچ = }"\n', " سچ = True"),
            ('result = f"{سچ= !s}"\n', "سچ= True"),
            ('result = f"{سچ=:>6}"\n', "سچ=     1"),
            ('result = f"{سچ=!a}"\n', "سچ=True"),
        )
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(execute(source)["result"], expected)
                plain = namespace()
                exec(translate(source), plain)
                self.assertEqual(plain["result"], expected)

    def test_debug_nested_quotes_raw_and_nested_fstrings(self):
        cases = (
            ('result = rf"{سچ=}"\n', "سچ=True"),
            ('result = f"{ {\'key\': سچ} = }"\n', " {'key': سچ} = {'key': True}"),
            ('result = f"{f\'{سچ}\'=}"\n', "f'{سچ}'='True'"),
        )
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(execute(source)["result"], expected)

    def test_fstring_comments_and_quote_reuse_on_supported_minors(self):
        source = 'x = "ok"\nresult = f"{x.replace("o", "O") if سچ else x # اگر\n}"\n'
        self.assertEqual(execute(source)["result"], "Ok")
        self.assertIn("# اگر\n", translate(source))

    def test_debug_field_with_multiline_comment_preserves_native_label(self):
        source = 'result = f"{سچ = # original\n}"\n'
        self.assertEqual(execute(source)["result"], "سچ = \nTrue")

    def test_debug_label_newlines_and_comments_match_native_cpython(self):
        sources = [
            'result = f"{سچ = # original\n}"\n',
            'result = f"{(سچ # expression\n) = # trailing\n}"\n',
            'result = f"{f\'{سچ # nested\n}\'=}"\n',
            'result = f"{(\'a#b\', سچ)=}"\n',
        ]
        if sys.version_info >= (3, 14):
            sources.append('result = f"{(سچ, t\'{value # nested\n}\')=}"\n')
        for newline in ("\n", "\r\n", "\r"):
            for sample in sources:
                source = sample.replace("\n", newline)
                with self.subTest(newline=repr(newline), source=source):
                    native = {"سچ": True, "value": 7}
                    exec(compile(source, "native.py", "exec", dont_inherit=True), native)
                    translated = {"value": 7}
                    exec(compile_urdu(source), translated)
                    intermediate = {"value": 7}
                    exec(compile(translate(source), "intermediate.py", "exec", dont_inherit=True), intermediate)
                    self.assertEqual(translated["result"], native["result"])
                    self.assertEqual(intermediate["result"], native["result"])

    def test_exec_eval_and_single_modes(self):
        self.assertEqual(eval(compile_urdu("سچ اور نہیں جھوٹ", mode="eval")), True)
        output = io.StringIO()
        with redirect_stdout(output):
            exec(compile_urdu("1 + 2", mode="single"), {})
        self.assertEqual(output.getvalue(), "3\n")

    def test_compile_flags_ast_and_top_level_await(self):
        tree = compile_urdu("x = سچ\n", flags=ast.PyCF_ONLY_AST)
        self.assertIsInstance(tree, ast.Module)
        code = compile_urdu("انتظار task()", mode="eval", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
        async def task():
            return 12
        self.assertEqual(asyncio.run(eval(code, {"task": task})), 12)

    def test_codeop_flags_support_incomplete_input(self):
        flags = codeop.PyCF_ALLOW_INCOMPLETE_INPUT | codeop.PyCF_DONT_IMPLY_DEDENT
        for source in ("اگر سچ:\n", "x = (\n", 'result = f"{سچ'):
            with self.subTest(source=source):
                with self.assertRaisesRegex(SyntaxError, "incomplete input"):
                    compile_urdu(source, flags=flags)

    def test_compile_and_parse_do_not_execute_imports(self):
        source = "درآمد _urdupy_nonexistent_compile_probe\nاٹھاؤ RuntimeError('never')\n"
        self.assertIsInstance(parse_urdu(source), ast.Module)
        self.assertEqual(compile_urdu(source, "check.urdu").co_filename, "check.urdu")

    def test_syntax_error_text_start_and_end_map_to_original(self):
        source = "اگر سچ: نام = (1 + )\n"
        with self.assertRaises(SyntaxError) as caught:
            compile_urdu(source, "original.urdu")
        error = caught.exception
        self.assertEqual((error.filename, error.lineno, error.text), ("original.urdu", 1, source))
        self.assertEqual(error.offset, source.index(")") + 1)
        self.assertEqual(error.end_offset, source.index(")") + 2)

    def test_missing_colon_maps_end_of_changed_token(self):
        source = "اگر سچ\n    گزر\n"
        with self.assertRaises(SyntaxError) as caught:
            compile_urdu(source)
        self.assertEqual(caught.exception.text, "اگر سچ\n")
        self.assertEqual(caught.exception.offset, len("اگر سچ") + 1)

    def test_semantic_ast_error_uses_original_unicode_character_columns(self):
        source = "نام = 1; واپس 2\n"
        with self.assertRaisesRegex(SyntaxError, "outside function") as caught:
            compile_urdu(source, "semantic.urdu")
        error = caught.exception
        self.assertEqual(error.text, source)
        self.assertEqual(error.offset, source.index("واپس") + 1)
        self.assertEqual(error.end_offset, len(source.rstrip()) + 1)

    def test_unicode_ast_byte_spans_point_into_original_source(self):
        source = "اگر سچ: نتیجہ = 1 / 0\n"
        tree = parse_urdu(source)
        expression = next(node for node in ast.walk(tree) if isinstance(node, ast.BinOp))
        encoded = source.encode("utf-8")
        self.assertEqual(encoded[expression.col_offset:expression.end_col_offset].decode("utf-8"), "1 / 0")

    def test_runtime_instruction_span_points_into_original_source(self):
        source = "اگر سچ: نتیجہ = 1 / 0\n"
        try:
            execute(source, "runtime.urdu")
        except ZeroDivisionError as error:
            frame = traceback.extract_tb(error.__traceback__)[-1]
            self.assertEqual((frame.filename, frame.lineno), ("runtime.urdu", 1))
            encoded = source.encode("utf-8")
            self.assertEqual(encoded[frame.colno:frame.end_colno].decode("utf-8"), "1 / 0")
        else:
            self.fail("expected ZeroDivisionError")

    def test_runtime_span_after_debug_label_insertion(self):
        source = 'result = f"{(1 اگر سچ ورنہ 2) / 0 = }"\n'
        try:
            execute(source)
        except ZeroDivisionError as error:
            frame = traceback.extract_tb(error.__traceback__)[-1]
            self.assertEqual(
                source.encode("utf-8")[frame.colno:frame.end_colno].decode("utf-8"),
                "(1 اگر سچ ورنہ 2) / 0",
            )
        else:
            self.fail("expected ZeroDivisionError")

    def test_multiline_debug_rewrite_maps_following_runtime_line(self):
        source = 'value = f"{سچ = # original\n}"\nresult = 1 / 0\n'
        try:
            execute(source, "multiline.urdu")
        except ZeroDivisionError as error:
            frame = traceback.extract_tb(error.__traceback__)[-1]
            self.assertEqual((frame.filename, frame.lineno), ("multiline.urdu", 3))
            encoded = source.split("\n")[2].encode("utf-8")
            self.assertEqual(encoded[frame.colno:frame.end_colno].decode("utf-8"), "1 / 0")
        else:
            self.fail("expected ZeroDivisionError")

    def test_multiline_debug_rewrite_maps_following_syntax_line(self):
        source = 'value = f"{سچ = # original\n}"\nresult = )\n'
        with self.assertRaises(SyntaxError) as caught:
            compile_urdu(source, "multiline.urdu")
        error = caught.exception
        self.assertEqual((error.filename, error.lineno, error.text), ("multiline.urdu", 3, "result = )\n"))
        self.assertEqual(error.offset, len("result = ") + 1)

    def test_syntax_error_after_debug_insertion_maps_exactly(self):
        source = 'result = f"{سچ=}" + )\n'
        with self.assertRaises(SyntaxError) as caught:
            compile_urdu(source)
        self.assertEqual(caught.exception.text, source)
        self.assertEqual(caught.exception.offset, source.index(")") + 1)

    def test_replacement_ranges_and_unchanged_gaps(self):
        source = "\ufeffاگر سچ:\r\n\tresult = f'{سچ=}' # واپس\r\n"
        mapping = translate_with_map(source, "spans.urdu")
        self.assertEqual((mapping.source, mapping.filename), (source, "spans.urdu"))
        original = translated = 0
        for edit in mapping.edits:
            self.assertEqual(source[edit.original_start:edit.original_end], edit.original)
            self.assertEqual(mapping.text[edit.translated_start:edit.translated_end], edit.replacement)
            self.assertEqual(source[original:edit.original_start], mapping.text[translated:edit.translated_start])
            original, translated = edit.original_end, edit.translated_end
        self.assertEqual(source[original:], mapping.text[translated:])
        self.assertEqual(mapping.map_position(1, 0), (1, 0))

    def test_deleted_debug_marker_preserves_both_neighbor_boundaries(self):
        source = 'result = f"{سچ=:>6}"\n'
        mapping = translate_with_map(source)
        translated_colon = mapping.text.index(":")
        self.assertEqual(mapping.map_position(1, translated_colon), (1, source.index(":")))
        self.assertEqual(mapping.map_position(1, translated_colon, end=True), (1, source.index("=" , source.index("{"))))
        tree = parse_urdu(source)
        true = next(node for node in ast.walk(tree) if isinstance(node, ast.Constant) and node.value is True)
        self.assertEqual(
            source.encode("utf-8")[true.col_offset:true.end_col_offset].decode("utf-8"), "سچ"
        )

    def test_plain_and_urdu_identifiers_obey_cpython_normalization(self):
        source = "كلاس = 1\nresult = كلاس\n"
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], 1)

    def test_invalid_format_controls_are_not_removed(self):
        source = "x\u200b = 1\n"
        self.assertEqual(translate(source), source)
        with self.assertRaises(SyntaxError) as caught:
            compile_urdu(source)
        self.assertEqual(caught.exception.text, source)

    def test_native_template_strings_and_literal_urdu_are_unchanged(self):
        source = "value = 3\nresult = t'اگر {value=}'\n"
        self.assertEqual(translate(source), source)
        if sys.version_info >= (3, 14):
            result = execute(source)["result"]
            self.assertEqual(result.strings, ("اگر value=", ""))
            self.assertEqual(result.interpolations[0].expression, "value")
            self.assertEqual(result.interpolations[0].value, 3)
        else:
            with self.assertRaises(SyntaxError):
                compile_urdu(source)

    def test_template_urdu_expression_limit_is_explicit(self):
        if sys.version_info >= (3, 14):
            for source in ("result = t'{سچ}'\n", 'result = t"{f\'{سچ}\'}"\n'):
                with self.subTest(source=source):
                    with self.assertRaisesRegex(SyntaxError, "template-string.*not supported"):
                        compile_urdu(source)
        else:
            with self.assertRaises(SyntaxError):
                compile_urdu("result = t'{سچ}'\n")

    def test_english_lazy_imports_preserve_unicode_exports(self):
        source = "lazy from _api import اگر as condition\n"
        self.assertEqual(translate(source), source)
        if sys.version_info >= (3, 15):
            compile_urdu(source)
        else:
            with self.assertRaises(SyntaxError):
                compile_urdu(source)

    def test_flags_optimize_and_dont_inherit(self):
        code = compile_urdu("تصدیق جھوٹ\nresult = 5\n", optimize=1, dont_inherit=True)
        values = {}
        exec(code, values)
        self.assertEqual(values["result"], 5)

    def test_alias_names_are_not_rewritten(self):
        source = "دکھاؤ = lambda x: x + 1\nresult = دکھاؤ(3)\n"
        self.assertEqual(translate(source), source)
        self.assertEqual(execute(source)["result"], 4)


if __name__ == "__main__":
    unittest.main()
