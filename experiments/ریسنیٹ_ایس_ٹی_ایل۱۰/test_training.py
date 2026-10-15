"""Offline end-to-end pipeline check; synthetic fixtures, never a real-data claim."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
import torch
from torch.utils.data import TensorDataset

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from urdupy import execute_source


class TrainingPipeline(unittest.TestCase):
    def test_pipeline_saves_metrics_checkpoint_and_urdu_charts_offline(self):
        folder = Path(__file__).resolve().parent
        old_threads, old_rng = torch.get_num_threads(), torch.get_rng_state()
        old_python, old_numpy = random.getstate(), np.random.get_state()
        old_path = sys.path[:]
        self.addCleanup(torch.set_num_threads, old_threads)
        self.addCleanup(torch.set_rng_state, old_rng)
        self.addCleanup(random.setstate, old_python)
        self.addCleanup(np.random.set_state, old_numpy)
        self.addCleanup(sys.path.__setitem__, slice(None), old_path)
        sys.path.insert(0, str(folder))
        torch.set_num_threads(2)
        source = folder / "تربیت.urdu"
        namespace = execute_source(source.read_text(encoding="utf-8"), str(source))
        train_x = torch.randn(40, 3, 16, 16)
        val_x = torch.randn(20, 3, 16, 16)
        labels = torch.arange(10).repeat(2)
        names = ["ہوائی جہاز", "پرندہ", "گاڑی", "بلی", "ہرن", "کتا", "گھوڑا", "بندر", "بحری جہاز", "ٹرک"]
        fake_data = {
            "train": TensorDataset(train_x, labels.repeat(2)),
            "validation": TensorDataset(val_x, labels),
            "test": TensorDataset(val_x + 0.1, labels),
            "train_indices": list(range(40)), "validation_indices": list(range(40, 60)),
            "mean": [0.5] * 3, "std": [0.2] * 3,
            "class_names": [str(i) for i in range(10)], "class_names_urdu": names,
            "provenance": {"fixture": "synthetic offline test"},
        }
        namespace["ڈیٹا_تیار_کرو"] = lambda *args, **kwargs: fake_data
        with tempfile.TemporaryDirectory(prefix="urdu-resnet-test-") as directory:
            output = Path(directory) / "نتائج"
            argv = [str(source), "--epochs", "1", "--batch-size", "8", "--image-size", "16",
                    "--base-width", "2", "--threads", "2", "--output", str(output)]
            # This Windows CPU torch build stalls in the oneDNN backward path
            # for the deliberately tiny channels-last fixture. Exercise the
            # real convolution/autograd pipeline with the native CPU backend;
            # this context restores the process's oneDNN setting afterwards.
            with mock.patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()), \
                 mock.patch("socket.socket.connect", side_effect=RuntimeError("offline test")), \
                 torch.backends.mkldnn.flags(enabled=False):
                namespace["چلائیں"]()
            report = json.loads((output / "خلاصہ.json").read_text(encoding="utf-8"))
            history = json.loads((output / "تاریخ.json").read_text(encoding="utf-8"))
            predictions = json.loads((output / "پیشگوئیاں.json").read_text(encoding="utf-8"))
            self.assertEqual(report["train_count"], 40)
            self.assertEqual(report["test_count"], 20)
            self.assertEqual(report["best_epoch"], 1)
            self.assertEqual(report["checkpoint_max_abs_error"], 0)
            self.assertEqual(len(history), 1)
            self.assertEqual(len(predictions["targets"]), 20)
            self.assertEqual(sum(a == b for a, b in zip(predictions["targets"], predictions["predictions"])), report["test_correct"])
            self.assertTrue((output / "بہترین_وزن.pt").is_file())
            self.assertTrue((output / "آخری_حالت.pt").is_file())
            self.assertGreaterEqual(len(list((output / "خاکے").glob("*.png"))), 3)
            self.assertEqual(json.loads((output / "ترتیب.json").read_text(encoding="utf-8"))["status"], "مکمل")


if __name__ == "__main__":
    unittest.main()
