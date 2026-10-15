"""Offline behavioral tests for the standalone complete-Urdu STL-10 trainer."""

from contextlib import contextmanager, redirect_stdout
import hashlib
from io import StringIO
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest import mock

from urdupy import execute_source, install_importer
from tests.compatibility._support import OfflineCase, require, torch_cpu


HERE = Path(__file__).resolve().parent


@contextmanager
def trainer():
    names = ("ماڈل", "اعداد", "خاکے")
    absent = object()
    previous = {name: sys.modules.pop(name, absent) for name in names}
    try:
        with mock.patch.object(sys, "path", [str(HERE), *sys.path]), install_importer():
            path = HERE / "تربیت.urdu"
            namespace = execute_source(path.read_text(encoding="utf-8"), str(path))
            yield namespace
    finally:
        for name, value in previous.items():
            if value is absent:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


def datasets(torch):
    class Counted(torch.utils.data.Dataset):
        def __init__(self, count, seed):
            generator = torch.Generator().manual_seed(seed)
            self.images = torch.rand(count, 3, 16, 16, generator=generator)
            self.labels = torch.arange(count) % 10
            self.visits = []
            self.تخمی_اوزار = generator

        def __len__(self):
            return len(self.images)

        def __getitem__(self, index):
            self.visits.append(index)
            return self.images[index], self.labels[index]

    return {
        "تربیتی": Counted(20, 11), "توثیقی": Counted(10, 12),
        "آزمائشی": Counted(20, 13), "جسامت": 16,
        "تربیتی_اشاریے": list(range(20)), "توثیقی_اشاریے": list(range(20, 30)),
        "اوسط": [0.0] * 3, "انحراف": [1.0] * 3,
        "جماعتیں": ["جماعت" + str(index) for index in range(10)],
        "ماخذ": {"اصل": "مصنوعی مقامی آزمائش"},
    }


class UrduSTLTraining(OfflineCase):
    def setUp(self):
        super().setUp()
        self.torch = require(self, "torch", "numpy", "PIL", "torchvision")["torch"]

    def test_source_is_entirely_urdu_and_cli_never_downloads(self):
        from urdupy import compile_urdu
        source = (HERE / "تربیت.urdu").read_text(encoding="utf-8")
        self.assertIsNone(re.search("[A-Za-z]", source))
        compile_urdu(source, str(HERE / "تربیت.urdu"))
        with trainer() as namespace, tempfile.TemporaryDirectory(prefix="urdupy-stl-cli-") as directory:
            captured = []

            def prepared(root, *, جسامت, تخم, download):
                captured.append((root, جسامت, تخم, download))
                return {"prepared": True}

            def train(data, output, **options):
                return {"received": data, "options": options}

            namespace["اعداد_تیار_کرو"] = prepared
            namespace["تربیت_چلاؤ"] = train
            with redirect_stdout(StringIO()):
                result = namespace["چلائیں"]([
                    "--اعداد", str(Path(directory) / "اعداد"), "--نتائج", str(Path(directory) / "نتائج"),
                    "--ادوار", "1", "--جسامت", "16", "--چوڑائی", "2", "--آلہ", "مرکزی",
                ])
            self.assertEqual(captured[0][1:], (16, 42, False))
            self.assertEqual(result["received"], {"prepared": True})
            self.assertEqual(result["options"]["ادوار"], 1)
            self.assertEqual(result["options"]["آلہ_انتخاب"], "مرکزی")
            with redirect_stdout(StringIO()):
                namespace["چلائیں"]([
                    "--اعداد", str(Path(directory) / "اعداد"), "--نتائج", str(Path(directory) / "نتائج"),
                    "--ادوار", "1", "--جسامت", "16", "--چوڑائی", "2", "--آلہ", "مرکزی", "--حاصل",
                ])
            self.assertEqual(captured[1][1:], (16, 42, True))
            occupied = Path(directory) / "محفوظ"
            occupied.mkdir()
            (occupied / "اصل").write_text("محفوظ", encoding="utf-8")
            with redirect_stdout(StringIO()), mock.patch.object(sys, "stderr", StringIO()), self.assertRaises(SystemExit):
                namespace["چلائیں"]([
                    "--اعداد", str(Path(directory) / "اعداد"), "--نتائج", str(occupied), "--حاصل",
                ])
            self.assertEqual(len(captured), 2, "invalid output must fail before downloading")

    def test_training_command_help_is_entirely_urdu(self):
        with trainer() as namespace:
            output = StringIO()
            with redirect_stdout(output), self.assertRaises(SystemExit) as result:
                namespace["چلائیں"](["--مدد"])
            self.assertEqual(result.exception.code, 0)
            self.assertIn("--اعداد", output.getvalue())
            self.assertIn("--نتائج", output.getvalue())
            self.assertIsNone(re.search("[A-Za-z]", output.getvalue()))

    def test_nonempty_output_and_invalid_options_fail_before_any_sample(self):
        torch = self.torch
        with trainer() as namespace, torch_cpu(torch), tempfile.TemporaryDirectory(prefix="urdupy-stl-guard-") as directory:
            data = datasets(torch)
            output = Path(directory) / "محفوظ"
            output.mkdir()
            marker = output / "اصل"
            marker.write_text("محفوظ", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "خالی"):
                namespace["تربیت_چلاؤ"](data, output, ادوار=1, چوڑائی=2)
            self.assertEqual(marker.read_text(encoding="utf-8"), "محفوظ")
            for options in ({"ادوار": 0}, {"بیچ": 0}, {"چوڑائی": -1},
                            {"شرح": float("nan")}, {"شرح": float("inf")}, {"شرح": 0}, {"تخم": -1}):
                with self.subTest(options=options), self.assertRaises(ValueError):
                    namespace["تربیت_چلاؤ"](data, Path(directory) / "نیا", **options)
            self.assertFalse((Path(directory) / "نیا").exists())
            self.assertEqual(data["تربیتی"].visits, [])
            self.assertEqual(data["توثیقی"].visits, [])
            self.assertEqual(data["آزمائشی"].visits, [])

    def test_two_epoch_real_resnet_pipeline_selection_checkpoint_and_single_test_pass(self):
        torch = self.torch
        with trainer() as namespace, torch_cpu(torch), tempfile.TemporaryDirectory(prefix="urdupy-stl-training-") as directory:
            data = datasets(torch)
            output = Path(directory) / "نتائج"
            with redirect_stdout(StringIO()), torch.backends.mkldnn.flags(enabled=False):
                report = namespace["تربیت_چلاؤ"](
                    data, output, ادوار=2, بیچ=10, چوڑائی=2, تھریڈ=1, تخم=42, خاکے=False)
            saved = json.loads((output / "خلاصہ.json").read_text(encoding="utf-8"))
            history = json.loads((output / "تاریخ.json").read_text(encoding="utf-8"))
            predictions = json.loads((output / "پیشگوئیاں.json").read_text(encoding="utf-8"))
            self.assertEqual(saved, report)
            self.assertEqual([row["دور"] for row in history], [1, 2])
            self.assertAlmostEqual(history[0]["شرح"], 0.05)
            self.assertAlmostEqual(history[1]["شرح"], 0.025)
            earliest_best = max(history, key=lambda row: row["توثیقی_درستگی"])
            self.assertEqual(report["بہترین_دور"], earliest_best["دور"])
            self.assertEqual(report["بہترین_توثیقی_درستگی"], earliest_best["توثیقی_درستگی"])
            self.assertEqual(report["بحالی_فرق"], 0)
            self.assertEqual(report["تربیتی_تعداد"], 20)
            self.assertEqual(report["توثیقی_تعداد"], 10)
            self.assertEqual(report["آزمائشی_تعداد"], 20)
            self.assertEqual(data["آزمائشی"].visits, list(range(20)), "test dataset was revisited for selection or reload")
            self.assertEqual(len(data["تربیتی"].visits), 40)
            self.assertEqual(data["توثیقی"].visits, list(range(10)) * 2)
            self.assertEqual(predictions["اصل"], data["آزمائشی"].labels.tolist())
            self.assertEqual(set(predictions), {"اصل", "متوقع", "اعتماد"})
            self.assertEqual(len(predictions["اعتماد"]), 20)
            self.assertTrue(all(0 <= value <= 1 for value in predictions["اعتماد"]))
            correct = sum(a == b for a, b in zip(predictions["اصل"], predictions["متوقع"]))
            self.assertEqual(report["آزمائشی_درست"], correct)
            self.assertEqual(report["آزمائشی_درستگی"], correct / 20)
            best_path = output / "بہترین_وزن.pt"
            best = torch.load(best_path, map_location="cpu", weights_only=True)
            self.assertEqual(report["وزن_خلاصہ"], hashlib.sha256(best_path.read_bytes()).hexdigest())
            final = torch.load(output / "آخری_حالت.pt", map_location="cpu", weights_only=True)
            self.assertEqual(final["دور"], 2)
            self.assertEqual(final["بہترین_دور"], report["بہترین_دور"])
            self.assertEqual(final["تاریخ"], history)
            for key in ("ماڈل", "اصلاح_کار", "شرح_کار", "دقت_کار", "ترتیب",
                        "ٹارچ_اتفاقی_حالت", "بہاؤ_اتفاقی_حالت", "افزائش_حالت"):
                self.assertIn(key, final)
            self.assertTrue(final["اصلاح_کار"]["state"])
            self.assertEqual(final["شرح_کار"]["last_epoch"], 2)
            self.assertEqual(final["اصلاح_کار"]["param_groups"][0]["momentum"], 0.9)
            self.assertEqual(final["اصلاح_کار"]["param_groups"][0]["weight_decay"], 0.0005)
            self.assertIsInstance(final["افزائش_حالت"], torch.Tensor)
            from urdupy.urdu_catalog import canonical_name
            model = namespace[canonical_name("ریسنیٹ۱۸")](جماعتیں=10, چوڑائی=2).eval()
            model.load_state_dict(best)
            with torch.no_grad(), torch.backends.mkldnn.flags(enabled=False):
                logits = model(data["آزمائشی"].images)
            self.assertEqual(logits.argmax(dim=1).tolist(), predictions["متوقع"])
            samples = torch.load(output / "نمونہ_تصاویر.pt", map_location="cpu", weights_only=True)
            self.assertEqual(samples["تصاویر"].dtype, torch.uint8)
            self.assertEqual(samples["تصاویر"].shape, (10, 3, 16, 16))
            self.assertEqual(samples["نمونہ_اشاریے"], list(range(10)))
            self.assertTrue((output / "تاریخ.csv").is_file())
            self.assertTrue((output / "پیشگوئیاں.csv").is_file())
            environment = json.loads((output / "ماحول.json").read_text(encoding="utf-8"))
            self.assertEqual(environment["ترتیب"]["حالت"], "مکمل")
            self.assertEqual(report["خاکے"], [])


if __name__ == "__main__":
    unittest.main()
