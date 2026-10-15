"""URD-031: Urdu-only source exercising genuine offline scientific backends."""

from contextlib import contextmanager, redirect_stdout
import importlib
import importlib.util
from io import StringIO
from pathlib import Path
import re
import sys
import tempfile
from types import ModuleType
from unittest import mock

if __package__:
    from ._support import OfflineCase, require, torch_cpu
else:
    from _support import OfflineCase, require, torch_cpu


EXAMPLES = Path(__file__).resolve().parents[2] / "examples" / "مکمل_اردو"


@contextmanager
def _examples_path():
    with mock.patch.object(sys, "path", [str(EXAMPLES), *sys.path]):
        yield


def _run(stem):
    from urdupy import execute_source
    path = EXAMPLES / (stem + ".urdu")
    with _examples_path(), redirect_stdout(StringIO()):
        return execute_source(path.read_text(encoding="utf-8"), str(path))


def _optional(case, name):
    if importlib.util.find_spec(name) is None:
        case.skipTest(f"optional module {name} is absent")
    return importlib.import_module(name)


def _reference_training(torch, method, epochs=120):
    """Independent native-Python program; no catalog or translated source."""
    torch.manual_seed(7)
    inputs = torch.randn(32, 1, device="cpu")
    targets = 2 * inputs - 0.5
    model = torch.nn.Linear(1, 1).to("cpu")
    if method == "تدریجی":
        optimizer = torch.optim.SGD(model.parameters(), lr=0.08, momentum=0.9)
    else:
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.08, weight_decay=0.0)
    criterion = torch.nn.MSELoss()
    losses = []
    analytic_gradient = (2 * (model(inputs) - targets) * inputs).mean().detach().reshape(1, 1)
    for epoch in range(epochs):
        optimizer.zero_grad(set_to_none=True)
        loss = criterion(model(inputs), targets)
        losses.append(loss.item())
        loss.backward()
        optimizer.step()
    model.eval()
    with torch.no_grad():
        losses.append(criterion(model(inputs), targets).item())
    return model, losses, inputs, targets, analytic_gradient


class UrduOnlyCompatibility(OfflineCase):
    def test_entire_example_source_has_no_ascii_letters_and_compiles(self):
        from urdupy import compile_urdu
        sources = sorted(EXAMPLES.glob("*.urdu"))
        self.assertGreaterEqual(len(sources), 6)
        for path in sources:
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertTrue(source.startswith("# اردوپائی: مکمل\n"))
                self.assertIsNone(re.search("[A-Za-z]", source), path.name)
                compile_urdu(source, str(path))

    def test_unlisted_third_party_identifiers_keep_real_objects_and_kwargs(self):
        from urdupy import execute_source
        from urdupy.urdu_catalog import encode_identifier
        native = ModuleType("vendor_new_v29")
        marker = object()

        def future_layer_X7(*, batch2_size):
            self.assertEqual(batch2_size, 3)
            return marker

        native.future_layer_X7 = future_layer_X7
        module = encode_identifier(native.__name__)
        member = encode_identifier("future_layer_X7")
        label = encode_identifier("batch2_size")
        source = ("# اردوپائی: مکمل\n"
                  f"درآمد {module} بطور کتب_خانہ\n"
                  f"فنکشن_شے = کتب_خانہ.{member}\n"
                  f"نتیجہ = فنکشن_شے({label}=3)\n")
        self.assertIsNone(re.search("[A-Za-z]", source))
        with mock.patch.dict(sys.modules, {native.__name__: native}):
            namespace = execute_source(source)
        self.assertIs(namespace["کتب_خانہ"], native)
        self.assertIs(namespace["فنکشن_شے"], future_layer_X7)
        self.assertIs(namespace["نتیجہ"], marker)

    def test_numpy_arrays_broadcast_dtype_and_linear_algebra(self):
        np = require(self, "numpy")["numpy"]
        result = _run("عددی_حساب")["حساب"]()
        expected = np.arange(6, dtype=np.float64).reshape(2, 3) + np.array([10, 20, 30])
        self.assertIsInstance(result["سرنی"], np.ndarray)
        self.assertEqual(result["سرنی"].dtype, np.float64)
        np.testing.assert_array_equal(result["سرنی"], expected)
        self.assertEqual(result["اوسط"], expected.mean())
        np.testing.assert_allclose(result["جواب"], [2, 3], rtol=0, atol=1e-15)

    def test_real_torch_protocols_two_optimizers_gradients_and_checkpoint(self):
        torch = require(self, "torch")["torch"]
        namespace = _run("عصبی_تربیت")
        self.assertTrue(issubclass(namespace["چھوٹا_ماڈل"], torch.nn.Module))
        self.assertIn("__init__", namespace["چھوٹا_ماڈل"].__dict__)
        self.assertIn("forward", namespace["چھوٹا_ماڈل"].__dict__)
        with torch_cpu(torch):
            for method in ("تدریجی", "ایڈم"):
                with self.subTest(optimizer=method):
                    model, losses, inputs, targets, gradient = namespace["سکھاؤ"](method)
                    reference, expected_losses, expected_inputs, expected_targets, expected_gradient = _reference_training(torch, method)
                    self.assertEqual(model.training, False)
                    self.assertEqual(model.تہہ.weight.device.type, "cpu")
                    self.assertEqual(losses, expected_losses)
                    self.assertLess(losses[-1], losses[0] * 0.0001)
                    self.assertEqual(len(losses), 121)
                    torch.testing.assert_close(inputs, expected_inputs, rtol=0, atol=0)
                    torch.testing.assert_close(targets, expected_targets, rtol=0, atol=0)
                    torch.testing.assert_close(gradient, expected_gradient, rtol=1e-6, atol=1e-7)
                    torch.testing.assert_close(model.تہہ.weight, reference.weight, rtol=0, atol=0)
                    torch.testing.assert_close(model.تہہ.bias, reference.bias, rtol=0, atol=0)
                    with tempfile.TemporaryDirectory(prefix="urdupy-full-urdu-") as directory:
                        path = Path(directory) / "سیکھے_وزن"
                        restored = namespace["محفوظ_اور_واپس"](model, inputs, path)
                        self.assertTrue(path.is_file())
                        state = torch.load(path, map_location="cpu", weights_only=True)
                        self.assertEqual(set(state), {"تہہ.weight", "تہہ.bias"})
                        with torch.no_grad():
                            torch.testing.assert_close(restored(inputs), model(inputs), rtol=0, atol=0)
                    self.assertFalse(path.exists())

    def test_numpy_opencv_pillow_actual_pixels(self):
        modules = require(self, "numpy", "cv2", "PIL")
        np, cv2 = modules["numpy"], modules["cv2"]
        from PIL import Image
        rgb, gray, resized, image = _run("تصویری_حساب")["تصویری_راستہ"]()
        self.assertIsInstance(rgb, np.ndarray)
        self.assertEqual(rgb.dtype, np.uint8)
        np.testing.assert_array_equal(gray, [[76, 150], [29, 255]])
        np.testing.assert_array_equal(gray, cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY))
        np.testing.assert_array_equal(resized, cv2.resize(gray, (4, 4)))
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(image.size, (4, 4))
        self.assertEqual(image.mode, "RGB")
        np.testing.assert_array_equal(np.asarray(image), np.asarray(Image.fromarray(rgb).resize((4, 4))))

    def test_torchvision_and_transformers_offline_native_equivalence(self):
        modules = require(self, "numpy", "torch", "PIL", "torchvision", "transformers")
        np, torch = modules["numpy"], modules["torch"]
        torchvision, transformers = modules["torchvision"], modules["transformers"]
        from PIL import Image
        namespace = _run("بصارت_اور_زبان")
        image = Image.fromarray(np.array([[[255, 0, 0], [0, 255, 0]]], dtype=np.uint8))
        expected_transform = torchvision.transforms.Compose([
            torchvision.transforms.Resize((4, 4)), torchvision.transforms.PILToTensor(),
            torchvision.transforms.ConvertImageDtype(torch.float32),
        ])
        torch.testing.assert_close(namespace["تصویر_بدلو"](image), expected_transform(image), rtol=0, atol=0)
        with torch_cpu(torch):
            model, actual = namespace["زبان_بناؤ"]()
            self.assertIsInstance(model, transformers.BertModel)
            self.assertEqual(actual.shape, (1, 3, 8))
            self.assertEqual(actual.device.type, "cpu")
            self.assertTrue(bool(torch.isfinite(actual).all()))
            torch.manual_seed(7)
            config = transformers.BertConfig(
                vocab_size=16, hidden_size=8, num_hidden_layers=1, num_attention_heads=2,
                intermediate_size=16, max_position_embeddings=16,
                hidden_dropout_prob=0.0, attention_probs_dropout_prob=0.0,
            )
            reference = transformers.BertModel(config).to("cpu").eval()
            with torch.no_grad():
                expected = reference(input_ids=torch.tensor([[1, 2, 3]], dtype=torch.int64)).last_hidden_state
            torch.testing.assert_close(actual, expected, rtol=0, atol=0)

    def test_all_urdu_resnet18_real_native_architecture_forward_backward_and_restore(self):
        torch = require(self, "torch")["torch"]
        namespace = _run("ریسنیٹ")
        with torch_cpu(torch):
            full = namespace["ریس_نیٹ"]()
            self.assertIsInstance(full, torch.nn.Module)
            self.assertEqual(sum(p.numel() for p in full.parameters()), 11_173_962)
            self.assertEqual(sum(isinstance(module, namespace["بنیادی_بلاک"]) for module in full.modules()), 8)
            self.assertEqual(sum(isinstance(module, torch.nn.Conv2d) for module in full.modules()), 20)
            self.assertEqual(sum(isinstance(module, torch.nn.Linear) for module in full.modules()), 1)
            self.assertEqual(sum(isinstance(module, torch.nn.MaxPool2d) for module in full.modules()), 0)
            model = namespace["ریس_نیٹ"](چوڑائی=4)
            inputs = torch.randn(2, 3, 32, 32)
            targets = torch.tensor([1, 2], dtype=torch.int64)
            # Tiny CPU channels-last convolution can stall in this oneDNN tuple.
            # Disable only for this synthetic fixture and restore the backend.
            with torch.backends.mkldnn.flags(enabled=False):
                logits = model(inputs)
                self.assertEqual(logits.shape, (2, 10))
                loss = torch.nn.CrossEntropyLoss()(logits, targets)
                loss.backward()
            self.assertTrue(all(parameter.grad is not None for parameter in model.parameters()))
            self.assertTrue(all(bool(torch.isfinite(parameter.grad).all()) for parameter in model.parameters()))
            self.assertGreater(model.ابتدائی[0].weight.grad.abs().sum().item(), 0)
            optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
            before = model.درجہ_بند.weight.detach().clone()
            optimizer.step()
            self.assertFalse(torch.equal(before, model.درجہ_بند.weight))
            model.eval()
            restored = namespace["ریس_نیٹ"](چوڑائی=4).eval()
            restored.load_state_dict(model.state_dict())
            with torch.no_grad(), torch.backends.mkldnn.flags(enabled=False):
                torch.testing.assert_close(model(inputs), restored(inputs), rtol=0, atol=0)

    def test_urdu_training_graph_uses_actual_loss_and_exports(self):
        torch = require(self, "torch")["torch"]
        _optional(self, "matplotlib")
        _optional(self, "arabic_reshaper")
        _optional(self, "bidi")
        with torch_cpu(torch):
            namespace = _run("تربیتی_خاکہ")
            with tempfile.TemporaryDirectory(prefix="urdupy-graph-") as directory:
                path = Path(directory) / "تربیتی_نقصان"
                figure, axis = namespace["خاکہ_بناؤ"](path)
                try:
                    points = axis.lines[0].get_ydata()
                    self.assertEqual(len(points), 121)
                    self.assertLess(points[-1], points[0] * 0.0001)
                    for text in (axis.get_title(), axis.get_xlabel(), axis.get_ylabel()):
                        self.assertTrue(text)
                        self.assertIsNone(re.search("[A-Za-z]", text))
                    image_path = Path(str(path) + ".png")
                    self.assertGreater(image_path.stat().st_size, 1000)
                    self.assertEqual(image_path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
                finally:
                    import matplotlib.pyplot as plt
                    plt.close(figure)


if __name__ == "__main__":
    import unittest
    unittest.main()
