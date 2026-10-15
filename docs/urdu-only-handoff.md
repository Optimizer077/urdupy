# URD-031: Complete Urdu dependency source surface

The maintainer requests PyTorch, NumPy and all dependency names without English,
and parallel agents. This expands the early charter non-goal. Five phases:
baseline/contracts; parallel catalog/CLI/examples; compiler/runtime integration;
native behavior/coverage review; clean packaging and installed verification.

## Contract

A leading `# اردوپائی: مکمل` enables reserved library spellings in imports,
attributes, names, stores, parameters, keyword labels and protocol definitions.
There are 763 curated entries: 39 modules, 521 members, 79 builtins, 36 values,
88 protocols. Every other identifier has an exact `اصل_` Urdu-digit spelling.
Arbitrary strings have `متن_` spellings decoded by `اصل_متن`; unusual attribute
and import names, dictionary keys and options remain reachable without English.

`اردوپائی` provides Urdu commands/help, complete-mode REPL, explicit local pip
profiles and name discovery. `نام --کتب_خانے` enumerates discoverable importable
roots, including filesystem namespace packages, without importing them. Custom
finders without enumeration cannot be exhaustively listed; exact spellings still
work. No import/check installs dependencies. Native arrays, tensors, autograd,
modules and subclasses remain real backend objects. Original mode stays compatible.

## Evidence

Starting clean worktree `eed8d2a`, CPython3.13.13/Windows AMD64: 162 core tests
and five paired examples PASS. Three agents held separate catalog, CLI/verifier
and examples/test scopes; integrator owned compiler/runtime/docs. A separate
agent independently reviewed integration and added 15 regressions.

Core: **230 PASS, zero skips** on clean wheel installations on CPython3.12.13,
3.13.13, 3.14.6 and 3.15.0, plus a separate clean 3.15 sdist build/install.
Both consoles, complete Urdu execution/discovery/REPL and nonexecuting checks pass
outside the checkout with optional libraries absent. The authoritative artifact
hashes and runs are in `dist/urdu-only/verification.json` and `SHA256SUMS`.

`.venv-ai/Scripts/python.exe -u -X utf8 tools/run_compatibility.py --require-all
--report dist/urdu-only/ai-compatibility.json` -> **19/19 PASS, zero skips**:
NumPy/linalg, exact image pixels, SGD/AdamW/analytic gradients/native weight
equality/checkpoints, torchvision, offline tiny BERT, full native ResNet-18
architecture/forward/backward/step/reload. All six example sources have zero ASCII
letters, including comments/docstrings/strings. All six also ran as real main
programs. Four complete-mode README/guide snippets executed and contain no Latin.

AI tuple: Python3.13.13, NumPy2.5.4, torch2.14.1+cpu, torchvision0.29.1+cpu,
OpenCV-headless5.0.0.93, Pillow12.3.0, Transformers5.19.0, Matplotlib3.11.2,
arabic-reshaper3.0.1, python-bidi0.6.11; Windows AMD64 CPU; offline fixtures.

`tools/verify_urdu_surface.py --report dist/urdu-only/namespace-audit.json`
in the AI environment -> **13,975 names / 24 namespaces PASS**. Every recorded
`dir()` name has identifier AST-lowering/text-roundtrip evidence; all nine direct
AI dependencies and major tensor/array/model/optimizer/transform types are covered.
This is name coverage, not a claim to execute every mathematical operation.
Catalog agent separately roundtripped all 1,114,112 Unicode codepoints as text
and 136,945 valid single-codepoint identifiers. Boundary/malformed/collision tests
remain in the suite. Independent review verified incomplete REPL from-imports,
escaped keyword-shaped native exports and encoded relative imports.

Actual graph: `runs/urdu-only/تربیتی_نقصان.png`, inspected by example agent and
integrator: joined Urdu title/labels and Urdu numerals. Synthetic AdamW120-step
loss **3.7798399925231934 -> 0.0000015165301192610059**. The earlier STL-10
77.35% result/checkpoints remain historical, unchanged and unretrained.

The final wheel is installed in `.venv` and `.venv-resnet`. An isolated process
outside the checkout imported the installed package and executed a zero-Latin
Urdu program on CUDA: native linear model, forward, scalar loss and finite
backpropagated gradients. CUDA0 available, torch2.14.1+cu130 retained. Evidence:
`dist/urdu-only/local-gpu-install.json`. This is a small GPU smoke test; the full
optional differential suite above is CPU evidence.

## Boundaries and rollback

Fallbacks are exact numeric Urdu spellings, not human translations of all terms.
Native messages, exceptions, repr/data and external documentation retain original
text. User source need not contain English dependency names or option values.
Unavailable C signatures limit automatic argument discovery. Non-NFKC/unusual
attributes use exact-text `خاصیت_لو`. Curated vocabulary is provisional; no human
naming acceptance is invented. No public upload is part of this task.

Implementation: `urdupy/urdu_surface.py`, `urdu_catalog.py`, small compiler/
runtime/importer/REPL integrations, CLI and Unicode console in pyproject. Tests:
`test_urdu_catalog.py`, `test_urdu_surface.py`, `test_urdu_surface_review.py`,
`test_urdu_cli.py`, `compat_urdu_only.py`. Examples: `examples/مکمل_اردو/`.
Guide: `docs/complete-urdu.md`, ADR-015. Tools audit namespaces and clean installs.
Final artifacts: `dist/urdu-only/`, separate from historical builds. Rollback
removes this additive surface/catalog/console/examples and preserves original mode.
