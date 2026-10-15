# Complete local implementation handoff

Latest additive work: [URD-031 complete Urdu dependency surface](urdu-only-handoff.md)
adds 763 spellings, a total identifier/text encoding, Urdu console and six entirely
Urdu examples. Current verification: 230 core tests on four clean installed
minors, 19 offline AI tests, 13,975 namespace names; final artifacts under
`dist/urdu-only/`. Earlier counts below are dated checkpoints.

Date: 2026-10-15. Package **0.1.0a1**; language contract **1.0-local**.
Project/package/command **UrduPy / urdupy**; local distribution
**urdupy-design-lab**. This is the continuation requested after M0, not a rewrite
of its [historical handoff](handoff.md).

## Phase outcomes

| Guide milestone | Local result | Evidence / external boundary |
|---|---|---|
| M0 — Research/design | DONE | Preserved design/naming workshop, official research, historical 57-test lab. |
| M1 — Language core | DONE | Production compiler, 35 hard + 2 contextual words, runtime aliases/runner, real CPython, regression suite. |
| M2 — Modules/diagnostics | DONE | Opt-in modules/regular packages, both language directions, relative/circular imports, resources/reload, Python priority, original source maps and state restoration. |
| M3 — Scientific/AI | DONE on recorded CPU environment | NumPy, OpenCV, Pillow, actual PyTorch autograd/analytic SGD, combined image/tensor path, torchvision. |
| M4 — Advanced use/tools | DONE locally | Tiny offline Transformers model, multiline REPL, tutorial/reference/CLI/RTL guidance, validated editor syntax assets. |
| M5 — Package readiness | DONE locally | Isolated wheel/sdist builds, four-minor clean wheel installs and a separate clean sdist build/install pass; external publishing/hosted results remain separate. |
| M6 — Language contract | DONE for local technical contract | `1.0-local` freezes documented names, grammar, APIs and migrations. Community maturity and wider untested frameworks remain external/future evidence, not fabricated approval. |

## Implemented public surfaces

- `urdupy.translate`, `translate_with_map`, `compile_urdu`; `parse_urdu` in
  `urdupy.compiler`; exec/eval/single compilation and CPython compiler flags.
- `execute_source` / `execute`, `run_path`; genuine objects, copied module-local
  builtins, normal scoping and a real script `__main__` context.
- `install_importer()` returns an idempotent owned context/handle. Package import
  itself installs no hook. `iter_urdu_modules` is explicit discovery.
- `urdupy run`, `translate [-o]`, `check FILE...`, `repl`, `--help`, `--version`;
  equivalent `python -m urdupy` entry point. `check` executes no source/imports.

Python/native/zip concrete specs retain global priority. Regular Urdu initializers
can resolve a standard namespace candidate, while a loose Urdu module cannot
displace that namespace. Imported module identity/caching/failure behavior belongs
to importlib, not a patched `__import__`. See [ADR-013](adr/013-runtime-imports.md).

## Final source verification

After compiler/runtime review repairs, the integrator independently ran:

| Interpreter | Command from project root | Actual result |
|---|---|---|
| CPython 3.12.13, Astral build, Windows AMD64 | Exact installed 3.12 interpreter, `-X utf8 -m unittest discover -s tests -q` | **159/159 PASS, zero skips** |
| CPython 3.13.13, Anaconda, Windows AMD64 | `python -X utf8 -m unittest discover -s tests -q` | **159/159 PASS, zero skips** |
| CPython 3.14.6, Astral build, Windows AMD64 | Exact installed 3.14 interpreter, same suite command | **159/159 PASS, zero skips** |
| CPython 3.15.0, Astral build, Windows AMD64 | `.runtimes/cpython315/python/python.exe -X utf8 -m unittest discover -s tests -q` | **159/159 PASS, zero skips** |

The 159 tests comprise 57 preserved M0 tests, 54 production compiler tests,
15 runtime tests, 18 importer tests and 15 CLI/REPL tests. They cover ordinary
English Python, Urdu grammar/functions/classes/async/generators/matching,
f-string expressions/debug labels, Unicode source spans/errors, attributes,
exports/kwargs, lexical shadowing, actual import metadata and precedence,
packages/resources/circular/repeated/reload/failure cases, argv/path/main/cache
ownership, exit/interrupt handling and interactive source history.

Compilation tests make no scientific dependency or network requirement. Optional
heavy tests use `compat_*.py` and an explicit runner, so routine core discovery
remains small and dependency-free. The five original Urdu/Python example pairs
continue to pass. Packaging verification additionally runs the core suite through
isolated installed package imports, with installed console commands outside the
checkout; CLI unit subprocesses also retain their checkout fixture coverage.

## Scientific/AI evidence

Independent final runner:

```powershell
.venv-ai/Scripts/python.exe -X utf8 tools/run_compatibility.py --require-all --report tests/compatibility/results-ai.json
```

The isolated CPU environment passes **9/9**, zero skips/errors/failures, using
NumPy **2.5.4**, OpenCV-headless distribution **5.0.0.93** (`cv2` **5.0.0**),
Pillow **12.3.0**, PyTorch **2.14.1+cpu**, torchvision **0.29.1+cpu** and
Transformers **5.19.0**. Detailed imported/transitive versions and per-test
results live in the JSON evidence and [AI compatibility](ai-compatibility.md).
All seven science `.urdu` examples also execute through the installed-style CLI.

Checks include real ndarray dtypes/shapes/broadcasting, exact color channels,
independent analytic gradients and SGD weights, state-dict roundtrip, explicit
array/tensor memory sharing, torchvision transforms/model output, and a tiny BERT
configuration with finite expected shape. Local configuration/synthetic data are
used under a Python socket guard. No pretrained weights/datasets, GPU, camera,
network inference or external service is needed.

The default Anaconda environment separately records five passes/four missing-
dependency skips. These results are not conflated with the complete isolated run.
SciPy/pandas/scikit-learn and other untested libraries remain unverified. Base
installation has no scientific dependencies.

## Build and clean-install gate

The maintained [artifact verifier](../tools/verify_release.py) inspects archives,
creates disposable environments, installs the actual wheel on each chosen
interpreter, installs/builds the sdist separately, runs `pip check`, verifies no
NumPy/PyTorch is present, runs the isolated core API suite and exercises installed
run/check/translate/repl commands outside the checkout.

Build command: `.venv-ai/Scripts/python.exe -X utf8 -m build`. It successfully
created `urdupy_design_lab-0.1.0a1-py3-none-any.whl` and
`urdupy_design_lab-0.1.0a1.tar.gz` through build 1.6.1 with isolated setuptools 84.0.0 builds. The wheel
was built from the sdist and contains only the import package and distribution
metadata, not verification environments, scientific libraries or model weights.

The integrator then ran `python -X utf8 tools/verify_release.py` with four
`--python` arguments (the exact 3.12/3.13/3.14/3.15 interpreters above), the two
`--wheel`/`--sdist` artifact paths and `--report dist/verification.json`.

| Actual clean environment | Result |
|---|---|
| Wheel, CPython 3.12.13 | **PASS** — 159 core tests, `pip check`, installed run/check/translate/repl, no NumPy/PyTorch. |
| Wheel, CPython 3.13.13 | **PASS** — the same clean checks. |
| Wheel, CPython 3.14.6 | **PASS** — the same clean checks. |
| Wheel, CPython 3.15.0 | **PASS** — the same clean checks. |
| Separate sdist build/install, CPython 3.15.0 | **PASS** — isolated backend install, the same 159 core tests, dependency and installed-console checks. |

Final artifacts were rebuilt after the source-cache and module-ownership repairs, and
the four clean wheel installs plus separate clean sdist installation were rerun
against those artifacts. The release report records their current hashes.
The generated `dist/verification.json` and `dist/SHA256SUMS` are artifact-side
evidence, intentionally outside the artifacts to avoid self-referential hashes.

The project `.venv` is a ready-to-run core-only local installation of that wheel;
`.venv-ai` holds the independently pinned scientific environment. Both remain
excluded from the distribution artifacts.

## Review repairs retained as regressions

- Relative-only imports and keyword-shaped module/export names select their
  delimiter through CPython parsing, preserving real API spellings.
- Debug f-strings preserve original labels, nested formats and host-specific
  newline/comment behavior, including the CPython 3.12 quirk. Source maps account
  for inserted labels/deleted markers and multiline shifts.
- Loader execution compiles and displays one captured source snapshot rather than
  reading a file twice across a possible edit.
- Runtime/REPL source caches handle LF/CRLF/bare-CR physical lines correctly,
  preserving Unicode separators inside literal data; cache cleanup respects
  entry ownership. A bare-CR regression reproduced the missing original line
  before universal ASCII-newline reading fixed it.
- REPL history uses unique session/input filenames, preserving earlier function
  source even with multiple consoles alive.
- Anonymous execution avoids holding a global script lock while user code runs;
  a worker can execute another Urdu source and finish before its parent joins.
  Script-level argv/path/main swapping remains serialized, not thread-local.
- Anonymous module setup restores a preexisting cache entry if its temporary
  name collides, preserving unrelated interpreter state. The regression runs in
  a fresh process against the actual selected package, including installed copies.
- Reference example compilation uses `dont_inherit=True`, so the verifier's own
  future flags do not alter the compared program's annotations/signature.

## Deliberate limits and external gates

- The source frontend is a tested lexical/context transform validated by CPython;
  the public tokenizer documents guarantees for valid Python input. This remains
  an explicit maintenance risk, not a claim of perfect arbitrary Python coverage.
- Native template strings are preserved; Urdu syntax inside their interpolation
  is explicitly rejected to avoid changing `Interpolation.expression` metadata.
  Compute the value first. English host-only grammar follows its interpreter.
- Temporary anonymous classes do not have a persistent pickle module identity.
  Use proper imported modules for serialization. Concurrent explicit reuse of
  one virtual filename should use a consistent source snapshot.
- Standard `pkgutil` is not monkey-patched; use explicit Urdu discovery. No
  language server, universal debugger integration or full static typing is claimed.
- All actual platform runs are Windows AMD64 normal CPython builds. Twelve CI
  jobs are configured for four minors and three OSes; no remote run is invented.
  Other OSes/architectures/free-threaded builds/GPUs need their own evidence.
- Package remains an alpha distribution. PyPI ownership/registerability, public
  release approval, hosted release execution and native-speaker/community review
  remain external gates. No upload, push or publication occurred.

## Reproduction, continuation and rollback

Start with [README](../README.md), [installation](install.md),
[tutorial](tutorial.md), [reference](language-reference.md), [CLI](cli.md) and
[stability contract](stability.md). The [roadmap](roadmap.md) records completed
local work separately from external gates. `AGENTS.md` is the task-state record.

All project source changes stay in the new `urdupy` folder; sibling projects and
the original attachment are unchanged. Additional CPython 3.14.6 was installed in
uv's user-managed interpreter cache; 3.15.0 was extracted under `.runtimes`.
Existing system Python packages were not modified. Local verification environments/runtimes/build caches
are excluded from packages. Revert a focused production change while retaining
its regression before any release; do not silently rewrite the versioned grammar.
Publication remains a separate maintainer action, not an implicit side effect of
the completed local implementation goal.

Final text audit: **36 Markdown files / 137 local file links** resolve, and
**51 Python/Urdu source files** contain no literal Unicode format controls.
Saved editor JSON, metadata TOML and CI YAML parse. This is a file/logic check,
not a claim that every editor, terminal or unrun operating system was inspected.

## Subsequent user task — Neural-network training (URD-027)

Added `examples/science/train_xor.urdu` and an independent Python counterpart.
The 337-parameter 2-16-16-1 network trains for 600 CPU epochs on 2,048 locally
generated samples before evaluating a separate 1,024-sample test set. Actual
training loss: 0.703598 → 0.002585; test accuracy: 1,021/1,024 (99.71%). This
measures a synthetic sign-XOR task only. The schedule was fixed before evaluation.

`runs/xor/model.pt` and `metrics.json` hold the completed local run; `runs/` is
ignored output. Loading tensor state reproduces all test logits exactly; an
independent fresh process also performed inference from the saved weights.
The [example README](../examples/science/README.md#train-a-neural-network) documents
training, options and model usage. CPU RNG and thread counts are restored after
training. No language/runtime/package metadata changes were needed.

Fresh baseline and final core runs: 159/159, zero skips. Focused optional tests:
2/2. Full optional CPU suite: 11/11, zero skips, with numerical Python equivalence,
independent label/split assertions and saved checkpoint checks. Evidence is
`tests/compatibility/results-training.json`; the earlier nine-test reports remain
historical. Five core example pairs and dependency-free CLI compile check also
passed. The new demo is verified with Python 3.13.13 / torch 2.14.1+cpu on Windows
AMD64. Existing wheel/sdist artifacts predate this source/example addition and
were not rebuilt for this task. No publication occurred.

## Subsequent user task — Urdu ResNet / STL-10 (URD-028)

Created `experiments/ریسنیٹ_ایس_ٹی_ایل۱۰/` with seven `.urdu` modules. Production
classes are `بنیادی_بلاک`, `ریس_نیٹ` and `تصویری_مجموعہ`; image category labels,
plots, reports, key folders and function names are Urdu. Required library/protocol
names stay intact. Three agents independently owned model, data and graphs;
integrator implemented training/integration and reviewed the real artifacts.

The full-width ResNet-18 has [2,2,2,2] blocks, a 3x3 stride1 small-image stem
without initial maxpool, 11,173,962 parameters and native96x96 inputs. Actual
training ran50epochs from scratch on the detected RTX5060Ti16GB, taking
1432.159seconds (23.9min), in separate `.venv-resnet` with official CUDA13 wheels.
The earlier `.venv-ai` CPU environment and system packages remain unchanged.

Official labeled data:4000fit/1000validation from the5000 train split, stratified
400/100 per class; official8000 test untouched until validation-only checkpoint
selection. Fit-only mean/std, seeded crop/flip augmentation, SGD0.05/momentum0.9/
weight_decay0.0005, cosine schedule, AMP/GradScaler, seed42. Earliest best validation
epoch44 scored77%; its final test score is **77.35% (6188/8000)** with loss0.756061.
This is one fixed supervised split, not the official ten-fold benchmark.

`نتائج/ابتدائی_تربیت/` contains complete metadata, split indices, per-epoch JSON/CSV,
all8000 predictions, best weights, last optimizer state, environment versions,
four Urdu PNG/SVG figure pairs and a generated Urdu results document. The integrator
visually inspected all four final PNGs: connected Urdu text/digits, complete labels,
no clipping, count/percentage scales and positive/negative prediction examples.
SVGs decode as valid XML with embedded glyph paths; no separate SVG browser visual
pass is claimed. The first two official images of each class form the20-image grid;
selection never depends on correctness.

Independent `نتائج_جانچیں.urdu` audit passed: all four raw labeled source MD5s,
exact test-label order, complete/disjoint/stratified train/validation indices,
all8000 predictions, confusion counts and accuracy, earliest maximum validation
epoch, source/checkpoint SHA256, image decoding and SVG structure. Reloading weights
has exact test-batch logits. Separate fresh-process CPU inference from the saved
weights succeeded, including Urdu top3 names. Inference's tensor-resize path was
fixed/tested before the final source inventory; active training source stayed frozen.

Verification:159core tests,11 existing optional AI tests,22 new experiment tests,
seven dependency-free compile checks and new-environment pip check all pass. Exact
versions are saved in `ماحول.json`; actual audit evidence is `تصدیق.json` and the
existing-AI report `اردوپائی_مطابقت.json`. The tiny synthetic CPU pipeline fixture
initially stalled in native oneDNN backward; a restoring test-only native-CPU context
resolved it. Actual GPU training does not use that CPU backend path.

Used labeled files individually match official hashes. The unused unlabeled archive
tail was stopped, never used or claimed verified. Automatic approval review rejected
recursive partial-download cleanup with `blocked by policy`; inactive scratch remains
under singular `experiment/` and `ڈیٹاسیٹ/حصے/`, both ignored. Active source/data is
under plural `experiments/`. No source publication or wheel/sdist rebuild occurred.
Reproduction, inference and graph/audit commands are in the experiment's Urdu README.

## Subsequent user task — Pip installation and dependency extras (URD-029)

The user requested automatic setup dependencies and installation using pip.
Added standard `science` and `ai` extras to pyproject metadata; the base compiler,
runtime and CLI still have zero active external requirements. The science
profile installs NumPy/Pillow/headless OpenCV; AI adds matching torch/torchvision,
Transformers, Matplotlib and Urdu reshaper/bidi helpers. Pip resolves dependencies;
there are no setup hooks, import-time installers, automatic datasets or weights.
Device-specific wheel selection stays explicit and compatible existing builds
are accepted. [ADR-014](adr/014-pip-extras.md) records the decision.

Actual `.venv-resnet/Scripts/python.exe -m pip install ".[ai]"
--report dist/pip-ai-install.json` succeeded, installed missing packages and
retained torch2.14.1+cu130/torchvision0.29.1+cu130. Installed console and `python -I`
imports were checked outside the source folder; CUDA remains available and
`pip check` passes. Full optional compatibility suite11/11 passes, zero skips,
in that installed AI environment. A new clean `.venv-science-install` installed
the built wheel's `[science]` extra automatically; all three imports/pip check
pass and torch is absent. `.venv` has the updated core wheel installed.

Three metadata regression tests bring the core suite to162. Updated
`tools/verify_release.py` inspects real wheel extras/markers while requiring zero
active base dependencies. Clean wheel installs on3.12.13/3.13.13/3.14.6/3.15.0
and a separate clean source build/install on3.15 each pass162core tests, pip check,
no-science-library assertions and installed run/check/translate/repl commands.
New artifacts and final hash/report evidence are under `dist/pip-extras/`;
old `dist/` reports remain historical. Direct pins reproduce recorded versions,
not every platform's wheel availability or a complete transitive lock. The source
archive is refreshed after documentation, with final artifact verification.

No grammar/runtime/model source changes, system Python installation, PyPI
publication or distribution rename occurred. From the checkout a user can run
`python -m pip install .`, `python -m pip install ".[science]"` or
`python -m pip install ".[ai]"`. Registry-only `pip install urdupy` is not the
published command for this local project. [Installation](install.md) contains
tested local/wheel and CPU/CUDA commands.

## Public source repository — URD-030 (2026-10-15)

The maintainer explicitly requested a public repository and selected the local
GitHub account **Optimizer077**. Source is now published at
[Optimizer077/urdupy](https://github.com/Optimizer077/urdupy), with `main` as the
default branch and local `origin/main` tracking configured. The initial source
commit is `841399b5ad6f39350ca1d16bcd9270e617e37539` (128 files). Anonymous GitHub
API requests verified public visibility, the README and the remote main SHA;
`git ls-remote --heads origin main` matched the local commit independently.

Fresh pre-publication checks on CPython 3.13.13 / Windows:

- `python -X utf8 -m unittest discover -s tests -q`: **162 PASS, zero skips**.
- `python -X utf8 examples/verify_examples.py`: **five pairs PASS**.
- Upload inventory: no secret-pattern findings or credential filenames; no file
  larger than 1 MB. Existing ignore rules exclude local environments, runtimes,
  datasets, checkpoints, generated training output and build artifacts.

An anonymous shallow clone into an ignored `.verification/public-clone-*`
directory independently passed the same 162 tests and five example pairs,
verifying that the uploaded source is complete and works after Git checkout.

The [first hosted CI run](https://github.com/Optimizer077/urdupy/actions/runs/38685274655)
is in progress. Its result remains pending; this is
separate from the local passing baseline. README now includes clone/install
instructions and a link to actual workflow results. No implementation, language,
dependency, PyPI publication, release or tag changes were made. Earlier statements
that no source push occurred describe their historical sessions. Next: inspect
hosted CI, retaining the remaining package-ownership and community gates.
