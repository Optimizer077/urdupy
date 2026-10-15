# Paired Phase 1 examples

Each `.urdu` file has a Python counterpart with the same identifiers, data and
observable result. The Python files run directly with CPython; `.urdu` files use
the **experimental** compiler plus an explicit alias namespace supplied by the
verifier. No public runner, `.urdu` import loader or AI dependency is required.

| Pair | Purpose | Important checked behavior |
|---|---|---|
| `01_conditions` | Branches, truth and absence | Equal lists are distinct objects; None differs from an empty list. |
| `02_loops` | Iteration, comprehension and while | Exclusive range end; skip, break and while-condition polarity. |
| `03_functions` | Ordinary/advanced arguments | `/`, defaults, `*args`, keyword-only, bare `*`, `**kwargs`, unpacking, TypeError, return/output, pass and fresh-list default. |
| `04_stdlib` | Actual Python imports | `math.sqrt`, `statistics.mean`, `collections.Counter`; external names unchanged. |
| `05_classes` | Classes and protocols | `__init__`, `__len__`, `__iter__`, classmethod, staticmethod and property. |

From the project root:

```powershell
python examples/verify_examples.py
python -X utf8 examples/01_conditions.py
```

`verify_examples.py` executes both files in a pair, compares stdout, recursively
compares values **and their types**, checks against explicit expected results,
compares the function signatures, and checks that the global built-ins namespace
is unchanged. Comparing types prevents `True`, `1` and `1.0` from accidentally
being treated as equivalent evidence. Each program receives a fresh copied
built-ins dictionary; Urdu aliases refer to genuine Python built-ins.

The `-X utf8` flag on the direct sample command selects UTF-8 for standard output
on Windows terminals that otherwise use an encoding such as CP1252. The verifier
captures Urdu output internally and prints ASCII result summaries.

Verified on 2026-10-15, Windows, using the locally available interpreters:

| Command | Actual interpreter | Result |
|---|---|---|
| `python examples/verify_examples.py` | CPython 3.13.13 | PASS: all 5 pairs, stdout, typed results, 5 function signatures, independent default-created lists, unchanged global built-ins. |
| `py -3.11 examples/verify_examples.py` | CPython 3.11.9 | PASS: the same 5 pairs and checks. |
| `python -X utf8 examples/01_conditions.py` | CPython 3.13.13 | PASS: prints `بالغ` followed by `True False True`. |

An initial verifier run failed because the verifier's own future-annotations
flag was inherited by plain Python compilation. The harness now uses
`dont_inherit=True` for the reference file. This correction compares each
program's actual source semantics rather than relaxing signature comparison.

A successful run proves these particular programs in that environment, not full
grammar compatibility. No package/interpreter combination outside these actual
runs is certified by this example table.

The [language design](../docs/language-design.md) contains five beginner reading
exercises and a clearly marked **design-only** PyTorch comparison. Reader
responses belong in the [blank feedback worksheet](../docs/naming-proposals.md#reader-feedback-worksheet--not-yet-conducted);
there is no claimed usability survey.
