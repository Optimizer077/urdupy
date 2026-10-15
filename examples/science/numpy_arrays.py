import numpy as np

def دوگنا_اور_جمع(اعداد: np.ndarray) -> np.ndarray:
    return اعداد * 2 + np.array([10, 20, 30], dtype=np.int64)

ARRAY = np.arange(6, dtype=np.int64).reshape(2, 3)
RESULT = دوگنا_اور_جمع(ARRAY)
print(RESULT.tolist(), RESULT.shape, RESULT.dtype.name)
