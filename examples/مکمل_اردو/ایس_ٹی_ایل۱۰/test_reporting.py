"""Offline reporting tests: controlled predictions, Urdu text and chart exports."""
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as XML
import numpy as np
from PIL import Image
from urdupy import execute_source
from urdupy import install_importer
from urdupy.urdu_catalog import canonical_name

HERE = Path(__file__).resolve().parent


def load(name):
    path = HERE / f"{name}.urdu"
    with patch.object(sys, "path", [str(HERE), *sys.path]):
        return execute_source(path.read_text(encoding="utf-8"), str(path))


def fixtures(images=True):
    history = [{"دور": n, "تربیتی_نقصان": 1.4-n*0.2, "تربیتی_درستگی": 0.25+n*0.15,
                "توثیقی_نقصان": 1.2-n*0.1, "توثیقی_درستگی": accuracy, "شرح": 0.05, "ثانیے": 0.1}
               for n, accuracy in enumerate([0.5, 0.75, 0.75], 1)]
    summary = {"تربیتی_تعداد": 12, "توثیقی_تعداد": 6, "آزمائشی_تعداد": 6, "بہترین_دور": 2,
               "بہترین_توثیقی_درستگی": 0.75, "آزمائشی_درستگی": 0.5, "آزمائشی_درست": 3,
               "آزمائشی_نقصان": 0.9, "دور": 3, "چوڑائی": 2, "جسامت": 16, "پیرامیٹر": 0,
               "جماعتیں": ["بلی", "کتا", "پرندہ"], "اوسط": [0.5]*3, "انحراف": [0.2]*3, "ثانیے": 0.3}
    predictions = {"اصل": [0, 0, 1, 1, 2, 2], "متوقع": [0, 1, 1, 2, 2, 0], "اعتماد": [0.8]*6}
    if images:
        predictions.update({"تصاویر": np.random.default_rng(42).integers(0, 256, (6, 3, 16, 16), dtype=np.uint8),
                            "نمونہ_اشاریے": list(range(6))})
    return history, summary, predictions


def save_fixture(directory, history, summary, predictions):
    for name, value in (("تاریخ", history), ("خلاصہ", summary), ("پیشگوئیاں", predictions)):
        (Path(directory)/f"{name}.json").write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


class ReportingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plot, cls.audit = load("خاکے"), load("جانچ")

    def test_zero_ascii_source_letters(self):
        for name in ("خاکے", "دوبارہ_خاکے", "جانچ"):
            self.assertIsNone(re.search("[A-Za-z]", (HERE/f"{name}.urdu").read_text(encoding="utf-8")))

    def test_independent_confusion_and_earliest_validation_tie(self):
        result = self.audit["حساب_جانچو"](*fixtures(False))
        self.assertEqual(result["الجھاؤ"], [[1, 1, 0], [0, 1, 1], [1, 0, 1]])
        self.assertEqual(result["بہترین_دور"], 2)
        self.assertEqual(result["آزمائشی_درستگی"], 0.5)

    def test_false_metrics_and_invalid_values_rejected(self):
        changes = [lambda h,s,p: s.update({"بہترین_دور": 3}),
                   lambda h,s,p: s.update({"آزمائشی_درستگی": 0.6}),
                   lambda h,s,p: s.update({"آزمائشی_درست": 4}),
                   lambda h,s,p: s.update({"آزمائشی_تعداد": 7}),
                   lambda h,s,p: p["اصل"].__setitem__(0, -1),
                   lambda h,s,p: p["متوقع"].__setitem__(0, True),
                   lambda h,s,p: p["اعتماد"].__setitem__(0, float("nan")),
                   lambda h,s,p: h[1].update({"دور": 1}),
                   lambda h,s,p: h[1].update({"توثیقی_درستگی": float("inf")})]
        for index, change in enumerate(changes):
            with self.subTest(case=index):
                data = fixtures(False)
                change(*data)
                with self.assertRaises(ValueError): self.audit["حساب_جانچو"](*data)

    def test_four_png_svg_pairs_and_image_decoding(self):
        with TemporaryDirectory() as directory:
            paths = self.plot["خاکے_بناؤ"](*fixtures(), directory)
            self.assertEqual(len(paths), 8)
            for path in paths:
                self.assertEqual(path.parent, Path(directory)/"خاکے")
                self.assertGreater(path.stat().st_size, 100)
                if path.suffix == ".png":
                    with Image.open(path) as image:
                        self.assertGreater(image.width, 400)
                        self.assertGreater(image.height, 300)
                        image.verify()
                else: self.assertEqual(XML.parse(path).getroot().tag, "{http://www.w3.org/2000/svg}svg")

    def test_missing_images_produce_honest_fourth_panel(self):
        with TemporaryDirectory() as directory:
            self.assertEqual(len(self.plot["خاکے_بناؤ"](*fixtures(False), directory)), 8)
            self.assertTrue((Path(directory)/"خاکے/پیشگوئیاں.png").is_file())

    def test_native_and_fallback_urdu_text_modes(self):
        with patch.dict(self.plot, {"_مقامی_ترتیب": True}):
            self.assertEqual(self.plot["اردو_متن"]("تربیت 10%"), "تربیت ۱۰٪")
        with patch.dict(self.plot, {"_مقامی_ترتیب": False}):
            result = self.plot["اردو_متن"]("تربیت 10%")
            self.assertTrue(any("\ufe70" <= char <= "\ufeff" for char in result))
            self.assertIn("۱۰", result)

    def test_saved_audit_tables_and_stale_success_invalidation(self):
        history, summary, predictions = fixtures(False)
        with TemporaryDirectory() as directory:
            save_fixture(directory, history, summary, predictions)
            result = self.audit["نتیجہ_جانچو"](directory, مکمل_فائلیں=False, وزن_جانچ=False)
            self.assertEqual(result["حالت"], "کامیاب")
            with (Path(directory)/"جماعتی_نتائج.csv").open(encoding="utf-8") as stream: rows = list(csv.reader(stream))
            self.assertEqual([r[0] for r in rows[1:]], summary["جماعتیں"])
            self.assertEqual(rows[1][1:4], ["۲", "۱", "۱"])
            self.assertIn("۵۰.۰٪", (Path(directory)/"نتائج.md").read_text(encoding="utf-8"))
            predictions["متوقع"][0] = 2
            save_fixture(directory, history, summary, predictions)
            with self.assertRaises(ValueError): self.audit["نتیجہ_جانچو"](directory, مکمل_فائلیں=False, وزن_جانچ=False)
            self.assertEqual(json.loads((Path(directory)/"تصدیق.json").read_text(encoding="utf-8"))["حالت"], "ناکام")

    def test_checkpoint_hash_mismatch_rejected(self):
        history, summary, predictions = fixtures(False)
        with TemporaryDirectory() as directory:
            checkpoint = Path(directory)/"بہترین_وزن.pt"
            checkpoint.write_bytes(b"controlled fixture")
            summary["وزن_خلاصہ"] = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
            save_fixture(directory, history, summary, predictions)
            self.audit["نتیجہ_جانچو"](directory, مکمل_فائلیں=False, وزن_جانچ=False)
            checkpoint.write_bytes(b"changed fixture")
            with self.assertRaises(ValueError): self.audit["نتیجہ_جانچو"](directory, مکمل_فائلیں=False, وزن_جانچ=False)

    def test_native_checkpoint_strict_load_and_source_hash(self):
        import torch
        model = load("ماڈل")[canonical_name("ریسنیٹ۱۸")](3, 2)
        history, summary, predictions = fixtures(False)
        summary["پیرامیٹر"] = sum(p.numel() for p in model.parameters())
        summary["بحالی_فرق"] = 0
        summary["ماخذ_خلاصے"] = {"خاکے.urdu": hashlib.sha256((HERE/"خاکے.urdu").read_bytes()).hexdigest()}
        with TemporaryDirectory() as directory, install_importer(), patch.object(sys, "path", [str(HERE), *sys.path]):
            checkpoint = Path(directory)/"بہترین_وزن.pt"
            torch.save(model.state_dict(), checkpoint)
            summary["وزن_خلاصہ"] = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
            save_fixture(directory, history, summary, predictions)
            result = self.audit["نتیجہ_جانچو"](directory, مکمل_فائلیں=False)
            self.assertTrue(result["وزن_ساخت_لوڈ_درست"])
            self.assertTrue(result["ماخذ_خلاصے_درست"])
            summary["ماخذ_خلاصے"]["خاکے.urdu"] = "0"*64
            save_fixture(directory, history, summary, predictions)
            with self.assertRaises(ValueError): self.audit["نتیجہ_جانچو"](directory, مکمل_فائلیں=False)

    def test_replot_from_saved_tensors_without_dataset(self):
        import torch
        model = load("ماڈل")[canonical_name("ریسنیٹ۱۸")](3, 2)
        history, summary, predictions = fixtures(False)
        summary["پیرامیٹر"] = sum(p.numel() for p in model.parameters())
        summary["بحالی_فرق"] = 0
        with TemporaryDirectory() as directory, install_importer(), patch.object(sys, "path", [str(HERE), *sys.path]):
            checkpoint = Path(directory)/"بہترین_وزن.pt"
            torch.save(model.state_dict(), checkpoint)
            summary["وزن_خلاصہ"] = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
            torch.save({"تصاویر": torch.as_tensor(fixtures()[2]["تصاویر"]), "نمونہ_اشاریے": list(range(6))},
                       Path(directory)/"نمونہ_تصاویر.pt")
            save_fixture(directory, history, summary, predictions)
            paths = load("دوبارہ_خاکے")["دوبارہ_بناؤ"](directory)
            self.assertEqual(len(paths), 8)
            result = json.loads((Path(directory)/"تصدیق.json").read_text(encoding="utf-8"))
            self.assertEqual(result["حالت"], "کامیاب")
            self.assertEqual(len(result["فائلیں"]), 8)


if __name__ == "__main__": unittest.main()
