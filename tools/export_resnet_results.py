"""Export a small, independently reconciled public snapshot of saved training.

No datasets or model weights are copied. Historical training source/checkpoints
remain untouched. The exported metrics are derived from all saved predictions.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments" / "ریسنیٹ_ایس_ٹی_ایل۱۰"
RESULTS = SOURCE / "نتائج" / "ابتدائی_تربیت"
DESTINATION = ROOT / "docs" / "نتائج" / "ریسنیٹ"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export(destination=DESTINATION):
    report = read(RESULTS / "خلاصہ.json")
    history = read(RESULTS / "تاریخ.json")
    predictions = read(RESULTS / "پیشگوئیاں.json")
    split = read(RESULTS / "تقسیم.json")
    targets, guesses = predictions["targets"], predictions["predictions"]
    raw = SOURCE / "ڈیٹاسیٹ" / "stl10_binary"
    for filename, expected in split["provenance"]["file_md5"].items():
        with (raw / filename).open("rb") as stream:
            assert hashlib.file_digest(stream, "md5").hexdigest() == expected, filename
    assert targets == [label - 1 for label in (raw / "test_y.bin").read_bytes()]
    assert len(targets) == len(guesses) == len(predictions["probabilities"]) == 8000
    assert len(history) == report["epochs"] == 50
    assert [row["epoch"] for row in history] == list(range(1, 51))
    assert set(split["train_indices"]).isdisjoint(split["validation_indices"])
    assert set(split["train_indices"]) | set(split["validation_indices"]) == set(range(5000))
    assert len(split["train_indices"]) == 4000 and len(split["validation_indices"]) == 1000
    best = max(history, key=lambda row: row["val_accuracy"])
    assert best["epoch"] == report["best_epoch"] == 44
    assert best["val_accuracy"] == report["best_val_accuracy"] == .77
    matrix = [[0] * 10 for _ in range(10)]
    for target, predicted in zip(targets, guesses):
        assert 0 <= target < 10 and 0 <= predicted < 10
        matrix[target][predicted] += 1
    correct = sum(matrix[index][index] for index in range(10))
    assert correct == report["test_correct"] == 6188
    assert correct / len(targets) == report["test_accuracy"] == .7735
    assert all(sum(row) == 800 for row in matrix)
    assert sha(RESULTS / "بہترین_وزن.pt") == report["checkpoint_sha256"]
    for name, expected in report["source_hashes"].items():
        assert sha(SOURCE / name) == expected, name

    destination.mkdir(parents=True, exist_ok=True)
    plots = []
    for name in ("تربیتی_خاکے", "الجھاؤ_جدول", "جماعتی_درستگی", "پیشگوئیاں"):
        for extension in (".png", ".svg"):
            original = RESULTS / "خاکے" / (name + extension)
            target = destination / original.name
            shutil.copyfile(original, target)
            assert sha(original) == sha(target)
            plots.append({"فائل": target.name, "شا۲۵۶": sha(target), "بائٹ": target.stat().st_size})
    summary = {
        "ماخذ": "محفوظ پچاس دور کی اصل تربیت؛ مکمل اردو ماخذ کی بعد کی تبدیلی کو نئی تربیت نہ سمجھیں",
        "اعدادی_مجموعہ": "ایس ٹی ایل ۱۰", "بناوٹ": "چھوٹی تصویر والا ریسنیٹ ۱۸",
        "پیرامیٹر": report["parameters"], "چوڑائی": report["base_width"], "جسامت": report["image_size"],
        "ادوار": 50, "بہترین_دور": 44, "تربیتی_تعداد": 4000, "توثیقی_تعداد": 1000,
        "آزمائشی_تعداد": 8000, "آزمائشی_درست": correct, "آزمائشی_درستگی": correct / len(targets),
        "بہترین_توثیقی_درستگی": .77, "آزمائشی_نقصان": report["test_loss"],
        "ابتدائی_تربیتی_نقصان": history[0]["train_loss"], "آخری_تربیتی_نقصان": history[-1]["train_loss"],
        "آخری_تربیتی_درستگی": history[-1]["train_accuracy"], "تربیتی_ثانیے": report["train_seconds"],
        "جماعتیں": report["class_names_urdu"], "الجھاؤ_جدول": matrix,
        "آلہ": report["gpu_name"], "تخم": report["seed"], "بیچ": 64,
        "ابتدائی_شرح": history[0]["lr"], "بہترکار": "رفتار کی یادداشت والا اتفاقی تدریجی نزول",
        "تقسیم_الگ_ہے": True, "اصل_آزمائشی_نشان_برابر": True,
        "چار_اصل_فائلوں_کے_ہاش_درست": True, "دس_فولڈ_نتیجہ": False,
        "تیار_وزن_استعمال": False, "بہترین_وزن_شا۲۵۶": report["checkpoint_sha256"],
        "اصل_خلاصہ_شا۲۵۶": sha(RESULTS / "خلاصہ.json"), "اصل_تاریخ_شا۲۵۶": sha(RESULTS / "تاریخ.json"),
        "اصل_پیشگوئیاں_شا۲۵۶": sha(RESULTS / "پیشگوئیاں.json"), "تاریخی_ماخذ_شا۲۵۶": report["source_hashes"],
        "خاکے": plots,
    }
    (destination / "خلاصہ.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = {"دور": "epoch", "تربیتی_نقصان": "train_loss", "تربیتی_درستگی": "train_accuracy",
              "توثیقی_نقصان": "val_loss", "توثیقی_درستگی": "val_accuracy", "شرح": "lr", "ثانیے": "seconds"}
    with (destination / "تربیتی_تاریخ.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(fields))
        writer.writeheader()
        writer.writerows({label: row[key] for label, key in fields.items()} for row in history)
    with (destination / "جماعتی_نتائج.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["جماعت", "تصاویر", "درست", "درست_تناسب"])
        writer.writerows((label, 800, matrix[index][index], matrix[index][index] / 800)
                         for index, label in enumerate(report["class_names_urdu"]))
    print(f"PASS: {correct}/{len(targets)}, {len(history)} epochs, {len(plots)} plot assets; {destination}")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DESTINATION)
    export(parser.parse_args().output)
