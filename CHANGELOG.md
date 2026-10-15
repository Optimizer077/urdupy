# Changelog

## Unreleased — Complete Urdu dependency surface (2026-10-15)

- Added opt-in `# اردوپائی: مکمل` mode: imports, attributes, parameters, keyword
  arguments, builtins and native class protocols can use Urdu spellings.
  Existing source without the directive retains its behavior.
- Added 763 curated spellings and lossless Urdu-digit spellings for all other
  identifiers and literal strings. Arrays, tensors, modules and autograd stay
  native; dependency messages/data are not implicitly translated.
- Added `اردوپائی`: Urdu commands, discovery and explicit local dependency installs.
- Six zero-Latin-letter examples cover NumPy, vision, SGD/AdamW, checkpoints,
  offline BERT, ResNet-18 and Urdu graphs. Native behavior is tested separately.
- Fixed incomplete parenthesized Urdu from-imports in the console. Encoded
  keyword-shaped native exports and relative module paths remain accessible.
- Final test/artifact evidence is recorded in the URD-031 handoff.

## Unreleased — Documentation and diagrams (2026-10-15)

- Rewrote `README.md` with a banner, a side-by-side Urdu/Python example, a
  highlights table, an architecture block diagram, a keyword cheat sheet, a
  libraries section, results tables and a documentation map. All facts from the
  previous README are kept.
- Added [architecture](docs/architecture.md) (package map, compile pipeline, run
  sequence, import resolution and interpreter-state tables, with Mermaid diagrams),
  [Using Python libraries](docs/python-libraries.md) (environment linking,
  CPU/GPU PyTorch, Urdu file/module naming rules, troubleshooting) and a
  [docs index](docs/README.md).
- Added `docs/assets/urdupy-banner.svg` and `docs/assets/architecture.svg`; the
  sdist manifest now includes `docs/*.svg`. No code, grammar or dependency changes.

## Unreleased — Pip dependency profiles (2026-10-15)

- Added standard `science` and `ai` pip extras. `pip install ".[ai]"` installs
  the scientific, training, NLP and Urdu plotting dependencies automatically.
- The base compiler/runtime keeps zero external runtime dependencies; matching
  preinstalled CPU/CUDA PyTorch builds satisfy the AI profile. No setup hooks,
  import-time downloads, driver installation or public package upload.
- Added packaging metadata regression checks and extras-aware artifact inspection;
  the core suite is now162 tests. New local artifacts live in `dist/pip-extras/`.
- Actually installed the AI extra into `.venv-resnet`; pip retained CUDA wheels
  and installed the missing OpenCV/Transformers packages plus their dependencies.
  Instructions and tested device setup are in [installation](docs/install.md).

## Unreleased — Urdu ResNet on STL-10 (2026-10-15)

- Added a separate Urdu-named experiment with Urdu ResNet/data classes, native
  96x96 full-width ResNet-18 using a small-image stem, and 11,173,962 parameters.
- Completed 50 epochs from scratch on RTX5060Ti, torch2.14.1+cu130. The earliest
  best validation checkpoint (epoch44, 77%) scored 77.35% (6,188/8,000) on the
  separate official test set; training wall time was 23.9 minutes.
- Saved weights, metrics/history, all test predictions, split indices, environment,
  Urdu PNG/SVG curves, confusion matrix, class recall and image predictions.
- Added 22 offline experiment tests and independent raw-label/hash/results audit.
  All pass; 159 core and 11 existing AI tests also pass. Core dependencies and
  language/runtime are unchanged. This is one fixed split, not the ten-fold benchmark.
- All four used labeled data files match official hashes. Unused archive tail
  verification is explicitly false. Inactive partial-download cleanup was rejected
  by automatic approval review and left in ignored scratch directories.
- Existing wheel/sdist artifacts were not rebuilt for this separate experiment.

## Unreleased — Neural training example (2026-10-15)

- Added paired Urdu/Python 600-epoch CPU XOR training with two hidden layers,
  held-out evaluation, saved tensor weights/metrics and exact reload checks.
- Added two optional acceptance tests: the CPU integration suite now passes
  11/11. Core remains 159/159; language/runtime/package dependencies are unchanged.
- Recorded toy-task accuracy 1,021/1,024 (99.71%) and loss 0.703598 → 0.002585.
  See [training instructions](examples/science/README.md#train-a-neural-network).
  Existing dist artifacts predate this example; no new package release was built.

## 0.1.0a1 — Complete local frontend (2026-10-15)

### Added

- Production compiler with 35 Urdu hard keywords, contextual matching, advanced
  function/async/generator syntax and f-string expressions/debug labels.
- Character/source maps, original Unicode syntax diagnostics and compiled spans.
- Real CPython runtime, module-local builtin aliases, script runner and owned
  process state; opt-in `.urdu` modules/packages with standard Python priority.
- CLI run/translate/check/repl, multiline console history, source-cache isolation.
- Nine complete offline CPU scientific/AI integrations and seven paired science
  examples, including actual PyTorch training and a tiny Transformers model.
- Local package metadata/build verification tooling, CI configuration, syntax
  assets, tutorial/reference/security/release/contributor documents.
- Technical language compatibility contract `1.0-local`, separate from the alpha
  distribution version and uncollected community naming evidence.

### Verification and boundaries

159 core tests pass on Python 3.12.13, 3.13.13, 3.14.6 and 3.15.0, Windows AMD64;
nine isolated AI tests pass with no skips. See [current evidence](docs/implementation-handoff.md)
for artifact installation results and exact library versions. No public release
or remote CI execution is claimed. Native template interpolation uses Python
syntax; the preserved M0 experimental API keeps its older documented limitations.

## Unreleased — Phase 1 / M0 (2026-10-15)

- Created the new `urdupy` project from the supplied engineering handbook.
- Designed Python-shaped Urdu grammar, full function signatures and a bilingual
  learning progression, with a naming workshop and human feedback worksheet.
- Recorded 31 experimental keyword mappings, 15 built-in alias names, and six
  deferred advanced candidates. Retained guide spellings; accepted no silent
  alternative synonyms or stable-language guarantees.
- Added a bounded source-span translation experiment, CPython compilation probes,
  namespace fixtures, negative cases and paired Urdu/Python example verification.
- Documented proposed builtins/import contracts, Unicode/RTL considerations,
  official Python/package research, later offline AI tests and phased exit gates.

The local package identifier `0.1.0a1` and spec `0.1-draft` label experiments;
no distribution has been built or released. Exact test evidence and limitations
are in [the handoff](docs/handoff.md). The historical prototype was absent, so
compatibility with its seven tests is **UNVERIFIED**. M1 production translation,
runtime/CLI, M2 `.urdu` imports/diagnostics, AI support and packaging remain later
work. No migration from an installed or released local implementation occurred.
