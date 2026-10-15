# Python and package research — Phase 1

Research date: **2026-10-15**. Owner: research agent, URD-002 and M0
distribution research. This is a design record, not a release support promise.

Evidence labels used throughout this directory:

- **VERIFIED:** directly observed command output or an identified official source.
- **HYPOTHESIS:** proposed UrduPy behavior awaiting implementation and tests.
- **OPEN / UNVERIFIED:** evidence or a decision is still missing.

## Official release evidence

**VERIFIED:** The [Python download index](https://www.python.org/downloads/)
identified 3.15.0 as the newest stable series on retrieval. Its
[release page](https://www.python.org/downloads/release/python-3150/) explicitly
labels it stable and gives a publication date of **2026-10-09**. The previous
series' [3.14.8 release page](https://www.python.org/downloads/release/python-3148/)
gives **2026-09-30**. Source retrieval began at **2026-10-15 00:32:56 UTC**;
retrieval time and release publication dates are different facts. These dates
are consistent with the workspace date. No inferred future release is used.

The download index also listed 3.13.16, 3.12.15, and 3.11.17. These index entries
do not mean those patch releases are installed here. Recheck the official index
at release time; this note deliberately records a dated observation.

## Actual local observations

Commands ran from the project directory, before research-file edits:

```powershell
python -c "import sys, platform; print(sys.version); print(platform.platform()); print(platform.machine())"
py -3.11 -c "import sys, platform; print(sys.version); print(platform.platform()); print(platform.machine())"
python -m unittest discover -s tests -v
```

| Interpreter | Exact observation | Result |
|---|---|---|
| Default `python` | `3.13.13`, packaged by Anaconda, Inc.; build `main, Apr 14 2026, 06:12:50`; `MSC v.1942 64 bit (AMD64)` | VERIFIED inventory |
| `py -3.11` | `3.11.9`, build `tags/v3.11.9:de54cf5, Apr 2 2024, 10:12:12`; `MSC v.1938 64 bit (AMD64)` | VERIFIED inventory |
| Default platform | `Windows-11-10.0.26200-SP0`, `AMD64` | VERIFIED observation |
| 3.11 platform string | `Windows-10-10.0.26200-SP0`, `AMD64` | VERIFIED output on the same machine; retain the reported string |
| Initial discovery | `Ran 0 tests`, `NO TESTS RAN`, exit code **1** | Empty baseline; no feature pass |

The integrator owns subsequent project-suite results. Those results belong in
the final handoff and handbook matrix, not in this earlier empty-baseline row.
No Linux, macOS, ARM, GPU, clean installation, or scientific-library integration
was tested by this research task.

## The tokenizer boundary matters

**VERIFIED:** Python's [3.12 porting notes](https://docs.python.org/3.12/whatsnew/3.12.html#porting-to-python-3-12)
describe f-string tokenization changing from one `STRING` to
`FSTRING_START`, `FSTRING_MIDDLE`, and `FSTRING_END`, with expression tokens
between them. The same document explains that Python 3.12 lifted restrictions
on quote reuse, comments, and backslashes in replacement expressions.
[PEP 701](https://peps.python.org/pep-0701/) supplies the design rationale and
notes that debug expressions preserve their original expression text.

**VERIFIED locally:** For `value = f"start {x + 1} end"`, 3.11.9 returned one
`STRING` token for the f-string; 3.13.13 returned the three f-string token kinds
and individual expression tokens. Run the reproducible observation:

```powershell
python docs/research/probe_environment.py
py -3.11 docs/research/probe_environment.py
```

**HYPOTHESIS:** A host-version adapter with explicit f-string state can preserve
literal portions and translate only supported expression contexts. One scanner
path should not be presumed equivalent on both tokenizer families. Debug
expression labels and nested format fields require dedicated fixtures.

**VERIFIED limitation:** The [public tokenizer documentation](https://docs.python.org/3.13/library/tokenize.html)
only promises behavior for syntactically valid Python. Urdu keyword syntax is
not valid Python before translation. Successful probes on that input are bounded
empirical evidence, not a documented guarantee from CPython. The tokenizer's
`untokenize` round-trip guarantee covers token kinds and strings, not unchanged
spacing or columns. Source preservation needs span edits and separate tests.

**OPEN:** 3.14 introduces [template string literals](https://docs.python.org/3.14/whatsnew/3.14.html#pep-750-template-string-literals).
3.15 adds [lazy import syntax using a soft keyword](https://docs.python.org/3.15/whatsnew/3.15.html#pep-810-explicit-lazy-imports).
These need explicit English pass-through and context fixtures before either minor
enters a support claim. No Urdu aliases for these constructs are proposed here.

## Proposed validation matrix

This is a test plan. `UNVERIFIED` does not mean supported.

| Target | Purpose | Current evidence | Next gate |
|---|---|---|---|
| CPython 3.11.9 / Windows AMD64 | Older tokenizer comparison | Inventory and research probe ran | Integrator's bounded suite; full M1/M2 suites later |
| CPython 3.13.13 Anaconda / Windows AMD64 | Current local experiment | Inventory and research probe ran | Integrator's bounded suite; clean upstream build later |
| CPython 3.12 latest patch | First new f-string tokenizer | UNVERIFIED locally | Run same fixtures; do not infer from 3.13 |
| CPython 3.14.8 | Prior stable series, template strings | Official release only; UNVERIFIED locally | Core and version-specific syntax fixtures |
| CPython 3.15.0 | Latest stable, highest-priority new runner | Official release only; UNVERIFIED locally | Core, lazy-import, syntax, runtime/import fixtures |
| Linux/macOS x86-64; ARM64 where available | Filesystem, RTL, native wheels | UNVERIFIED | Independent CI rows with exact versions |

**Proposed policy:** M0 publishes no supported Python range. M1 should add a
version only after a clean environment passes its claimed feature suite. 3.15
is the desired current target; reaching it is not accomplished by researching it.
Keep `requires-python`, classifiers, badges, and support prose aligned with that
decision. Tool-only project configuration can exist without installable project
metadata. See [ADR-008](../adr/008-python-versions.md).

## Distribution name observations

The browser fetcher could not render the PyPI JSON endpoints. A direct HTTPS
request with PowerShell `Invoke-WebRequest -SkipHttpErrorCheck` succeeded in
observing the following responses on 2026-10-15:

| Official endpoint | HTTP status | Body | Interpretation |
|---|---|---|---|
| [urdupy JSON](https://pypi.org/pypi/urdupy/json) | 404 | `{"message": "Not Found"}` | No project metadata returned |
| [urdupy-design-lab JSON](https://pypi.org/pypi/urdupy-design-lab/json) | 404 | `{"message": "Not Found"}` | No project metadata returned |

The [PyPI JSON API documentation](https://docs.pypi.org/api/json/) defines the
project metadata endpoint. **OPEN:** Neither response proves the name can be
registered, is legally clear, belongs to this user, or remains free tomorrow.
[PyPI's name guidance](https://pypi.org/help/#project-name) explains that names
can be unavailable despite no visible release, including prohibited, confusing,
or already registered names without releases. No registration was attempted.

**HYPOTHESIS:** Keep **UrduPy** as the project/language name and `urdupy` as the
local import package. Reserve `urdupy-design-lab` only as an explicitly provisional
distribution candidate. [Distribution and import names are distinct](https://packaging.python.org/en/latest/discussions/distribution-package-vs-import-package/).
Under [PyPA normalization](https://packaging.python.org/en/latest/specifications/name-normalization/),
hyphens, underscores, and periods normalize alike; spelling `UrduPy` with capital
letters does not create a different registry identity. See
[ADR-009](../adr/009-distribution.md) for release and migration gates.

No package was installed, built, published, reserved, or uploaded by this task.
