"""Offline independent audit fixtures; no model, dataset download or inference."""

import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from urdupy import execute_source


class نتائج_کی_جانچ(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.جڑ = Path(__file__).resolve().parent
        ماخذ = cls.جڑ / "نتائج_جانچیں.urdu"
        cls.ماڈیول = execute_source(ماخذ.read_text(encoding="utf-8"), str(ماخذ), {"__file__": str(ماخذ), "__name__": "_urdu_audit_test"})

    def test_الجھاؤ_کی_سمت_اور_غلط_اشاریے(self):
        گنو = self.ماڈیول["الجھاؤ_گنو"]
        self.assertEqual(گنو([0, 0, 1, 1, 2], [0, 1, 1, 2, 0], classes=3), [[1, 1, 0], [0, 1, 1], [1, 0, 0]])
        for اصل, اندازہ in [([], []), ([0], []), ([0], [3]), ([True], [0]), ([0.0], [0])]:
            with self.assertRaises(ValueError):
                گنو(اصل, اندازہ, classes=3)

    def test_توثیق_میں_برابر_درستگی_کا_پہلا_دور(self):
        چنو = self.ماڈیول["بہترین_دور_چنو"]
        self.assertEqual(چنو([{"epoch": 1, "val_accuracy": 0.3}, {"epoch": 2, "val_accuracy": 0.7}, {"epoch": 3, "val_accuracy": 0.7}]), (2, 0.7))
        with self.assertRaises(ValueError):
            چنو([{"epoch": 1, "val_accuracy": float("nan")}])

    def test_نامکمل_تربیت_سے_کامیابی_کی_فائل_نہیں_بنتی(self):
        with tempfile.TemporaryDirectory() as عارضی:
            منزل = Path(عارضی)
            self.لکھو(منزل / "ترتیب.json", {"status": "تربیت", "epochs": 50})
            with self.assertRaises(ValueError):
                self.ماڈیول["نتیجہ_جانچو"](منزل)
            self.assertFalse((منزل / "تصدیق.json").exists())

    @staticmethod
    def لکھو(راستہ, قدر):
        راستہ.write_text(json.dumps(قدر, ensure_ascii=False), encoding="utf-8")

    def فرضی_ثبوت_بناؤ(self, منزل):
        اصل = منزل / "data" / "stl10_binary"
        اصل.mkdir(parents=True)
        تربیتی_نشان = bytes(جماعت + 1 for جماعت in range(10) for _ in range(500))
        آزمائشی_نشان = bytes(جماعت + 1 for جماعت in range(10) for _ in range(800))
        فائلیں = {"train_X.bin": b"offline synthetic training image fixture", "test_X.bin": b"offline synthetic test image fixture", "train_y.bin": تربیتی_نشان, "test_y.bin": آزمائشی_نشان}
        for نام, مواد in فائلیں.items():
            (اصل / نام).write_bytes(مواد)
        اصل_جانچ = {نام: hashlib.md5(مواد).hexdigest() for نام, مواد in فائلیں.items()}
        ترتیب = {"status": "مکمل", "epochs": 50, "data_dir": str(اصل.parent), "image_size": 96, "base_width": 64, "seed": 42, "device": "fixture", "torch": "fixture", "python": "fixture"}
        self.لکھو(منزل / "ترتیب.json", ترتیب)
        تاریخ = [{"epoch": دور, "train_loss": 1.0, "val_loss": 1.1, "train_accuracy": 0.8, "val_accuracy": 0.7, "lr": 0.01, "seconds": 1.0} for دور in range(1, 51)]
        تاریخ[36]["val_accuracy"] = 0.9
        تاریخ[37]["val_accuracy"] = 0.9
        self.لکھو(منزل / "تاریخ.json", تاریخ)
        تقسیم = {"train_indices": [جماعت * 500 + مقام for جماعت in range(10) for مقام in range(400)], "validation_indices": [جماعت * 500 + مقام for جماعت in range(10) for مقام in range(400, 500)], "class_names": self.ماڈیول["_انگریزی_جماعتیں"], "class_names_urdu": self.ماڈیول["_اردو_جماعتیں"]}
        self.لکھو(منزل / "تقسیم.json", تقسیم)
        حقیقی = [قدر - 1 for قدر in آزمائشی_نشان]
        اندازے = حقیقی.copy()
        اندازے[0], اندازے[800] = 1, 0
        پیشگوئیاں = {"targets": حقیقی, "predictions": اندازے, "probabilities": [0.9] * 8000}
        self.لکھو(منزل / "پیشگوئیاں.json", پیشگوئیاں)
        (منزل / "بہترین_وزن.pt").write_bytes(b"offline checkpoint bytes; never loaded")
        خاکے = منزل / "خاکے"
        خاکے.mkdir()
        خاکوں_کے_راستے = []
        for نام in self.ماڈیول["_خاکوں_کے_نام"]:
            Image.new("RGB", (512, 384), "white").save(خاکے / f"{نام}.png")
            (خاکے / f"{نام}.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 384"><rect width="512" height="384"/></svg>', encoding="utf-8")
            خاکوں_کے_راستے.extend([f"خاکے/{نام}.png", f"خاکے/{نام}.svg"])
        اطلاع = {کلید: ترتیب[کلید] for کلید in ["epochs", "image_size", "base_width", "seed", "device", "torch", "python"]}
        اطلاع.update({"train_count": 4000, "val_count": 1000, "test_count": 8000, "class_names": تقسیم["class_names"], "class_names_urdu": تقسیم["class_names_urdu"], "test_correct": 7998, "test_accuracy": 7998 / 8000, "best_epoch": 37, "best_val_accuracy": 0.9, "checkpoint_max_abs_error": 0.0, "checkpoint_sha256": hashlib.sha256((منزل / "بہترین_وزن.pt").read_bytes()).hexdigest(), "source_hashes": {نام: hashlib.sha256((self.جڑ / نام).read_bytes()).hexdigest() for نام in ["ماڈل.urdu", "اعداد.urdu", "تربیت.urdu", "خاکے.urdu"]}, "plots": خاکوں_کے_راستے})
        self.لکھو(منزل / "خلاصہ.json", اطلاع)
        return اصل_جانچ, اطلاع, پیشگوئیاں

    def test_مکمل_فرضی_جانچ_اور_محفوظ_اعداد_میں_ردوبدل(self):
        جانچو = self.ماڈیول["نتیجہ_جانچو"]
        with tempfile.TemporaryDirectory() as عارضی:
            منزل = Path(عارضی)
            اصل_جانچ, اطلاع, پیشگوئیاں = self.فرضی_ثبوت_بناؤ(منزل)
            with patch.dict(جانچو.__globals__, {"_اصل_جانچ": اصل_جانچ}):
                ثبوت = جانچو(منزل)
                self.assertEqual(ثبوت["status"], "PASS")
                self.assertEqual(ثبوت["test_correct"], 7998)
                self.assertEqual(ثبوت["test_accuracy"], 7998 / 8000)
                self.assertEqual(ثبوت["best_epoch"], 37)
                self.assertEqual(ثبوت["confusion_matrix"][0][:2], [799, 1])
                self.assertEqual(ثبوت["confusion_matrix"][1][:2], [1, 799])
                self.assertEqual(ثبوت["per_class"][0]["recall"], 799 / 800)
                self.assertFalse(ثبوت["full_archive_verified"])
                self.assertEqual(json.loads((منزل / "تصدیق.json").read_text(encoding="utf-8"))["status"], "PASS")
                with (منزل / "الجھاؤ_جدول.csv").open(encoding="utf-8-sig", newline="") as فائل:
                    سطور = list(csv.reader(فائل))
                self.assertEqual(len(سطور), 11)
                self.assertEqual(سطور[0][0], "حقیقی_جماعت_بمقابلہ_پیشگوئی")
                with (منزل / "جماعتی_نتائج.csv").open(encoding="utf-8-sig", newline="") as فائل:
                    جماعتیں = list(csv.DictReader(فائل))
                self.assertEqual(جماعتیں[0]["کل_تصاویر"], "800")
                self.assertEqual(float(جماعتیں[0]["بازیافت_تناسب"]), 799 / 800)
                self.assertIn("خاکے/الجھاؤ_جدول.png", (منزل / "نتائج.md").read_text(encoding="utf-8"))
                اطلاع["best_epoch"] = 38
                self.لکھو(منزل / "خلاصہ.json", اطلاع)
                with self.assertRaisesRegex(ValueError, "پہلا دور"):
                    جانچو(منزل)
                self.assertEqual(json.loads((منزل / "تصدیق.json").read_text(encoding="utf-8"))["status"], "FAIL")
                اطلاع["best_epoch"] = 37
                self.لکھو(منزل / "خلاصہ.json", اطلاع)
                پیشگوئیاں["targets"][0], پیشگوئیاں["targets"][800] = پیشگوئیاں["targets"][800], پیشگوئیاں["targets"][0]
                self.لکھو(منزل / "پیشگوئیاں.json", پیشگوئیاں)
                with self.assertRaisesRegex(ValueError, "عین ترتیب"):
                    جانچو(منزل)

    def test_خراب_ویکٹر_خاکہ_پکڑا_جاتا_ہے(self):
        with tempfile.TemporaryDirectory() as عارضی:
            منزل = Path(عارضی)
            _, اطلاع, _ = self.فرضی_ثبوت_بناؤ(منزل)
            (منزل / "خاکے" / "الجھاؤ_جدول.svg").write_text('<other viewBox="0 0 512 384"/>', encoding="utf-8")
            with self.assertRaises(ValueError):
                self.ماڈیول["خاکے_جانچو"](منزل, اطلاع["plots"])


if __name__ == "__main__":
    unittest.main()
