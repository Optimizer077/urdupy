"""AI-002/004: synthetic CPU images, no GUI, camera, fixtures or downloads."""

if __package__:
    from ._support import OfflineCase, pair, require
else:
    from _support import OfflineCase, pair, require


class VisionCompatibility(OfflineCase):
    def test_ai002_opencv_color_gray_and_resize(self):
        modules = require(self, "numpy", "cv2")
        np = modules["numpy"]
        urdu, python = pair(self, "opencv_color")
        expected = np.array([[[30, 20, 10], [30, 20, 10]],
                             [[30, 20, 10], [30, 20, 10]]], dtype=np.uint8)
        self.assertEqual(urdu["RESULT"].shape, (2, 2, 3))
        self.assertEqual(urdu["RESULT"].dtype, np.dtype("uint8"))
        np.testing.assert_array_equal(urdu["RESULT"], expected)
        np.testing.assert_array_equal(urdu["RESULT"], python["RESULT"])
        np.testing.assert_array_equal(urdu["RGB"], [[[30, 20, 10]]])
        np.testing.assert_array_equal(urdu["GRAY"], [[22]])
        np.testing.assert_array_equal(urdu["BGR"], [[[10, 20, 30]]])

    def test_ai002_pillow_local_png_roundtrip(self):
        modules = require(self, "numpy", "PIL")
        np = modules["numpy"]
        urdu, python = pair(self, "pillow_image")
        self.assertEqual(urdu["IMAGE"].mode, "RGB")
        self.assertEqual(urdu["IMAGE"].size, (2, 1))
        self.assertEqual(urdu["RESULT"].dtype, np.dtype("uint8"))
        np.testing.assert_array_equal(urdu["RESULT"], [[[30, 20, 10], [60, 50, 40]]])
        np.testing.assert_array_equal(urdu["RESULT"], python["RESULT"])

    def test_ai004_numpy_opencv_torch_channels_and_model(self):
        modules = require(self, "numpy", "cv2", "torch")
        np, torch = modules["numpy"], modules["torch"]
        urdu, python = pair(self, "vision_tensor", torch=torch)
        tensor = urdu["TENSOR"]
        self.assertIsInstance(tensor, torch.Tensor)
        self.assertEqual(tuple(tensor.shape), (1, 3, 1, 2))
        self.assertEqual(tensor.dtype, torch.float32)
        self.assertEqual(tensor.device.type, "cpu")
        self.assertTrue(tensor.is_contiguous())
        np.testing.assert_array_equal(urdu["RGB"], [[[30, 20, 10], [60, 50, 40]]])
        self.assertFalse(np.shares_memory(urdu["ARRAY"], urdu["BGR"]))
        expected_channels = torch.tensor([[[[30, 60]], [[20, 50]], [[10, 40]]]],
                                         dtype=torch.float32) / 255.0
        expected_output = torch.tensor([[[[100.0, 280.0]]]]) / 255.0
        torch.testing.assert_close(tensor, expected_channels, rtol=0, atol=1e-7)
        torch.testing.assert_close(urdu["RESULT"], expected_output, rtol=0, atol=2e-7)
        torch.testing.assert_close(urdu["RESULT"], python["RESULT"], rtol=0, atol=0)
