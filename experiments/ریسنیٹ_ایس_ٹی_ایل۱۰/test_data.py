"""Offline data invariants; no archive, network or real images are required."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch

from urdupy import run_path


class اعداد_کی_جانچ(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.پرانے_تھریڈ = torch.get_num_threads()
        torch.set_num_threads(1)
        cls.ماڈیول = run_path(Path(__file__).with_name("اعداد.urdu"))

    @classmethod
    def tearDownClass(cls):
        torch.set_num_threads(cls.پرانے_تھریڈ)

    def test_طبقاتی_تقسیم_مکمل_الگ_اور_دوبارہ_یکساں(self):
        نشان = torch.arange(10).repeat_interleave(500)
        تقسیم = self.ماڈیول["طبقاتی_تقسیم"]
        پرانی_حالت = torch.get_rng_state().clone()
        تربیت, توثیق = تقسیم(نشان, seed=42)
        دوبارہ_تربیت, دوبارہ_توثیق = تقسیم(نشان, seed=42)
        self.assertEqual(len(تربیت), 4000)
        self.assertEqual(len(توثیق), 1000)
        self.assertEqual(set(تربیت.tolist()) & set(توثیق.tolist()), set())
        self.assertEqual(set(تربیت.tolist()) | set(توثیق.tolist()), set(range(5000)))
        torch.testing.assert_close(torch.bincount(نشان[تربیت]), torch.full((10,), 400))
        torch.testing.assert_close(torch.bincount(نشان[توثیق]), torch.full((10,), 100))
        self.assertTrue(torch.equal(تربیت, دوبارہ_تربیت))
        self.assertTrue(torch.equal(توثیق, دوبارہ_توثیق))
        self.assertTrue(torch.equal(پرانی_حالت, torch.get_rng_state()))
        self.assertFalse(torch.equal(تقسیم(نشان, seed=43)[0], تربیت))
        with self.assertRaises(ValueError):
            تقسیم(torch.tensor([0, 1]), validation_per_class=1)

    def test_تربیتی_پیمانے_اور_تبدیلی_کی_درستی(self):
        تصاویر = torch.tensor([0, 255], dtype=torch.uint8).view(2, 1, 1, 1).expand(2, 3, 2, 2).clone()
        اوسط, انحراف = self.ماڈیول["تربیتی_پیمانے"](تصاویر)
        self.assertEqual(اوسط, [0.5, 0.5, 0.5])
        self.assertEqual(انحراف, [0.5, 0.5, 0.5])
        مجموعہ = self.ماڈیول["تصویری_مجموعہ"](تصاویر, [0, 1], اوسط, انحراف)
        self.assertEqual(مجموعہ[0][0].dtype, torch.float32)
        torch.testing.assert_close(مجموعہ[0][0], -torch.ones(3, 2, 2))
        torch.testing.assert_close(مجموعہ[1][0], torch.ones(3, 2, 2))
        self.assertTrue(torch.equal(مجموعہ[0][0], مجموعہ[0][0]))
        with self.assertRaises(ValueError):
            self.ماڈیول["تصویری_مجموعہ"](تصاویر, [0], اوسط, انحراف)

    def test_تربیتی_تراش_بیج_کے_مطابق_اصل_محفوظ(self):
        تصاویر = torch.arange(3 * 16 * 16).remainder(256).to(torch.uint8).reshape(1, 3, 16, 16)
        اصل = تصاویر.clone()
        بناؤ = self.ماڈیول["تصویری_مجموعہ"]
        پہلا = بناؤ(تصاویر, [2], [0, 0, 0], [1, 1, 1], training=True, seed=17)
        دوسرا = بناؤ(تصاویر, [2], [0, 0, 0], [1, 1, 1], training=True, seed=17)
        نتائج = []
        for _ in range(5):
            الف, ب = پہلا[0], دوسرا[0]
            self.assertTrue(torch.equal(الف[0], ب[0]))
            self.assertEqual(الف[0].shape, (3, 16, 16))
            self.assertEqual(الف[1].item(), 2)
            نتائج.append(الف[0])
        self.assertTrue(any(not torch.equal(نتائج[0], ن) for ن in نتائج[1:]))
        self.assertTrue(torch.equal(اصل, تصاویر))

    def test_سرکاری_خام_تصویر_کی_سمت(self):
        with tempfile.TemporaryDirectory() as عارضی:
            جڑ = Path(عارضی)
            (جڑ / "stl10_binary").mkdir()
            اصل = np.zeros((1, 3, 96, 96), dtype=np.uint8)
            اصل[0, 1, 4, 9] = 197
            اصل.tofile(جڑ / "stl10_binary/train_X.bin")
            np.array([10], dtype=np.uint8).tofile(جڑ / "stl10_binary/train_y.bin")
            تصاویر, نشان = self.ماڈیول["خام_پڑھو"](جڑ, "train")
            self.assertEqual(تصاویر[0, 1, 9, 4].item(), 197)
            self.assertEqual(تصاویر[0, 1, 4, 9].item(), 0)
            self.assertEqual(نشان.tolist(), [9])
            self.assertTrue(تصاویر.is_contiguous())

    def test_مکمل_انٹرفیس_میں_صرف_تربیتی_اوسط(self):
        بناؤ = self.ماڈیول["ڈیٹا_تیار_کرو"]
        نشان = torch.arange(10).repeat_interleave(500)
        تربیت, توثیق = self.ماڈیول["طبقاتی_تقسیم"](نشان, seed=42)
        تصاویر = torch.zeros(5000, 3, 16, 16, dtype=torch.uint8)
        تصاویر[تربیت[::2]] = 128
        تصاویر[توثیق] = 255
        فرضی = {
            "train_images": تصاویر,
            "train_labels": نشان,
            "test_images": torch.full((8000, 3, 16, 16), 255, dtype=torch.uint8),
            "test_labels": torch.arange(10).repeat_interleave(800),
            "source_md5": self.ماڈیول["فائل_جانچ"],
            "image_size": 16,
        }
        with tempfile.TemporaryDirectory() as عارضی:
            (Path(عارضی) / "تصاویر_16_v1.pt").touch()
            with patch.dict(بناؤ.__globals__, {"check_integrity": lambda *_: True}), patch.object(torch, "load", return_value=فرضی):
                اعداد = بناؤ(عارضی, image_size=16, seed=42, download=False)
        متوقع = 64.0 / 255.0
        for اوسط, انحراف in zip(اعداد["mean"], اعداد["std"]):
            self.assertAlmostEqual(اوسط, متوقع)
            self.assertAlmostEqual(انحراف, متوقع)
        self.assertEqual([len(اعداد[ک]) for ک in ["train", "validation", "test"]], [4000, 1000, 8000])
        self.assertEqual(اعداد["train_indices"], تربیت.tolist())
        self.assertEqual(اعداد["validation_indices"], توثیق.tolist())
        self.assertEqual(اعداد["class_names_urdu"][0], "ہوائی جہاز")
        self.assertEqual(اعداد["class_names_urdu"][-1], "ٹرک")
        self.assertEqual(اعداد["provenance"]["normalization_fit"], "train4000_only")
        self.assertFalse(اعداد["provenance"]["unlabeled_used"])
        self.assertFalse(اعداد["provenance"]["standard_ten_fold_protocol"])


if __name__ == "__main__":
    unittest.main()
