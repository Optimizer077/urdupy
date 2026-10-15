from io import BytesIO
from PIL import Image
import numpy as np

IMAGE = Image.new("RGB", (2, 1))
IMAGE.putdata([(30, 20, 10), (60, 50, 40)])
BUFFER = BytesIO()
IMAGE.save(BUFFER, format="PNG")
BUFFER.seek(0)
with Image.open(BUFFER) as تصویر:
    RESULT = np.array(تصویر)
print(RESULT.tolist(), RESULT.dtype.name)
