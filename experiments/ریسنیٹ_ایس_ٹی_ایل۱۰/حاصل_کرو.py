"""Download the official STL-10 archive; extract only the labeled experiment files.

This is an opt-in experiment command, never a routine test dependency. The full
official archive is checked against torchvision's published MD5 before reading it.
The 100,000 unlabeled images are neither extracted nor loaded.
"""

import argparse
import json
from pathlib import Path
import tarfile
import time

from torchvision.datasets.utils import check_integrity, download_url


سرکاری_پتہ = "https://ai.stanford.edu/~acoates/stl10/stl10_binary.tar.gz"
محفوظہ_نام = "stl10_binary.tar.gz"
محفوظہ_جانچ = "91f7769df0f17e558f3565bffb0c7dfb"
فائل_جانچ = {
    "train_X.bin": "918c2871b30a85fa023e0c44e0bee87f",
    "train_y.bin": "5a34089d4802c674881badbb80307741",
    "test_X.bin": "7f263ba9f9e0b06b93213547f721ac82",
    "test_y.bin": "36f9794fa4beb8a2c72628de14fa638e",
}


def حاصل_کرو(جڑ):
    جڑ = Path(جڑ).resolve()
    جڑ.mkdir(parents=True, exist_ok=True)
    منزل = جڑ / "stl10_binary"
    آغاز = time.time()
    if all(check_integrity(منزل / نام, جانچ) for نام, جانچ in فائل_جانچ.items()):
        print("تمام نشان زدہ فائلیں پہلے سے درست ہیں۔", flush=True)
        return منزل
    print("سرکاری ایس ٹی ایل ۱۰ محفوظہ حاصل ہو رہا ہے۔", flush=True)
    download_url(سرکاری_پتہ, str(جڑ), محفوظہ_نام, md5=محفوظہ_جانچ)
    محفوظہ = جڑ / محفوظہ_نام
    if not check_integrity(محفوظہ, محفوظہ_جانچ):
        raise RuntimeError("سرکاری محفوظہ کی جانچ ناکام ہوئی۔")
    منزل.mkdir(parents=True, exist_ok=True)
    منتخب = set(فائل_جانچ) | {"class_names.txt", "fold_indices.txt", "README"}
    with tarfile.open(محفوظہ, "r:gz") as بستہ:
        for رکن in بستہ:
            حصہ = Path(رکن.name)
            if حصہ.parts[:1] != ("stl10_binary",) or len(حصہ.parts) != 2:
                continue
            if حصہ.name not in منتخب or not رکن.isfile():
                continue
            with بستہ.extractfile(رکن) as ماخذ, (منزل / حصہ.name).open("wb") as ہدف:
                while ٹکڑا := ماخذ.read(8 * 1024 * 1024):
                    ہدف.write(ٹکڑا)
            print(f"فائل تیار: {حصہ.name}", flush=True)
    for نام, جانچ in فائل_جانچ.items():
        if not check_integrity(منزل / نام, جانچ):
            raise RuntimeError(f"فائل کی جانچ ناکام ہوئی: {نام}")
    تفصیل = {
        "url": سرکاری_پتہ,
        "archive": محفوظہ_نام,
        "archive_bytes": محفوظہ.stat().st_size,
        "archive_md5": محفوظہ_جانچ,
        "file_md5": فائل_جانچ,
        "duration_seconds": round(time.time() - آغاز, 3),
        "unlabeled_extracted": False,
        "official_train_count": 5000,
        "official_test_count": 8000,
    }
    (جڑ / "حصول.json").write_text(json.dumps(تفصیل, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("سرکاری نشان زدہ اعداد کی تمام جانچیں کامیاب ہیں۔", flush=True)
    return منزل


if __name__ == "__main__":
    دلائل = argparse.ArgumentParser(description="سرکاری ایس ٹی ایل ۱۰ اعداد حاصل کریں۔")
    دلائل.add_argument("--root", type=Path, default=Path(__file__).parent / "ڈیٹاسیٹ")
    اختیار = دلائل.parse_args()
    حاصل_کرو(اختیار.root)
