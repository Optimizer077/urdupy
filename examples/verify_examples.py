"""Differential checks for the five owned Phase 1 example pairs.

This is a source-checkout example verifier, not a public execution API or sandbox.
Run from the project root with: python examples/verify_examples.py
"""

from __future__ import annotations

import builtins
from contextlib import redirect_stdout
from inspect import signature
from io import StringIO
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urdupy.experimental import compile_urdu  # noqa: E402
from urdupy.lexicon import BUILTIN_ALIASES  # noqa: E402


EXPECTED = {
    "01_conditions": {
        "category": "بالغ",
        "equal_values": True,
        "same_distinct": False,
        "same_alias": True,
        "missing": True,
        "empty_is_missing": False,
        "booleans": [True, False],
        "logic": True,
    },
    "02_loops": {
        "kept": [1, 2, 4],
        "sum": 7,
        "squares": [1, 4, 9],
        "countdown": [3, 2, 1],
    },
    "03_functions": {
        "bill": {"amount": 195, "label": "کتاب"},
        "default": {"amount": 100, "label": "عام"},
        "unpacked": {"amount": 95, "label": "عام"},
        "greeting": "خوش آمدید سارہ",
        "fresh_lists": [[1], [2]],
        "output_returns_none": True,
        "pass_returns_none": True,
        "argument_errors": ["TypeError", "TypeError"],
    },
    "04_stdlib": {
        "root": 9.0,
        "mean": 4,
        "counts": {"a": 2, "b": 1},
        "length": 3,
    },
    "05_classes": {
        "items": ["کتاب", "قلم"],
        "length": 2,
        "property": 2,
        "valid": True,
        "empty_length": 0,
        "instance": True,
    },
}

EXPECTED_STDOUT = {
    "01_conditions": "بالغ\nTrue False True\n",
    "02_loops": "[1, 2, 4] 7\n[1, 4, 9] [3, 2, 1]\n",
    "03_functions": "کام مکمل\n195 کتاب\nخوش آمدید سارہ\n",
    "04_stdlib": "9.0 4\n{'a': 2, 'b': 1} 3\n",
    "05_classes": "['کتاب', 'قلم'] 2\nTrue True\n",
}


def compare_typed(actual: Any, expected: Any, path: str = "RESULT") -> None:
    """Compare nested values without treating True, 1 and 1.0 as equivalent."""
    if type(actual) is not type(expected):
        raise AssertionError(
            f"{path}: type {type(actual).__name__} != {type(expected).__name__}"
        )
    if isinstance(expected, dict):
        if list(actual) != list(expected):
            raise AssertionError(f"{path}: dictionary keys/order differ")
        for actual_key, expected_key in zip(actual, expected):
            compare_typed(actual_key, expected_key, f"{path}.key")
            compare_typed(actual[actual_key], expected[expected_key], f"{path}[{expected_key!r}]")
    elif isinstance(expected, (list, tuple)):
        if len(actual) != len(expected):
            raise AssertionError(f"{path}: sequence lengths differ")
        for index, (left, right) in enumerate(zip(actual, expected)):
            compare_typed(left, right, f"{path}[{index}]")
    elif actual != expected:
        raise AssertionError(f"{path}: {actual!r} != {expected!r}")


def execute(path: Path) -> tuple[dict[str, Any], str]:
    source = path.read_text(encoding="utf-8")
    namespace: dict[str, Any] = {
        "__name__": "__example__",
        "__file__": str(path),
        "__builtins__": dict(vars(builtins)),
    }
    if path.suffix == ".urdu":
        namespace["__builtins__"].update(
            {alias: getattr(builtins, target) for alias, target in BUILTIN_ALIASES.items()}
        )
        code = compile_urdu(source, filename=str(path))
    else:
        # Judge the example's future imports, not this verifier's annotations flag.
        code = compile(source, str(path), "exec", dont_inherit=True)
    output = StringIO()
    with redirect_stdout(output):
        exec(code, namespace)
    return namespace, output.getvalue()


def verify_all() -> tuple[str, ...]:
    """Raise on failure; return the checked stems for integration tests."""
    original_builtins = dict(vars(builtins))
    verified = []
    for stem, expected in EXPECTED.items():
        urdu, urdu_output = execute(ROOT / "examples" / f"{stem}.urdu")
        python, python_output = execute(ROOT / "examples" / f"{stem}.py")
        compare_typed(urdu["RESULT"], python["RESULT"], f"{stem}.differential")
        compare_typed(urdu["RESULT"], expected, f"{stem}.expected")
        if urdu_output != python_output or urdu_output != EXPECTED_STDOUT[stem]:
            raise AssertionError(f"{stem}: stdout differs from equivalent Python or expectation")
        if stem == "03_functions":
            for name in ("بل", "سلام", "شامل_کرو", "صرف_دکھاؤ", "عارضی"):
                if signature(urdu[name]) != signature(python[name]):
                    raise AssertionError(f"{stem}: function signature changed: {name}")
            if urdu["پہلی"] is urdu["دوسری"]:
                raise AssertionError(f"{stem}: None-default lists share an object")
        verified.append(stem)
    if dict(vars(builtins)) != original_builtins:
        raise AssertionError("example execution mutated the process builtins namespace")
    return tuple(verified)


def main() -> None:
    for stem in verify_all():
        print(f"PASS {stem}: stdout, typed results and applicable function contracts")
    print("PASS 5 example pairs; global builtins unchanged")


if __name__ == "__main__":
    main()
