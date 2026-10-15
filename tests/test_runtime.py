import builtins
from contextlib import redirect_stdout
from io import StringIO
import linecache
from pathlib import Path
import sys
import subprocess
from tempfile import TemporaryDirectory
import unittest

from urdupy.runtime import execute_source, format_exception, make_builtins, run_path


class RuntimeTests(unittest.TestCase):
    def test_alias_identity_and_no_implicit_exports(self):
        namespace = execute_source("RESULT = (دکھاؤ, حد, فہرست, قسم)\n")
        self.assertEqual(namespace["RESULT"], (print, range, list, type))
        self.assertNotIn("دکھاؤ", namespace)
        self.assertNotIn("دکھاؤ", vars(builtins))

    def test_shadow_delete_and_function_scope(self):
        namespace = execute_source(
            "original = دکھاؤ\n"
            "دکھاؤ = lambda x: x + 1\n"
            "first = دکھاؤ(4)\n"
            "حذف دکھاؤ\n"
            "فنکشن local(حد):\n    واپس حد(3)\n"
            "RESULT = (first, دکھاؤ ہے original, local(lambda x: x * 2))\n"
        )
        self.assertEqual(namespace["RESULT"], (5, True, 6))

    def test_assigned_local_does_not_fall_back_to_alias(self):
        with self.assertRaises(UnboundLocalError):
            execute_source("فنکشن f():\n    دکھاؤ('x')\n    دکھاؤ = 1\nf()\n")

    def test_custom_builtins_are_copied_without_filling_missing_capabilities(self):
        original = {"len": len}
        copied = make_builtins(original)
        self.assertIs(copied["لمبائی"], len)
        self.assertNotIn("print", copied)
        self.assertNotIn("دکھاؤ", copied)
        self.assertEqual(original, {"len": len})

    def test_supplied_namespace_and_ordinary_type_errors(self):
        namespace = {"factor": 3}
        self.assertIs(execute_source("RESULT = factor * 7", globals=namespace), namespace)
        self.assertEqual(namespace["RESULT"], 21)
        with self.assertRaises(TypeError):
            execute_source("گزر", globals=[])

    def test_alias_dicts_are_isolated(self):
        first, second = execute_source("گزر"), execute_source("گزر")
        first["__builtins__"]["حد"] = None
        self.assertIs(second["__builtins__"]["حد"], range)

    def test_nested_execution_in_a_worker_thread_can_finish_before_parent(self):
        namespace = execute_source(
            "from threading import Thread\n"
            "from urdupy import execute_source\n"
            "results = []\n"
            "def worker(): results.append(execute_source('RESULT = 7')['RESULT'])\n"
            "thread = Thread(target=worker)\n"
            "thread.start()\nthread.join(timeout=2)\n"
            "RESULT = (thread.is_alive(), results)\n"
        )
        self.assertEqual(namespace["RESULT"], (False, [7]))

    def test_anonymous_dataclass_has_real_definition_module_and_no_leak(self):
        before = set(sys.modules)
        namespace = execute_source(
            "from __future__ import annotations\n"
            "from dataclasses import dataclass\n"
            "@dataclass\nکلاس Point:\n    value: int\n"
            "RESULT = Point(7).value\n"
        )
        self.assertEqual(namespace["RESULT"], 7)
        self.assertNotIn(namespace["__name__"], sys.modules)
        self.assertFalse({name for name in set(sys.modules) - before if name.startswith("_urdupy_exec_")})

    def test_anonymous_execution_restores_a_preexisting_module_cache_entry(self):
        package_root = Path(sys.modules[execute_source.__module__].__file__).resolve().parent.parent
        result = subprocess.run(
            [sys.executable, "-I", "-c", (
                "import sys,types; sys.path.insert(0,sys.argv[1]); from urdupy import execute_source; "
                "previous=types.ModuleType('_urdupy_exec_1'); "
                "sys.modules[previous.__name__]=previous; "
                "execute_source('pass'); "
                "assert sys.modules.get(previous.__name__) is previous"
            ), str(package_root)], capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_original_virtual_source_is_captured_and_cache_restored(self):
        filename = "<runtime-original-source>"
        original = (3, None, ["old\n"], filename)
        linecache.cache[filename] = original
        meta = list(sys.meta_path)
        try:
            with self.assertRaises(ZeroDivisionError) as caught:
                execute_source("اگر سچ:\n    result = 1 / 0\n", filename)
            text = format_exception(caught.exception)
            self.assertIn("result = 1 / 0", text)
            self.assertIn(filename, text)
            self.assertIs(linecache.cache[filename], original)
            self.assertEqual(sys.meta_path, meta)
        finally:
            linecache.cache.pop(filename, None)

    def test_user_replacement_of_source_cache_is_not_erased(self):
        filename = "<runtime-owned-cache>"
        replacement = (1, None, ["new\n"], filename)
        try:
            execute_source(
                "import linecache\nlinecache.cache[__file__] = replacement\n",
                filename, {"replacement": replacement},
            )
            self.assertIs(linecache.cache[filename], replacement)
        finally:
            linecache.cache.pop(filename, None)

    def test_literal_unicode_separator_does_not_split_traceback_lines(self):
        for newline in ("\n", "\r\n", "\r"):
            with self.subTest(newline=repr(newline)):
                with self.assertRaises(ZeroDivisionError) as caught:
                    execute_source(f"text = 'a\u2028b'{newline}جواب = 1 / 0{newline}", "<unicode-separator>")
                self.assertIn("جواب = 1 / 0", format_exception(caught.exception))

    def test_script_main_argv_path_and_dataclass(self):
        old_argv, old_path, old_main = sys.argv, sys.path, sys.modules["__main__"]
        with TemporaryDirectory() as directory:
            path = Path(directory) / "حساب.urdu"
            path.write_text(
                "from __future__ import annotations\n"
                "import sys\nfrom dataclasses import dataclass\n"
                "@dataclass\nکلاس Item:\n    value: int\n"
                "RESULT = (__name__, sys.argv[:], sys.path[0], Item(3).value)\n",
                encoding="utf-8",
            )
            result = run_path(path, ["one", "--two"])["RESULT"]
            self.assertEqual(result, ("__main__", [str(path), "one", "--two"], directory, 3))
        self.assertIs(sys.argv, old_argv)
        self.assertIs(sys.path, old_path)
        self.assertIs(sys.modules["__main__"], old_main)

    def test_process_state_restores_for_exit_interrupt_error_and_syntax(self):
        for source, expected in (
            ("raise SystemExit(7)", SystemExit),
            ("raise KeyboardInterrupt", KeyboardInterrupt),
            ("raise RuntimeError('failure')", RuntimeError),
            ("اگر سچ", SyntaxError),
        ):
            with self.subTest(expected=expected), TemporaryDirectory() as directory:
                path = Path(directory) / "script.urdu"
                path.write_text(source, encoding="utf-8")
                argv, paths, main, meta = sys.argv, sys.path, sys.modules["__main__"], list(sys.meta_path)
                with self.assertRaises(expected):
                    run_path(path)
                self.assertIs(sys.argv, argv)
                self.assertIs(sys.path, paths)
                self.assertIs(sys.modules["__main__"], main)
                self.assertEqual(sys.meta_path, meta)

    def test_bom_crlf_and_real_builtin_output(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "bom.urdu"
            path.write_bytes("\ufeffاگر سچ:\r\n    دکھاؤ('سلام')\r\n".encode("utf-8"))
            output = StringIO()
            with redirect_stdout(output):
                run_path(path)
            self.assertEqual(output.getvalue(), "سلام\n")


if __name__ == "__main__":
    unittest.main()
