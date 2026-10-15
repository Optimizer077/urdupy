# ADR-010: Optional CPU environments and offline compatibility evidence

- **Date:** 2026-10-15
- **Status:** Implemented fixture/environment policy; integration evidence recorded separately
- **Owner:** Scientific compatibility agent; integration by the project owner
- **Tasks:** URD-012..017
- **Affected interfaces:** Optional test environments, scientific examples, compatibility reporting

## Context and options

UrduPy must execute genuine NumPy/OpenCV/PyTorch objects through CPython. Adding
every scientific framework to its base requirements would make a small language
frontend expensive to install and couple it to native wheel/device constraints.
Conversely, import-only checks or skipped optional tests cannot establish that
Urdu functions/classes actually work with those frameworks.

Considered options:

1. Put scientific packages in base dependencies and use online pretrained demos.
   This introduces unnecessary downloads/device assumptions and weakens routine
   reproducibility.
2. Record only successful imports in the existing interpreter. This is useful
   inventory, but proves neither translation nor numerical behavior.
3. Keep a dependency-free core, create optional isolated CPU environments, and
   compare offline Urdu/Python fixtures with explicit value/shape/dtype checks.
   This is the implemented policy.

## Decision

**URD-029 addition:** [ADR-014](014-pip-extras.md) now defines standard `science`
and `ai` extras for automatic pip dependency resolution. This retains the
dependency-free core and opt-in device selection described here; the old direct
requirements files remain recorded environment inputs.

Keep all scientific frameworks out of base package requirements. Run optional
`compat_*.py` tests explicitly through `tools/run_compatibility.py`; ordinary
`test_*.py` core discovery does not load heavy libraries. Include
`tests/compatibility/__init__.py` so the explicit recursive pattern discovers
the suite reliably.

Skip only when the requested optional module and its known distributions are
absent. An installed distribution with no importable module, an import error,
or an incompatible native operation is a failure/error requiring investigation.
`--require-all` makes any skipped required fixture a nonzero run. A partial run
reports `PARTIAL`, never full compatibility.

Use synthetic arrays/images and CPU tensors. Construct torchvision models with
`weights=None`; construct a tiny BERT from local `BertConfig`. No test calls
`from_pretrained`, accesses a camera, starts a GUI, downloads datasets or requests
model weights. Python network socket/DNS entry points are patched to fail during
each test; offline environment variables are set and restored. This is a fixture
guard, not an OS-level network sandbox or a claim about every native library.

Use a fixed analytic autograd/SGD example in float64, fixed input values, and
independent expected results. Broader models compare separately written Python
paths plus shape, dtype, finite values and relevant operation expectations.
Scope CPU random state and thread changes using `torch.random.fork_rng` and
cleanup. Save only self-created state dictionaries in temporary directories;
load them with `weights_only=True` and `map_location="cpu"`.

## Version/environment evidence

The existing default interpreter initially supplied NumPy 2.5.2, Pillow 12.3.0
and torch 2.14.1+cpu. The integrator created a project-local `.venv-ai` using
`--system-site-packages`; installed overrides give that environment NumPy 2.5.4,
opencv-python-headless 5.0.0.93, Transformers 5.19.0 and torchvision 0.29.1+cpu.
Inherited packages are explicitly acknowledged: this is isolated installation
scope, not a claim of a pristine dependency environment.

The upstream [torchvision 0.29.1 release](https://github.com/pytorch/vision/releases/tag/v0.29.1)
explicitly declares compatibility with PyTorch 2.14.1 and relaxes its requirement
to `torch>=2.14`. Older installation tables observed during this session stop at
2.13/0.28; the specific release provides the newer evidence. Successful local
imports and numerical tests are still required; the release note alone is not
an UrduPy compatibility test.

Record distribution versions and actual imported module versions separately:
for example the OpenCV distribution is `5.0.0.93`, while `cv2.__version__` is
`5.0.0`. Do not infer accelerator support from a CPU wheel or one availability
check. Exact completed commands/results belong in
[`ai-compatibility.md`](../ai-compatibility.md).

## Dependency inputs and reproduction

[`requirements/compatibility.txt`](../../requirements/compatibility.txt) pins
direct scientific dependencies for this recorded Windows/CPython environment.
[`compatibility-torch-cpu.txt`](../../requirements/compatibility-torch-cpu.txt)
is installed separately from the official PyTorch CPU wheel index. Avoid adding
multiple competing OpenCV providers. These are direct-version inputs, not a
complete hash-locked transitive dependency graph or a cross-platform promise.

For a new platform, use official [PyTorch installation guidance](https://pytorch.org/get-started/locally/),
select matching wheels, run `pip check`, and record actual fixture results before
adding a compatibility claim. Framework environments may use a different Python
minor from the newest core-language target.

## Compatibility impact, rollback and limits

The production runtime/compiler API is exercised as supplied; no framework API
names are translated. `__init__`, `forward`, `.backward`, `.parameters`,
`.state_dict`, `torch.nn.Linear`, `cv2.cvtColor` and NumPy members remain genuine
Python interfaces.

Rollback only the newly added optional tests, science examples, runner, dependency
inputs and this documentation. Remove a disposable environment only after
verifying its project-local absolute path. Never uninstall or replace system
libraries as part of test cleanup. No model files or release artifacts are
published by this workflow.

GPU training, pretrained inference, distributed jobs, exporters, every model
architecture, untested library versions and other platforms remain outside the
recorded evidence. Optional science tests cannot ratify Urdu keyword usability or
stable language spellings.
