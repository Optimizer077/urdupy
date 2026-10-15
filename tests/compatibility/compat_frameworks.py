"""Optional torchvision and tiny Transformers architecture tests without weights."""

if __package__:
    from ._support import OfflineCase, pair, require
else:
    from _support import OfflineCase, pair, require


class FrameworkCompatibility(OfflineCase):
    def test_torchvision_transforms_and_model_without_pretrained_weights(self):
        modules = require(self, "torch", "PIL", "torchvision")
        torch = modules["torch"]
        urdu, python = pair(self, "torchvision_model", torch=torch)
        self.assertIsInstance(urdu["MODEL"], torch.nn.Module)
        self.assertEqual(tuple(urdu["TENSOR"].shape), (3, 2, 2))
        self.assertEqual(tuple(urdu["RESULT"].shape), (1, 3))
        self.assertEqual(urdu["RESULT"].device.type, "cpu")
        self.assertTrue(bool(torch.isfinite(urdu["RESULT"]).all()))
        expected = torch.tensor([30.0, 20.0, 10.0]).reshape(3, 1, 1) / 255.0
        torch.testing.assert_close(urdu["TENSOR"], expected.expand(3, 2, 2), rtol=0, atol=1e-7)
        expected_normalized = (expected - torch.tensor([0.1, 0.2, 0.3]).reshape(3, 1, 1)) / 0.5
        torch.testing.assert_close(urdu["NORMALIZED"], expected_normalized.expand(3, 2, 2), rtol=0, atol=1e-7)
        torch.testing.assert_close(urdu["RESULT"], python["RESULT"], rtol=0, atol=0)

    def test_ai005_transformers_tiny_config_model_completely_offline(self):
        modules = require(self, "torch", "transformers")
        torch, transformers = modules["torch"], modules["transformers"]
        urdu, python = pair(self, "transformers_tiny", torch=torch)
        self.assertIsInstance(urdu["MODEL"], transformers.BertModel)
        self.assertIsInstance(urdu["MODEL"], torch.nn.Module)
        self.assertEqual(urdu["CONFIG"].vocab_size, 16)
        self.assertEqual(urdu["CONFIG"].num_hidden_layers, 1)
        self.assertEqual(tuple(urdu["RESULT"].shape), (1, 3, 8))
        self.assertEqual(urdu["RESULT"].dtype, torch.float32)
        self.assertEqual(urdu["RESULT"].device.type, "cpu")
        self.assertTrue(bool(torch.isfinite(urdu["RESULT"]).all()))
        self.assertGreater(urdu["RESULT"].abs().sum().item(), 0.0)
        torch.testing.assert_close(urdu["RESULT"], python["RESULT"], rtol=0, atol=1e-6)
