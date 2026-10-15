"""Optional nonlinear training acceptance; synthetic CPU data, no downloads."""

import hashlib
import json
from pathlib import Path
import tempfile

if __package__:
    from ._support import OfflineCase, execute_example, require, torch_cpu
else:
    from _support import OfflineCase, execute_example, require, torch_cpu


class NeuralTraining(OfflineCase):
    def test_multiepoch_learning_python_equivalence_and_checkpoint(self):
        torch = require(self, "torch")["torch"]
        urdu, _ = execute_example("train_xor", "urdu", torch=torch)
        python, _ = execute_example("train_xor", "py", torch=torch)
        original_rng = torch.get_rng_state().clone()
        original_threads = torch.get_num_threads()
        model, report = urdu["تربیت"](verbose=False)
        reference, expected_report = python["تربیت"](verbose=False)
        self.assertEqual(torch.get_num_threads(), original_threads)
        self.assertTrue(torch.equal(torch.get_rng_state(), original_rng))
        self.assertEqual(report, expected_report)
        self.assertEqual(report["parameters"], 337)
        self.assertFalse(model.training)
        self.assertLess(report["final_train_loss"], report["initial_train_loss"] * 0.1)
        self.assertGreaterEqual(report["test_accuracy"], 0.97)
        self.assertEqual(report["xor_predictions"], [0, 1, 1, 0])
        self.assertEqual([point["epoch"] for point in report["history"]],
                         [0, 100, 200, 300, 400, 500, 600])
        for name, value in model.state_dict().items():
            torch.testing.assert_close(value, reference.state_dict()[name], rtol=0, atol=0)
            self.assertTrue(torch.isfinite(value).all())

        with torch_cpu(torch):
            train_x, _ = urdu["ڈیٹا_بناؤ"](2048, report["train_data_seed"])
            test_x, test_y = urdu["ڈیٹا_بناؤ"](1024, report["test_data_seed"])
            # Independently express XOR as a negative coordinate product.
            torch.testing.assert_close(test_y, (test_x.prod(dim=1) < 0).float(), rtol=0, atol=0)
            self.assertEqual(torch.unique(torch.cat([train_x, test_x]), dim=0).shape[0], 3072)
            with torch.no_grad():
                logits = model(test_x)
            self.assertEqual(((logits >= 0) == test_y.bool()).sum().item(), report["test_correct"])
            with tempfile.TemporaryDirectory(prefix="urdupy-training-") as directory:
                weights = urdu["محفوظ_کرو"](model, report, directory)
                saved = json.loads((Path(directory) / "metrics.json").read_text(encoding="utf-8"))
                self.assertEqual(saved["checkpoint_max_abs_error"], 0)
                self.assertEqual(saved["checkpoint_sha256"], hashlib.sha256(weights.read_bytes()).hexdigest())
                restored = urdu["عصبی_نیٹ"]()
                restored.load_state_dict(torch.load(weights, map_location="cpu", weights_only=True))
                restored.eval()
                with torch.no_grad():
                    torch.testing.assert_close(restored(test_x), logits, rtol=0, atol=0)
            self.assertFalse(weights.exists())

    def test_training_rejects_nonpositive_epochs_and_data_is_seeded(self):
        torch = require(self, "torch")["torch"]
        urdu, _ = execute_example("train_xor", "urdu", torch=torch)
        for epochs in (0, -1):
            with self.assertRaisesRegex(ValueError, "epochs must be positive"):
                urdu["تربیت"](epochs=epochs, verbose=False)
        first, labels = urdu["ڈیٹا_بناؤ"](32, 43)
        repeated, repeated_labels = urdu["ڈیٹا_بناؤ"](32, 43)
        other, _ = urdu["ڈیٹا_بناؤ"](32, 44)
        torch.testing.assert_close(first, repeated, rtol=0, atol=0)
        torch.testing.assert_close(labels, repeated_labels, rtol=0, atol=0)
        self.assertFalse(torch.equal(first, other))
