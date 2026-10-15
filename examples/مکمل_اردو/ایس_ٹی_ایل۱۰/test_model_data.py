"""Offline numerical, raw-layout and historical checkpoint compatibility checks."""

import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image
import torch
import torchvision

from urdupy import compile_urdu, execute_source
from urdupy.urdu_catalog import canonical_name


DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[2]
HISTORICAL = ROOT / "experiments" / "ریسنیٹ_ایس_ٹی_ایل۱۰"
RESULTS = HISTORICAL / "نتائج" / "ابتدائی_تربیت"


def load_source(path, namespace=None):
    namespace = {"__name__": "_urdu_stl10_fixture", **(namespace or {})}
    return execute_source(path.read_text(encoding="utf-8"), str(path), globals=namespace)


def call_urdu(function, *args, **kwargs):
    return function(*args, **{canonical_name(name): value for name, value in kwargs.items()})


class CompleteUrduModelData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_threads = torch.get_num_threads()
        cls.previous_rng = torch.get_rng_state().clone()
        torch.set_num_threads(1)
        cls.model = load_source(DIRECTORY / "ماڈل.urdu")
        cls.data = load_source(DIRECTORY / "اعداد.urdu")
        cls.old_model = load_source(HISTORICAL / "ماڈل.urdu")
        cls.old_data = load_source(HISTORICAL / "اعداد.urdu")
        model_module = ModuleType("ماڈل")
        model_module.__dict__.update(cls.model)
        with patch.dict(sys.modules, {"ماڈل": model_module}):
            cls.inference = load_source(DIRECTORY / "پیشگوئی.urdu")

    @classmethod
    def tearDownClass(cls):
        torch.set_num_threads(cls.previous_threads)
        torch.set_rng_state(cls.previous_rng)

    def test_owned_urdu_sources_have_zero_ascii_letters_and_compile(self):
        for stem in ("ماڈل", "اعداد", "پیشگوئی"):
            path = DIRECTORY / (stem + ".urdu")
            source = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search("[A-Za-z]", source), path.name)
            compile_urdu(source, str(path))

    def test_standalone_inference_help_is_entirely_urdu(self):
        result = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "urdupy", "run", str(DIRECTORY / "پیشگوئی.urdu"), "--", "--مدد"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True,
        )
        self.assertIn("اردو پیشگوئی", result.stdout)
        self.assertIn("--نتائج", result.stdout)
        self.assertIn("--تعداد", result.stdout)
        self.assertIsNone(re.search("[A-Za-z]", result.stdout))
        self.assertEqual(result.stderr, "")

    def test_seeded_new_model_preserves_all_historical_keys_and_initial_weights(self):
        torch.manual_seed(271)
        old = self.old_model["ریسنیٹ۱۸"](num_classes=10, base_width=8)
        torch.manual_seed(271)
        new = self.model[canonical_name("ریسنیٹ۱۸")](جماعتیں=10, چوڑائی=8)
        self.assertIsInstance(new, torch.nn.Module)
        self.assertEqual(type(new).__name__, "ریس_نیٹ")
        self.assertEqual(list(old.state_dict()), list(new.state_dict()))
        for name, value in old.state_dict().items():
            torch.testing.assert_close(value, new.state_dict()[name], rtol=0, atol=0)
        self.assertTrue(any("راستہ.0.weight" in key for key in new.state_dict()))
        self.assertFalse(any("Path" in key for key in new.state_dict()))

    def test_native_model_backward_and_positive_dimension_validation(self):
        model = self.model[canonical_name("ریسنیٹ۱۸")](چوڑائی=4)
        image = torch.randn(2, 3, 32, 32)
        # Tiny fixture backward uses restoring plain CPU kernels; actual CUDA
        # training remains the framework's selected backend.
        with torch.backends.mkldnn.flags(enabled=False):
            logits = model(image)
            self.assertEqual(logits.shape, (2, 10))
            torch.nn.functional.cross_entropy(logits, torch.tensor([1, 7])).backward()
        gradient = model.ابتدائی_پیچش.weight.grad
        self.assertTrue(torch.isfinite(gradient).all())
        self.assertGreater(gradient.abs().sum().item(), 0)
        for invalid in (0, -1, 1.5, True):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    self.model[canonical_name("ریسنیٹ۱۸")](جماعتیں=invalid)
                with self.assertRaises(ValueError):
                    self.model[canonical_name("ریسنیٹ۱۸")](چوڑائی=invalid)

    def test_full_width_parameter_count_and_checkpoint_tensor_roundtrip(self):
        model = self.model[canonical_name("ریسنیٹ۱۸")]().eval()
        self.assertEqual(sum(parameter.numel() for parameter in model.parameters()), 11173962)
        image = torch.randn(1, 3, 32, 32)
        with torch.inference_mode():
            expected = model(image)
        stream = io.BytesIO()
        torch.save(model.state_dict(), stream)
        stream.seek(0)
        restored = self.model[canonical_name("ریسنیٹ۱۸")]().eval()
        restored.load_state_dict(torch.load(stream, weights_only=True, map_location="cpu"))
        with torch.inference_mode():
            torch.testing.assert_close(restored(image), expected, rtol=0, atol=0)

    def test_split_matches_historical_indices_and_preserves_global_rng(self):
        labels = torch.arange(10).repeat_interleave(500)
        before = torch.get_rng_state().clone()
        training, validation = self.data["طبقاتی_تقسیم"](labels, تخم=42)
        old_training, old_validation = self.old_data["طبقاتی_تقسیم"](labels, seed=42)
        self.assertTrue(torch.equal(training, old_training))
        self.assertTrue(torch.equal(validation, old_validation))
        self.assertTrue(torch.equal(before, torch.get_rng_state()))
        self.assertEqual(len(set(training.tolist()) & set(validation.tolist())), 0)
        self.assertEqual(set(training.tolist()) | set(validation.tolist()), set(range(5000)))
        torch.testing.assert_close(torch.bincount(labels[training]), torch.full((10,), 400))
        torch.testing.assert_close(torch.bincount(labels[validation]), torch.full((10,), 100))

    def test_raw_reader_preserves_official_width_height_orientation_and_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = Path(directory) / "stl10_binary"
            raw.mkdir()
            original = np.zeros((1, 3, 96, 96), dtype=np.uint8)
            original[0, 1, 4, 9] = 197
            original.tofile(raw / "train_X.bin")
            np.array([10], dtype=np.uint8).tofile(raw / "train_y.bin")
            images, labels = self.data["خام_پڑھو"](directory, "تربیتی")
            self.assertEqual(images[0, 1, 9, 4].item(), 197)
            self.assertEqual(images[0, 1, 4, 9].item(), 0)
            self.assertEqual(labels.tolist(), [9])
            self.assertTrue(images.is_contiguous())

    def test_actual_checksum_rejects_missing_and_corrupted_files(self):
        check = self.data["فائل_درست_ہے"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "فائل"
            self.assertFalse(check(path, hashlib.md5(b"fixture").hexdigest()))
            path.write_bytes(b"fixture")
            self.assertTrue(check(path, hashlib.md5(b"fixture").hexdigest()))
            path.write_bytes(b"corrupted")
            self.assertFalse(check(path, hashlib.md5(b"fixture").hexdigest()))

    def test_seeded_augmentation_matches_historical_pixels_and_keeps_original(self):
        images = torch.arange(3 * 16 * 16).remainder(256).to(torch.uint8).reshape(1, 3, 16, 16)
        original = images.clone()
        new = self.data["تصویری_مجموعہ"](images, [2], [0, 0, 0], [1, 1, 1], سکھانا=True, تخم=17)
        old = self.old_data["تصویری_مجموعہ"](images, [2], [0, 0, 0], [1, 1, 1], training=True, seed=17)
        outcomes = []
        for _ in range(5):
            actual, expected = new[0], old[0]
            torch.testing.assert_close(actual[0], expected[0], rtol=0, atol=0)
            self.assertEqual(actual[1].item(), 2)
            outcomes.append(actual[0])
        self.assertTrue(any(not torch.equal(outcomes[0], image) for image in outcomes[1:]))
        self.assertTrue(torch.equal(images, original))

    def test_factory_fits_statistics_only_on_training_and_never_downloads_complete_data(self):
        labels = torch.arange(10).repeat_interleave(500)
        training, validation = self.data["طبقاتی_تقسیم"](labels, تخم=42)
        images = torch.zeros(5000, 3, 16, 16, dtype=torch.uint8)
        images[training[::2]] = 128
        images[validation] = 255
        fixtures = {
            "تربیتی": (images, labels),
            "آزمائشی": (torch.full((8000, 3, 16, 16), 255, dtype=torch.uint8), torch.arange(10).repeat_interleave(800)),
        }
        factory = self.data["اعداد_تیار_کرو"]
        replacements = {"فائل_درست_ہے": lambda *_: True, "خام_پڑھو": lambda root, phase: fixtures[phase]}
        with tempfile.TemporaryDirectory() as directory, patch.dict(factory.__globals__, replacements), patch.object(torchvision.datasets, "STL10") as download:
            data = call_urdu(factory, directory, جسامت=16, تخم=42, حصول=True)
            download.assert_not_called()
        self.assertEqual([len(data[key]) for key in ("تربیتی", "توثیقی", "آزمائشی")], [4000, 1000, 8000])
        self.assertEqual(data["تربیتی_اشاریے"], training.tolist())
        self.assertEqual(data["توثیقی_اشاریے"], validation.tolist())
        for mean, std in zip(data["اوسط"], data["انحراف"]):
            self.assertAlmostEqual(mean, 64 / 255)
            self.assertAlmostEqual(std, 64 / 255)
        self.assertEqual(data["جماعتیں"][0], "ہوائی جہاز")
        self.assertFalse(data["ماخذ"]["غیر_نشان_زدہ_استعمال"])
        self.assertFalse(data["ماخذ"]["معیاری_دس_فولڈ"])

    def test_explicit_download_is_native_and_missing_data_without_flag_fails(self):
        factory = self.data["اعداد_تیار_کرو"]
        with tempfile.TemporaryDirectory() as directory, patch.dict(factory.__globals__, {"فائل_درست_ہے": lambda *_: False}), patch.object(torchvision.datasets, "STL10") as download:
            with self.assertRaises(RuntimeError):
                call_urdu(factory, directory, حصول=False)
            download.assert_not_called()
            with self.assertRaises(RuntimeError):
                call_urdu(factory, directory, حصول=True)
            download.assert_called_once_with(Path(directory).resolve(), download=True)

    def test_inference_preprocessing_matches_historical_tensor_resize(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "عکس.png"
            pixels = np.random.default_rng(42).integers(0, 256, (65, 83, 3), dtype=np.uint8)
            Image.fromarray(pixels).save(path)
            for size in (48, 96):
                summary = {"جسامت": size, "اوسط": [0.4, 0.5, 0.6], "انحراف": [0.2, 0.3, 0.4], "جماعتیں": ["الف"], "چوڑائی": 4}
                actual = self.inference["تصویر_تیار_کرو"](path, summary)
                expected = torchvision.transforms.Compose([
                    torchvision.transforms.PILToTensor(),
                    torchvision.transforms.Resize((size, size), antialias=True),
                    torchvision.transforms.ConvertImageDtype(torch.float32),
                    torchvision.transforms.Normalize(summary["اوسط"], summary["انحراف"]),
                ])(Image.open(path).convert("RGB")).unsqueeze(0)
                torch.testing.assert_close(actual, expected, rtol=0, atol=0)

    @unittest.skipUnless((RESULTS / "بہترین_وزن.pt").is_file(), "historical trained checkpoint is an ignored local artifact")
    def test_actual_trained_historical_checkpoint_has_exact_new_model_logits(self):
        checkpoint = torch.load(RESULTS / "بہترین_وزن.pt", map_location="cpu", weights_only=True)
        old = self.old_model["ریسنیٹ۱۸"](num_classes=10, base_width=64).eval()
        new = self.model[canonical_name("ریسنیٹ۱۸")]().eval()
        old.load_state_dict(checkpoint)
        new.load_state_dict(checkpoint)
        summary = json.loads((RESULTS / "خلاصہ.json").read_text(encoding="utf-8"))
        sample = self.inference["تصویر_تیار_کرو"](RESULTS / "نمونہ.png", summary)
        with torch.inference_mode():
            torch.testing.assert_close(new(sample), old(sample), rtol=0, atol=0)
        predictions = self.inference["پیشگوئی_کرو"](RESULTS / "نمونہ.png", RESULTS, تعداد=3)
        self.assertEqual(len(predictions), 3)
        self.assertEqual(predictions[0]["جماعت"], "گھوڑا")
        self.assertGreater(predictions[0]["امکان"], 0.99)


if __name__ == "__main__":
    unittest.main()
