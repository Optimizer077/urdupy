import numpy as np
import cv2

def رنگ_بدلو(تصویر):
    return cv2.cvtColor(تصویر, cv2.COLOR_BGR2RGB)

BGR = np.array([[[10, 20, 30]]], dtype=np.uint8)
RGB = رنگ_بدلو(BGR)
GRAY = cv2.cvtColor(BGR, cv2.COLOR_BGR2GRAY)
RESULT = cv2.resize(RGB, (2, 2), interpolation=cv2.INTER_NEAREST)
print(RESULT.tolist(), RESULT.dtype.name, GRAY.tolist())
