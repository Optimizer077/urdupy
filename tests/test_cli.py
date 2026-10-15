from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import linecache
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from urdupy.cli import main
from urdupy.repl import UrduConsole


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def invoke(self, *args, input=None):
        return subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "urdupy", *map(str, args)],
            cwd=ROOT, input=input, capture_output=True, text=True, encoding="utf-8",
            timeout=30,
        )

    def test_help_version_and_no_command(self):
        self.assertEqual(self.invoke("--help").returncode, 0)
        self.assertIn("UrduPy 0.1.0a1", self.invoke("--version").stdout)
        self.assertEqual(self.invoke().returncode, 2)

    def test_run_unicode_stdout_and_argument_separator(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "script.urdu"
            path.write_text("import sys\nدکھاؤ('سلام', sys.argv[1:])\n", encoding="utf-8")
            result = self.invoke("run", path, "--", "one", "--two")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "سلام ['one', '--two']\n")

    def test_check_does_not_execute_source_or_imports_and_handles_multiple(self):
        with TemporaryDirectory() as directory:
            first, second = Path(directory) / "first.urdu", Path(directory) / "second.urdu"
            first.write_text("درآمد missing_module_check_only_urdupy\nاٹھاؤ RuntimeError\n", encoding="utf-8")
            second.write_text("فنکشن f():\n    واپس 7\n", encoding="utf-8")
            result = self.invoke("check", first, second)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.count("OK "), 2)

    def test_check_reports_original_syntax_and_nonzero_status(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "bad.urdu"
            path.write_text("اگر سچ\n    گزر\n", encoding="utf-8")
            result = self.invoke("check", path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("SyntaxError", result.stderr)
            self.assertIn("اگر سچ", result.stderr)
            self.assertIn(str(path), result.stderr)

    def test_translate_output_is_intermediate_and_preserves_data(self):
        with TemporaryDirectory() as directory:
            path, output = Path(directory) / "source.urdu", Path(directory) / "out.py"
            path.write_text("اگر سچ:\n    دکھاؤ('اگر') # واپس\n", encoding="utf-8")
            result = self.invoke("translate", path, "-o", output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), "if True:\n    دکھاؤ('اگر') # واپس\n")
            self.assertIn("Intermediate Python", result.stderr)
            self.assertEqual(self.invoke("translate", path, "-o", path).returncode, 2)

    def test_exit_statuses_match_python(self):
        for statement, code, message in (
            ("raise SystemExit(7)", 7, None),
            ("raise SystemExit('finished')", 1, "finished"),
            ("raise KeyboardInterrupt", 130, "KeyboardInterrupt"),
            ("raise SystemExit", 0, None),
        ):
            with self.subTest(statement=statement), TemporaryDirectory() as directory:
                path = Path(directory) / "exit.urdu"
                path.write_text(statement, encoding="utf-8")
                result = self.invoke("run", path)
                self.assertEqual(result.returncode, code, result.stderr)
                if message:
                    self.assertIn(message, result.stderr)

    def test_runtime_error_traceback_uses_original_source(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "error.urdu"
            path.write_text("اگر سچ:\n    جواب = 1 / 0\n", encoding="utf-8")
            result = self.invoke("run", path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("جواب = 1 / 0", result.stderr)
            self.assertIn("ZeroDivisionError", result.stderr)

    def test_missing_file_is_a_failure(self):
        result = self.invoke("run", "missing-file-urdupy-test.urdu")
        self.assertEqual(result.returncode, 1)
        self.assertIn("FileNotFoundError", result.stderr)

    def test_main_callable_returns_status_and_restores_stream_encoding(self):
        output, error = StringIO(), StringIO()
        with redirect_stdout(output), redirect_stderr(error):
            self.assertEqual(main(["check", "examples/01_conditions.urdu"]), 0)
        self.assertIn("OK ", output.getvalue())

    def test_repl_piped_multiline_and_expressions(self):
        result = self.invoke("repl", input="فنکشن مربع(عدد):\n    واپس عدد * عدد\n\nمربع(4)\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("16", result.stdout)
        self.assertNotIn("SyntaxError", result.stderr)


class ConsoleTests(unittest.TestCase):
    def test_multiline_function_and_parentheses(self):
        with UrduConsole() as console:
            self.assertTrue(console.push("فنکشن جمع(x):"))
            self.assertTrue(console.push("    واپس x + 1"))
            self.assertFalse(console.push(""))
            self.assertTrue(console.push("result = ("))
            self.assertFalse(console.push("جمع(4))"))
            self.assertEqual(console.locals["result"], 5)

    def test_future_annotations_persist_between_inputs(self):
        with UrduConsole() as console:
            console.push("from __future__ import annotations")
            console.push("فنکشن f(x: Missing): واپس x")
            console.push("")
            self.assertEqual(console.locals["f"].__annotations__, {"x": "Missing"})

    def test_previous_definition_source_retained_until_console_close(self):
        error = StringIO()
        with UrduConsole() as console, redirect_stderr(error):
            console.push("فنکشن broken():")
            console.push("    واپس 1 / 0")
            console.push("")
            filename = console.locals["broken"].__code__.co_filename
            console.push("broken()")
            self.assertIn("واپس 1 / 0", error.getvalue())
            self.assertIn(filename, linecache.cache)
        self.assertNotIn(filename, linecache.cache)

    def test_syntax_error_does_not_poison_next_input(self):
        error = StringIO()
        with UrduConsole() as console, redirect_stderr(error):
            self.assertFalse(console.push("اگر سچ"))
            self.assertFalse(console.push("answer = 42"))
            self.assertEqual(console.locals["answer"], 42)
        self.assertIn("SyntaxError", error.getvalue())

    def test_multiple_consoles_do_not_overwrite_prior_function_source(self):
        error = StringIO()
        with UrduConsole() as first, UrduConsole() as second, redirect_stderr(error):
            first.push("فنکشن original():")
            first.push("    واپس 1 / 0")
            first.push("")
            filename = first.locals["original"].__code__.co_filename
            second.push("other = 42")
            self.assertIn("واپس 1 / 0", linecache.getline(filename, 2))
            first.push("original()")
            self.assertIn("واپس 1 / 0", error.getvalue())


if __name__ == "__main__":
    unittest.main()
