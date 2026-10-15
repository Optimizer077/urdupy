"""Standalone Urdu application surface and reproducible public result contracts."""

import csv
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

from urdupy import compile_urdu

ROOT = Path(__file__).resolve().parents[1]


class StandaloneUrduContract(unittest.TestCase):
    def test_readme_application_snippets_need_no_english_code_or_embedding(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        snippets = re.findall(r"```(?:python|urdu)\n(.*?)```", readme, re.S)
        self.assertGreaterEqual(len(snippets), 5)
        for source in snippets:
            with self.subTest(source=source[:60]):
                self.assertIsNone(re.search(r"[A-Za-z]", source))
                compile_urdu(source)
        self.assertNotIn("from urdupy import", readme)
        self.assertNotIn("execute_source(", readme)

    def test_all_complete_urdu_sources_are_executable_without_latin_letters(self):
        sources = sorted((ROOT / "examples" / "مکمل_اردو").rglob("*.urdu"))
        self.assertGreaterEqual(len(sources), 15)
        for path in sources:
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIsNone(re.search(r"[A-Za-z]", source))
                compile_urdu(source, str(path))

    def test_standalone_urdu_imports_run_from_the_cli(self):
        path = ROOT / "examples" / "مکمل_اردو" / "آزاد_پروگرام.urdu"
        result = subprocess.run([sys.executable, "-X", "utf8", "-m", "urdupy", "چلاؤ", str(path)],
                                cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "7\n")

    def test_public_result_snapshot_reconciles_all_counts_and_epochs(self):
        folder = ROOT / "docs" / "نتائج" / "ریسنیٹ"
        summary = json.loads((folder / "خلاصہ.json").read_text(encoding="utf-8"))
        matrix = summary["الجھاؤ_جدول"]
        self.assertEqual(len(matrix), 10)
        self.assertTrue(all(len(row) == 10 and sum(row) == 800 for row in matrix))
        self.assertEqual(sum(matrix[i][i] for i in range(10)), summary["آزمائشی_درست"])
        self.assertEqual(summary["آزمائشی_درست"] / summary["آزمائشی_تعداد"], summary["آزمائشی_درستگی"])
        rows = list(csv.DictReader(io.StringIO((folder / "تربیتی_تاریخ.csv").read_text(encoding="utf-8-sig"))))
        self.assertEqual([int(row["دور"]) for row in rows], list(range(1, 51)))
        best = max(rows, key=lambda row: float(row["توثیقی_درستگی"]))
        self.assertEqual(int(best["دور"]), summary["بہترین_دور"])
        self.assertEqual(float(best["توثیقی_درستگی"]), summary["بہترین_توثیقی_درستگی"])
        import hashlib
        for artifact in summary["خاکے"]:
            path = folder / artifact["فائل"]
            self.assertEqual(path.stat().st_size, artifact["بائٹ"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), artifact["شا۲۵۶"])


if __name__ == "__main__":
    unittest.main()
