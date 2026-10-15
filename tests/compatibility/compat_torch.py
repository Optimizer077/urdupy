"""AI-003: genuine CPython torch modules, analytic autograd, optimizer and state."""

from pathlib import Path
import tempfile

if __package__:
    from ._support import OfflineCase, pair, require, torch_cpu
else:
    from _support import OfflineCase, pair, require, torch_cpu


class TorchCompatibility(OfflineCase):
    def test_ai003_module_autograd_and_analytic_sgd_step(self):
        torch = require(self, "torch")["torch"]
        urdu, python = pair(self, "torch_training", torch=torch)
        self.assertIsInstance(urdu["MODEL"], torch.nn.Module)
        self.assertEqual(urdu["MODEL"].layer.weight.device.type, "cpu")
        self.assertEqual(urdu["MODEL"].layer.weight.dtype, torch.float64)
        self.assertEqual(urdu["OUTPUT"].item(), -1.0)
        self.assertEqual(urdu["LOSS"].item(), 1.0)
        # y = 1*1 - 1*2 = -1; d(y^2)/dw = 2*y*[1,2] = [-2,-4].
        # SGD(0.1) changes [1,-1] to [1.2,-0.6], whose new prediction is zero.
        expected_gradient = torch.tensor([[-2.0, -4.0]], dtype=torch.float64)
        expected_weights = torch.tensor([[1.2, -0.6]], dtype=torch.float64)
        torch.testing.assert_close(urdu["GRADIENT"], expected_gradient, rtol=0, atol=0)
        torch.testing.assert_close(urdu["WEIGHTS_AFTER"], expected_weights, rtol=0, atol=1e-12)
        self.assertFalse(torch.equal(urdu["WEIGHTS_BEFORE"], urdu["WEIGHTS_AFTER"]))
        self.assertLess(abs(urdu["RESULT"].item()), 1e-12)
        for name in ("OUTPUT", "LOSS", "GRADIENT", "WEIGHTS_BEFORE", "WEIGHTS_AFTER", "RESULT"):
            torch.testing.assert_close(urdu[name], python[name], rtol=0, atol=0)

    def test_ai003_temporary_state_dict_roundtrip(self):
        torch = require(self, "torch")["torch"]
        urdu, _ = pair(self, "torch_training", torch=torch)
        with tempfile.TemporaryDirectory(prefix="urdupy-state-") as directory:
            path = Path(directory) / "weights.pt"
            torch.save(urdu["MODEL"].state_dict(), path)
            state = torch.load(path, map_location="cpu", weights_only=True)
            with torch_cpu(torch):
                restored = type(urdu["MODEL"])()
            restored.load_state_dict(state)
            with torch.no_grad():
                output = restored(urdu["INPUT"])
            torch.testing.assert_close(output, urdu["RESULT"], rtol=0, atol=0)
        self.assertFalse(path.exists(), "temporary checkpoint should be cleaned up")

    def test_numpy_tensor_sharing_is_real_for_the_explicit_contiguous_array(self):
        modules = require(self, "numpy", "torch")
        np, torch = modules["numpy"], modules["torch"]
        from urdupy.runtime import execute_source
        source = (
            "درآمد numpy بطور np\nدرآمد torch\n"
            "ARRAY = np.array([1.0, 2.0], dtype=np.float32)\n"
            "TENSOR = torch.from_numpy(ARRAY)\nARRAY[0] = 9.0\n"
        )
        result = execute_source(source, filename="sharing.urdu")
        self.assertEqual(result["TENSOR"][0].item(), 9.0)
        result["TENSOR"][1] = 7.0
        np.testing.assert_array_equal(result["ARRAY"], [9.0, 7.0])
        self.assertEqual(result["TENSOR"].dtype, torch.float32)
