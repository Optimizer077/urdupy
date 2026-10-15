"""CPU/offline fixtures; no optional dependency is imported at discovery time."""

import builtins
from contextlib import contextmanager, redirect_stdout
import importlib
import importlib.metadata
import importlib.util
from io import StringIO
import os
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples" / "science"
DISTRIBUTIONS = {
    "numpy": ("numpy",),
    "PIL": ("Pillow",),
    "cv2": ("opencv-python-headless", "opencv-python"),
    "torch": ("torch",),
    "torchvision": ("torchvision",),
    "transformers": ("transformers",),
    "scipy": ("scipy",),
    "pandas": ("pandas",),
    "sklearn": ("scikit-learn",),
}


@contextmanager
def offline():
    """Fail a Python socket network attempt; restore environment and API patches."""
    environment = {
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "HF_HUB_DISABLE_TELEMETRY": "1",
        "DO_NOT_TRACK": "1",
    }
    message = "compatibility fixtures must run offline"
    with mock.patch.dict(os.environ, environment), \
         mock.patch("socket.create_connection", side_effect=RuntimeError(message)), \
         mock.patch("socket.socket.connect", side_effect=RuntimeError(message)), \
         mock.patch("socket.socket.connect_ex", side_effect=RuntimeError(message)), \
         mock.patch("socket.getaddrinfo", side_effect=RuntimeError(message)):
        yield


def require(case, *names):
    """Skip absent extras. An installed-but-broken import is an error, not a skip."""
    modules = {}
    for name in names:
        if importlib.util.find_spec(name) is None:
            installed = []
            for distribution in DISTRIBUTIONS[name]:
                try:
                    installed.append(f"{distribution}=={importlib.metadata.version(distribution)}")
                except importlib.metadata.PackageNotFoundError:
                    pass
            if installed:
                raise ImportError(f"Installed distribution has no importable {name}: {installed}")
            case.skipTest(f"optional module {name} is absent; install a compatible isolated environment")
        modules[name] = importlib.import_module(name)
    return modules


@contextmanager
def torch_cpu(torch):
    """Restore CPU RNG and thread settings; no GPU initialization is required."""
    original_threads = torch.get_num_threads()
    with torch.random.fork_rng(devices=[]):
        try:
            torch.set_num_threads(1)
            torch.manual_seed(7)
            yield
        finally:
            torch.set_num_threads(original_threads)


def execute_example(stem, language, torch=None):
    path = EXAMPLES / f"{stem}.{language}"
    source = path.read_text(encoding="utf-8")
    output = StringIO()

    def run():
        with redirect_stdout(output):
            if language == "urdu":
                from urdupy.runtime import execute_source
                return execute_source(source, filename=str(path))
            namespace = {"__name__": "__compatibility__", "__file__": str(path),
                         "__builtins__": dict(vars(builtins))}
            exec(compile(source, str(path), "exec", dont_inherit=True), namespace)
            return namespace

    if torch is None:
        namespace = run()
    else:
        with torch_cpu(torch):
            namespace = run()
    return namespace, output.getvalue()


def pair(case, stem, torch=None):
    urdu, urdu_output = execute_example(stem, "urdu", torch)
    python, python_output = execute_example(stem, "py", torch)
    case.assertEqual(urdu_output, python_output, "Urdu and Python stdout differ")
    return urdu, python


class OfflineCase(unittest.TestCase):
    def setUp(self):
        guard = offline()
        guard.__enter__()
        self.addCleanup(guard.__exit__, None, None, None)
