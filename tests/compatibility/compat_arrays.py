"""AI-001: real NumPy values and an independent arithmetic expectation."""

if __package__:
    from ._support import OfflineCase, pair, require
else:
    from _support import OfflineCase, pair, require


class NumPyCompatibility(OfflineCase):
    def test_ai001_broadcast_shape_dtype_indexing(self):
        np = require(self, "numpy")["numpy"]
        urdu, python = pair(self, "numpy_arrays")
        result = urdu["RESULT"]
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (2, 3))
        self.assertEqual(result.dtype, np.dtype("int64"))
        np.testing.assert_array_equal(result, [[10, 22, 34], [16, 28, 40]])
        np.testing.assert_array_equal(result, python["RESULT"])
        np.testing.assert_array_equal(result[:, 1], [22, 28])
        self.assertEqual(int(result.sum()), 150)
        np.testing.assert_array_equal(urdu["ARRAY"], [[0, 1, 2], [3, 4, 5]])
        self.assertIs(urdu["دوگنا_اور_جمع"].__annotations__["return"], np.ndarray)
