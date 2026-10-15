"""Offline inference checks using synthetic images and a dummy classifier."""

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
from PIL import Image
import torch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from urdupy import execute_source


class پیشگوئی_کی_جانچ(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = Path(__file__).resolve().parent
        old_path = sys.path[:]
        sys.path.insert(0, str(folder))
        try:
            path = folder / "پیشگوئی.urdu"
            cls.inference = execute_source(path.read_text(encoding="utf-8"), str(path))
            path = folder / "اعداد.urdu"
            cls.data = execute_source(path.read_text(encoding="utf-8"), str(path))
        finally:
            sys.path[:] = old_path

    def test_preprocessing_matches_dataset_at_48_and_96(self):
        pixels = np.random.default_rng(42).integers(0, 256, (96, 96, 3), dtype=np.uint8)
        mean, std = [0.41, 0.52, 0.63], [0.21, 0.22, 0.23]
        with tempfile.TemporaryDirectory(prefix="urdu-inference-") as directory:
            path = Path(directory) / "تصویر.png"
            Image.fromarray(pixels).save(path)
            raw = torch.from_numpy(pixels.copy()).permute(2, 0, 1).unsqueeze(0)
            for size in (48, 96):
                with self.subTest(image_size=size):
                    resized = self.data["جسامت_بدلو"](raw, size)
                    expected = (resized.float().div(255.0) - torch.tensor(mean).view(1, 3, 1, 1))
                    expected = expected / torch.tensor(std).view(1, 3, 1, 1)
                    actual = self.inference["تصویر_تیار_کرو"](
                        path, {"image_size": size, "mean": mean, "std": std})
                    self.assertEqual(actual.dtype, torch.float32)
                    self.assertEqual(tuple(actual.shape), (1, 3, size, size))
                    torch.testing.assert_close(actual, expected, rtol=0, atol=0)

    def test_inference_returns_top_three_urdu_classes_and_captured_tensor(self):
        class کاذب_ماڈل(torch.nn.Module):
            def forward(self, تصویر):
                self.دیکھی_تصویر = تصویر.detach().clone()
                return torch.arange(10, dtype=torch.float32).unsqueeze(0)

        model = کاذب_ماڈل()
        names = ["ہوائی جہاز", "پرندہ", "گاڑی", "بلی", "ہرن", "کتا", "گھوڑا", "بندر", "بحری جہاز", "ٹرک"]
        report = {"class_names_urdu": names, "base_width": 16, "image_size": 48,
                  "mean": [0.4, 0.5, 0.6], "std": [0.2, 0.2, 0.2]}
        pixels = np.random.default_rng(7).integers(0, 256, (96, 96, 3), dtype=np.uint8)
        with tempfile.TemporaryDirectory(prefix="urdu-predictions-") as directory:
            folder = Path(directory)
            path = folder / "تصویر.png"
            Image.fromarray(pixels).save(path)
            (folder / "خلاصہ.json").write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
            with mock.patch.dict(self.inference, {"ریسنیٹ۱۸": lambda **kwargs: model}), \
                 mock.patch.object(torch, "load", return_value={}) as load:
                predictions = self.inference["پیشگوئی_کرو"](path, folder)
            load.assert_called_once_with(folder / "بہترین_وزن.pt", map_location="cpu", weights_only=True)
            self.assertFalse(model.training)
            self.assertEqual([p["جماعت"] for p in predictions], ["ٹرک", "بحری جہاز", "بندر"])
            probabilities = [p["امکان"] for p in predictions]
            self.assertTrue(all(0 < probability < 1 for probability in probabilities))
            self.assertEqual(probabilities, sorted(probabilities, reverse=True))
            expected = self.inference["تصویر_تیار_کرو"](path, report)
            torch.testing.assert_close(model.دیکھی_تصویر, expected, rtol=0, atol=0)


if __name__ == "__main__":
    unittest.main()
