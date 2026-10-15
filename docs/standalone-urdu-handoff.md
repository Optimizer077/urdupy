# URD-032: Standalone complete Urdu training

The main README now teaches standalone `.urdu` applications through `اردوپائی`.
It no longer embeds Urdu strings inside a Python host program. A two-file Urdu
example imports a sibling Urdu module directly. The existing Python API remains
available for interoperability. CPython and native scientific libraries still
provide execution; this change does not implement an independent VM.

## Implemented scope

Three agents owned model/data/inference, training, and plotting/audit. The
integrator owned the library vocabulary, shared docs, public result export and
cross-module checks. All fifteen `.urdu` sources under `examples/مکمل_اردو/`
contain zero ASCII letters, including comments and strings. The seven new modules
under [the STL-10 workflow](../examples/مکمل_اردو/ایس_ٹی_ایل۱۰/README.md) cover
the complete process with Urdu class names, constructors, forward methods,
arguments, optimizer calls, CLI help, labels and saved report keys.
The catalog now contains 881 entries: 41 modules, 627 members, 79 builtins,
46 values and88 protocols. Existing exact fallback spellings remain available.

The model is a native full-width ResNet-18 with a 3x3 small-image stem and
11,173,962 parameters. Initialization, strict historical checkpoint loading and
logits match the original model exactly. Data preparation verifies four labeled
binary file hashes, reproduces orientation, the stratified 4,000/1,000 split
and training-only normalization. The 8,000 test examples are held out until
validation selects the earliest best checkpoint. Explicit `--حاصل` enables
initial data download; ordinary tests remain offline.

Training uses native momentum SGD, cosine scheduling and GPU AMP where selected.
It saves weights, full optimizer/scheduler/scaler/RNG state, history, all test
predictions, split indices, environment, sample images and source hashes. Saved
state is not a promise of a resume CLI. Audit independently checks the recorded
predictions, selection, hashes and checkpoint architecture; recorded forward
reload parity is reported separately. Replotting uses the saved image cache and
does not need the dataset.

## Actual new training run

The following standalone command completed successfully using existing verified
STL-10 data and the installed package:

```powershell
.venv-resnet/Scripts/اردوپائی.exe چلاؤ examples/مکمل_اردو/ایس_ٹی_ایل۱۰/تربیت.urdu -- --اعداد experiments/ریسنیٹ_ایس_ٹی_ایل۱۰/ڈیٹاسیٹ --نتائج runs/مکمل_اردو_ریسنیٹ_جانچ_۳۲ --ادوار 1 --بیچ 64 --جسامت 96 --چوڑائی 64 --تھریڈ 6 --آلہ گرافیکی
```

RTX 5060 Ti, torch2.14.1+cu130, CPython3.13.13/Windows AMD64:

| Measurement | Observed |
|---|---|
| Full-width parameters / image size | 11,173,962 / 96x96 |
| Train / validation / test count | 4,000 / 1,000 / 8,000 |
| Epochs / best epoch | 1 / 1 |
| Training loss / accuracy | 2.2751248512 / 21.875% |
| Validation accuracy | 20.7% |
| Test accuracy | 1,728 / 8,000 = 21.6% |
| Training epoch wall time | 29.3965023 seconds |
| Forward reload difference | 0.0 |
| Best weight SHA-256 | `4a20f7c57af5f096c848080aeca7b353609261fcf3639ae3f2f2c271395eb8e0` |

The standalone `جانچ.urdu` and `دوبارہ_خاکے.urdu` commands also passed on these
real artifacts. Four PNG/SVG pairs were rendered and visually inspected: joined
Urdu titles, axes, numerals and all ten classes, with correct image examples.
The one-epoch run checks integration; it is separate from the earlier trained
model's accuracy. Local weights/data/run outputs remain ignored.

## Preserved 50-epoch result

[Tracked results](نتائج/ریسنیٹ/README.md) include all four original PNG/SVG
pairs, all fifty history rows, class metrics and a compact Urdu JSON summary
with hashes. The export reconciled all 8,000 saved predictions with original
test labels, four raw file MD5s, disjoint split indices, earliest best epoch,
checkpoint SHA-256 and seven historical source hashes. No historical source or
checkpoint was modified. The new Urdu model's loaded output matches that model.

The earlier run scored **6,188/8,000 = 77.35%**, with best validation epoch44 at
77%, after fifty epochs and 23.9 minutes. Its checkpoint SHA-256 is
`9dd5eed6d09b9701b7ce2ff9c1ae89f6c0f45faf0df2bb28698de5b5525fe32c`.
This is one fixed split, not the ten-fold protocol. It was not rerun for fifty
epochs after this source change. `tools/export_resnet_results.py` reproduces
the public snapshot from the existing local data and artifacts.

## Verification and packaging

Fresh pre-edit baseline: 230 core tests and22 historical experiment tests PASS.
Current executed checks, zero skips:

```powershell
python -X utf8 -m unittest discover -s tests -q
.venv-ai/Scripts/python.exe -X utf8 -m unittest discover -s examples/مکمل_اردو/ایس_ٹی_ایل۱۰ -p test_*.py -q
.venv-ai/Scripts/python.exe -X utf8 tools/run_compatibility.py --require-all --report dist/standalone-urdu/ai-compatibility.json
```

These report **234 core**, **27 workflow** and **19 optional AI** tests PASS.
All22 historical tests were also rerun after integration and PASS. Strict old/new
model and data parity are covered by the new suite. Core contracts enforce zero ASCII
letters, direct Urdu imports, README compilation and public metric/plot hashes.
Five legacy paired examples pass. All six README Urdu code blocks were actually
executed through the installed console outside the checkout; this caught and
fixed a short-example method spelling. Its100-step AdamW loss ends at
0.00037186252302490175. Evidence: `dist/standalone-urdu/readme-execution.json`.

New artifacts and release verification belong under `dist/standalone-urdu/`.
`tools/verify_release.py` verifies both console entry points, no base runtime
dependencies, the complete sdist workflow and all public result assets. Repeated
`--python` arguments select installed 3.12/3.13/3.14/3.15 interpreters; the tool
installs the wheel on each and separately builds/installs the sdist on the last.
It writes exact artifact hashes, installed paths, test summaries and outcomes
to `verification.json` and `SHA256SUMS`.
Clean wheel installation, all234 core tests, both consoles, `pip check` and
isolated package imports PASS on3.12.13,3.13.13,3.14.6 and3.15.0. Separate
clean3.15 sdist build/install and all234 tests also PASS. Optional science/AI
libraries are absent from these core verification environments.

Rollback removes the additive examples, catalog entries, result export/assets
and README changes; the existing compiler/runtime/importer API is unchanged.
The implementation initially remained local. A subsequent explicit maintainer
`push it` instruction authorizes publishing this source/docs/results update to
GitHub. No registry upload is requested.
