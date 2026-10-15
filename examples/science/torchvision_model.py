import torch
from PIL import Image
from torchvision import models, transforms

IMAGE = Image.new("RGB", (2, 2), color=(30, 20, 10))
TENSOR = transforms.functional.to_tensor(IMAGE)
NORMALIZED = transforms.Normalize(mean=[0.1, 0.2, 0.3], std=[0.5, 0.5, 0.5])(TENSOR)
# weights=None: کوئی pretrained weights یا نیٹ ورک ڈاؤن لوڈ نہیں
MODEL = models.resnet18(weights=None, num_classes=3).cpu().eval()
with torch.no_grad():
    RESULT = MODEL(torch.zeros((1, 3, 32, 32), device="cpu"))
print(list(TENSOR.shape), list(RESULT.shape), bool(torch.isfinite(RESULT).all()))
