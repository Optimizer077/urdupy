"""Audit every discoverable name in selected real dependency namespaces.

This checks the total spelling mechanism, not every mathematical operation of
the dependency. Native execution is separately tested in compat_urdu_only.py.
"""

import argparse
import ast
import importlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urdupy import compile_urdu
from urdupy.urdu_catalog import encode_identifier, decode_identifier, encode_text, decode_text
from urdupy.urdu_surface import DIRECTIVE


NAMESPACES = (
    "numpy", "numpy.ndarray", "numpy.linalg", "numpy.fft", "numpy.random",
    "torch", "torch.Tensor", "torch.nn", "torch.nn.functional", "torch.optim",
    "torch.utils.data", "torchvision", "torchvision.models", "torchvision.transforms",
    "cv2", "PIL.Image", "PIL.Image.Image", "matplotlib", "matplotlib.pyplot",
    "transformers", "transformers.BertConfig", "transformers.BertModel",
    "arabic_reshaper", "bidi.algorithm",
)


def resolve(path):
    parts = path.split(".")
    value = importlib.import_module(parts[0])
    for part in parts[1:]:
        try:
            value = getattr(value, part)
        except AttributeError:
            value = importlib.import_module(f"{value.__name__}.{part}")
    return value


def audit(paths=NAMESPACES):
    import keyword
    import unicodedata
    namespaces, errors, total = [], [], 0
    for path in paths:
        try:
            value = resolve(path)
            names = sorted(set(dir(value)))
            identifiers = [name for name in names if name.isidentifier() and not keyword.iskeyword(name)
                           and unicodedata.normalize("NFKC", name) == name]
            # Check all attributes in one AST, including private/native protocols.
            source = DIRECTIVE + "\nنتیجہ = [" + ",".join("شے." + encode_identifier(name) for name in identifiers) + "]\n"
            assert not any(c.isascii() and c.isalpha() for c in source)
            tree = compile_urdu(source, flags=ast.PyCF_ONLY_AST)
            translated = [node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)]
            if translated != identifiers:
                raise AssertionError("AST attribute spellings do not match the native namespace")
            for name in names:
                assert decode_text(encode_text(name)) == name
                if name in identifiers:
                    assert decode_identifier(encode_identifier(name)) == name
            namespaces.append({"namespace": path, "status": "PASS", "names": len(names),
                               "identifier_spellings": len(identifiers),
                               "text_spellings": len(names), "all_names": names})
            total += len(names)
        except Exception as error:
            namespaces.append({"namespace": path, "status": "FAIL", "error": f"{type(error).__name__}: {error}"})
            errors.append(path)
    versions = {}
    for name in ("numpy", "torch", "torchvision", "opencv-python-headless", "Pillow", "matplotlib",
                 "transformers", "arabic-reshaper", "python-bidi"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return {"status": "FAIL" if errors else "PASS", "python": sys.version, "platform": platform.platform(),
            "versions": versions, "names_checked": total, "namespaces": namespaces,
            "scope": "Every dir() name in the listed installed namespaces; AST lowering plus exact text/identifier roundtrips.",
            "limitations": "Dynamic undiscoverable names remain expressible by the same codec; this is not an exhaustive operation/numerical-correctness claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    # All fixtures and configurations are local. Guard Python socket APIs during
    # optional imports just like the compatibility suite.
    from tests.compatibility._support import offline
    with offline():
        result = audit()
    arguments.report.parent.mkdir(parents=True, exist_ok=True)
    arguments.report.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']}: {result['names_checked']} names across {len(result['namespaces'])} namespaces")
    for row in result["namespaces"]:
        if row["status"] != "PASS":
            print(row)
    return int(result["status"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
