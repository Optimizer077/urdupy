"""Run optional offline CPU fixtures and emit inspectable environment evidence."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PACKAGES = (
    "numpy", "Pillow", "opencv-python-headless", "opencv-python", "torch",
    "torchvision", "transformers", "tokenizers", "huggingface-hub", "safetensors",
    "scipy", "pandas", "scikit-learn",
)


def inventory():
    import urdupy
    packages = {}
    for name in PACKAGES:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "urdupy_version": urdupy.__version__,
        "language_spec_version": urdupy.LANGUAGE_SPEC_VERSION,
        "packages": packages,
    }


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def startTest(self, test):
        self.started = time.perf_counter()
        super().startTest(test)

    def record(self, test, status, detail=None):
        self.records.append({
            "test": test.id(), "status": status,
            "seconds": round(time.perf_counter() - self.started, 6),
            "detail": detail,
        })

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record(test, "PASS")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.record(test, "SKIP", reason)

    def addFailure(self, test, error):
        super().addFailure(test, error)
        self.record(test, "FAIL", self._exc_info_to_string(error, test))

    def addError(self, test, error):
        super().addError(test, error)
        self.record(test, "ERROR", self._exc_info_to_string(error, test))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", action="store_true", help="report distribution metadata without importing optional libraries")
    parser.add_argument("--report", type=Path, help="save JSON evidence to this path")
    parser.add_argument("--require-all", action="store_true", help="return failure when any optional test is skipped")
    arguments = parser.parse_args(argv)
    report = inventory()
    exit_code = 0
    if not arguments.inventory:
        loader = unittest.TestLoader()
        suite = loader.discover(str(ROOT / "tests"), pattern="compat_*.py")
        result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult).run(suite)
        report.update({
            "tests_run": result.testsRun,
            "passed": sum(record["status"] == "PASS" for record in result.records),
            "skipped": len(result.skipped),
            "failures": len(result.failures),
            "errors": len(result.errors),
            "records": result.records,
            "offline_policy": "local configs/synthetic data; Python socket APIs guarded during each test",
            "device_policy": "CPU; no accelerator validation claimed",
            "runtime": "urdupy.runtime.execute_source",
        })
        report["imported_versions"] = {
            name: str(getattr(sys.modules[name], "__version__", "unknown"))
            for name in ("numpy", "PIL", "cv2", "torch", "torchvision", "transformers")
            if name in sys.modules
        }
        if not result.wasSuccessful() or result.testsRun == 0 or (arguments.require_all and result.skipped):
            exit_code = 1
        report["status"] = "FAIL" if exit_code else ("PARTIAL" if result.skipped else "PASS")
    encoded = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
