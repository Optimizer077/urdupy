"""Optional offline checks for the Urdu ResNet; no data or weights downloads."""

import io
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import torch

from urdupy.runtime import execute_source


class UrduResNetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_threads = torch.get_num_threads()
        cls.old_rng = torch.get_rng_state()
        torch.set_num_threads(2)
        path = Path(__file__).with_name("ماڈل.urdu")
        cls.module = execute_source(path.read_text(encoding="utf-8"), str(path))

    @classmethod
    def tearDownClass(cls):
        torch.set_rng_state(cls.old_rng)
        torch.set_num_threads(cls.old_threads)

    def make_model(self, **kwargs):
        return self.module["ریسنیٹ۱۸"](**kwargs)

    def test_shape_backward_and_urdu_structure(self):
        model = self.make_model()
        self.assertEqual(type(model).__name__, "ریس_نیٹ")
        self.assertEqual(model.بنیادی_چوڑائی, 16)
        self.assertEqual(model.زمرے, 10)
        blocks = [m for m in model.modules() if type(m).__name__ == "بنیادی_بلاک"]
        self.assertEqual(len(blocks), 8)
        for stage in (model.پہلا_مرحلہ, model.دوسرا_مرحلہ,
                      model.تیسرا_مرحلہ, model.چوتھا_مرحلہ):
            self.assertEqual(len(stage), 2)
        self.assertFalse(any(isinstance(m, torch.nn.MaxPool2d) for m in model.modules()))
        self.assertEqual(sum(isinstance(m, torch.nn.Conv2d) for m in model.modules()), 20)
        # 17 principal convolutional layers plus the classifier define depth 18;
        # three projection convolutions live in the residual shortcuts.
        image = torch.randn(2, 3, 96, 96)
        logits = model(image)
        self.assertEqual(tuple(logits.shape), (2, 10))
        loss = torch.nn.functional.cross_entropy(logits, torch.tensor([2, 7]))
        loss.backward()
        gradient = model.ابتدائی_پیچش.weight.grad
        self.assertTrue(torch.isfinite(gradient).all())
        self.assertGreater(gradient.abs().sum().item(), 0)
        self.assertTrue(all(any("\u0600" <= char <= "\u06ff" for char in name)
                            for name, _ in model.named_children()))

    def test_identity_and_projection_shortcuts(self):
        block_type = self.module["بنیادی_بلاک"]
        identity = block_type(16, 16).eval()
        projection = block_type(16, 32, 2).eval()
        self.assertIsInstance(identity.راستہ, torch.nn.Identity)
        self.assertIsInstance(projection.راستہ, torch.nn.Sequential)
        image = torch.randn(2, 16, 24, 24)
        with torch.no_grad():
            self.assertEqual(tuple(identity(image).shape), (2, 16, 24, 24))
            self.assertEqual(tuple(projection(image).shape), (2, 32, 12, 12))
            # Suppress the residual branch: output must be ReLU(shortcut(x)).
            projection.دوسری_معیاری_بندی.weight.zero_()
            projection.دوسری_معیاری_بندی.bias.zero_()
            expected = torch.relu(projection.راستہ(image))
            torch.testing.assert_close(projection(image), expected, rtol=0, atol=0)

    def test_state_dict_roundtrip_with_urdu_keys(self):
        model = self.make_model(num_classes=10, base_width=16).eval()
        image = torch.randn(2, 3, 48, 48)
        with torch.no_grad():
            expected = model(image)
        stream = io.BytesIO()
        torch.save(model.state_dict(), stream)
        stream.seek(0)
        restored = self.make_model().eval()
        restored.load_state_dict(torch.load(stream, weights_only=True, map_location="cpu"))
        with torch.no_grad():
            torch.testing.assert_close(restored(image), expected, rtol=0, atol=0)
        self.assertIn("ابتدائی_پیچش.weight", restored.state_dict())

    def test_full_width_agrees_with_torchvision_small_image_resnet18(self):
        from torchvision.models import resnet18

        reference = resnet18(weights=None, num_classes=10)
        reference.conv1 = torch.nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        reference.maxpool = torch.nn.Identity()
        reference.eval()
        model = self.make_model(base_width=64).eval()
        self.assertEqual(sum(p.numel() for p in model.parameters()),
                         sum(p.numel() for p in reference.parameters()))
        original, target = list(model.state_dict().items()), list(reference.state_dict().items())
        self.assertEqual(len(original), len(target))
        mapped = {}
        for (urdu_name, value), (english_name, destination) in zip(original, target):
            self.assertEqual(value.shape, destination.shape, (urdu_name, english_name))
            mapped[english_name] = value
        reference.load_state_dict(mapped)
        image = torch.randn(2, 3, 32, 32)
        with torch.no_grad():
            torch.testing.assert_close(model(image), reference(image), rtol=0, atol=0)

    def test_invalid_dimensions_are_rejected(self):
        for value in (0, -1, 1.5, True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.make_model(num_classes=value)
                with self.assertRaises(ValueError):
                    self.make_model(base_width=value)


if __name__ == "__main__":
    unittest.main()
