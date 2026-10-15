"""Optional offline graph-data checks; rendering is covered by test_training.py."""

from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urdupy import execute_source


class خاکہ_جانچ(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name("خاکے.urdu")
        cls.module = execute_source(path.read_text(encoding="utf-8"), str(path))

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="urdu-resnet-plot-data-")
        self.addCleanup(self.directory.cleanup)
        self.output = Path(self.directory.name) / "خاکے"
        self.history = [
            {"epoch": 1, "train_loss": 2.1, "val_loss": 2.2,
             "train_accuracy": 0.21, "val_accuracy": 0.2},
            {"epoch": 2, "train_loss": 1.8, "val_loss": 1.9,
             "train_accuracy": 0.3, "val_accuracy": 0.28},
        ]
        self.report = {
            "class_names_urdu": ["ہوائی جہاز", "پرندہ", "گاڑی", "بلی", "ہرن",
                                 "کتا", "گھوڑا", "بندر", "بحری جہاز", "ٹرک"],
            "test_count": 7, "test_accuracy": 3 / 7,
            "train_count": 4000, "val_count": 1000, "best_epoch": 2,
        }
        # Deliberately asymmetric: two true class-0 images predict class 1,
        # one true class-1 image predicts class 0, and class 9 predicts class 8.
        self.predictions = {
            "targets": [0, 0, 0, 1, 2, 9, 9],
            "predictions": [0, 1, 1, 0, 2, 8, 9],
        }
        self.renderers = {
            name: mock.Mock(return_value=[self.output / f"{name}.png"])
            for name in ("تربیتی_خاکہ", "الجھاؤ_خاکہ", "جماعتی_خاکہ", "تصویری_خاکہ")
        }
        patcher = mock.patch.dict(self.module, self.renderers)
        patcher.start()
        self.addCleanup(patcher.stop)

    def بناؤ(self, **changes):
        return self.module["خاکے_بناؤ"](
            changes.get("history", self.history),
            changes.get("report", self.report),
            changes.get("predictions", self.predictions), self.output,
        )

    def خاموش_ناکامی(self, **changes):
        with self.assertRaises(ValueError):
            self.بناؤ(**changes)
        for renderer in self.renderers.values():
            renderer.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_صف_حقیقی_ستون_پیشگوئی_اور_تعداد(self):
        original = deepcopy((self.history, self.report, self.predictions))
        paths = self.بناؤ()
        expected = np.zeros((10, 10), dtype=np.int64)
        expected[0, 0], expected[0, 1] = 1, 2
        expected[1, 0], expected[2, 2] = 1, 1
        expected[9, 8], expected[9, 9] = 1, 1
        confusion = self.renderers["الجھاؤ_خاکہ"].call_args.args[0]
        per_class = self.renderers["جماعتی_خاکہ"].call_args.args[0]
        np.testing.assert_array_equal(confusion, expected)
        np.testing.assert_array_equal(per_class, expected)
        self.assertEqual(confusion.sum(), self.report["test_count"])
        self.assertEqual(np.trace(confusion) / confusion.sum(), self.report["test_accuracy"])
        self.assertEqual(confusion[0, 1], 2)
        self.assertEqual(confusion[1, 0], 1)
        self.assertTrue(np.all(confusion[3:9] == 0))
        self.assertEqual(len(paths), 4)
        self.assertTrue(all(path.parent == self.output for path in paths))
        for renderer in self.renderers.values():
            renderer.assert_called_once()
        self.assertIs(self.renderers["تربیتی_خاکہ"].call_args.args[0], self.history)
        self.assertEqual((self.history, self.report, self.predictions), original)

    def test_غلط_آزمائشی_تعداد_اور_درستگی(self):
        for changes in ({"test_count": 8}, {"test_accuracy": 0.9}):
            with self.subTest(changes=changes):
                self.خاموش_ناکامی(report={**self.report, **changes})
        for predictions in (
            {**self.predictions, "predictions": [0]},
            {"targets": [], "predictions": []},
            {**self.predictions, "targets": [[0] * 7]},
        ):
            with self.subTest(predictions=predictions):
                self.خاموش_ناکامی(predictions=predictions)

    def test_جماعتوں_کے_اشاریے_اور_نام(self):
        for field in ("targets", "predictions"):
            for value in (-1, 10):
                predictions = deepcopy(self.predictions)
                predictions[field][0] = value
                with self.subTest(field=field, value=value):
                    self.خاموش_ناکامی(predictions=predictions)
        for names in ([], ["بلی", "بلی"]):
            with self.subTest(names=names):
                self.خاموش_ناکامی(report={**self.report, "class_names_urdu": names})

    def test_تربیتی_تاریخ_کی_حدود(self):
        for history in ([], list(reversed(self.history)), [self.history[0]] * 2):
            with self.subTest(history=history):
                self.خاموش_ناکامی(history=history)
        for field in ("train_loss", "val_loss", "train_accuracy", "val_accuracy"):
            for value in (-0.1, float("nan"), float("inf")):
                history = deepcopy(self.history)
                history[0][field] = value
                with self.subTest(field=field, value=value):
                    self.خاموش_ناکامی(history=history)
        for field in ("train_accuracy", "val_accuracy"):
            history = deepcopy(self.history)
            history[0][field] = 1.01
            with self.subTest(field=field):
                self.خاموش_ناکامی(history=history)


if __name__ == "__main__":
    unittest.main()
