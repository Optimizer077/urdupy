# Scientific and AI compatibility

URD-031 adds eight complete-Urdu tests: the current full optional suite is
**19/19 PASS, zero skips** in the recorded CPU environment. It covers real
NumPy/vision/offline BERT, exact SGD/AdamW training/checkpoints, native ResNet-18
and Urdu graph export. Name coverage separately audits **13,975 names across
24 namespaces**, not all mathematical operations. See the
[complete Urdu handoff](urdu-only-handoff.md) and local reports under
`dist/urdu-only/`. The original evidence below remains historical.

Date: 2026-10-15. Tasks URD-012..017 and URD-027. Tests use ordinary library names, real
CPython objects, synthetic data and CPU execution. Compatibility claims apply
only to recorded operations and environments, not every API in a framework.

## Run the optional suite

From the project root, with scientific dependencies already installed in the
chosen interpreter:

```powershell
python tools/run_compatibility.py
python tools/run_compatibility.py --require-all --report docs/compatibility-result.json
python -m unittest discover -s tests/compatibility -p "compat_*.py" -v
```

The first command can report `PARTIAL` when optional packages are absent. The
second returns a nonzero status if any fixture is skipped or fails, and saves
exact distribution/module versions and individual outcomes. Ordinary core
`python -m unittest discover -s tests -v` uses `test_*.py`, which leaves this
heavier suite unexecuted. A core-suite pass therefore makes no scientific claim.

`--inventory` reads metadata without importing scientific packages. A missing
package is a skip with its name; a broken installed dependency is an error.

## Acceptance fixtures

| ID / operation | Independent checks beyond Python-path comparison | Files |
|---|---|---|
| AI-001 NumPy | Actual ndarray, int64 `(2, 3)`, exact broadcast result `[[10,22,34],[16,28,40]]`, indexed column and sum 150 | `numpy_arrays.urdu` / `.py`; `compat_arrays.py` |
| AI-002 OpenCV | BGR `[10,20,30]` becomes RGB `[30,20,10]`; gray 22; nearest resize gives exact `(2,2,3)` uint8 data | `opencv_color.urdu` / `.py`; `compat_vision.py` |
| AI-002 Pillow | In-memory PNG roundtrip preserves two RGB pixels, size, mode and uint8 values | `pillow_image.urdu` / `.py`; `compat_vision.py` |
| AI-003 PyTorch | Genuine nn.Module, float64 CPU output -1, loss 1, gradient `[-2,-4]`, SGD weights `[1.2,-0.6]`; new prediction zero | `torch_training.urdu` / `.py`; `compat_torch.py` |
| AI-003 checkpoint | Self-created temporary `state_dict` saves/reloads; restored output equals original; directory removed | `compat_torch.py` |
| URD-027 nonlinear training | Seeded 600-epoch 2-16-16-1 network; loss falls by more than 90%; at least 97% held-out accuracy; four XOR answers; exact Python weights/metrics and checkpoint predictions; CPU RNG/threads restored | `train_xor.urdu` / `.py`; `compat_training.py` |
| AI-004 image to tensor | RGB channel order, float32 scaling by 255, contiguous `(1,3,1,2)`, explicit copied array, Conv2d output `[100,280]/255` | `vision_tensor.urdu` / `.py`; `compat_vision.py` |
| Explicit sharing | A separate contiguous float32 NumPy array shares data with `torch.from_numpy` in both directions | `compat_torch.py` |
| torchvision | Pixel-to-tensor and Normalize values; genuine ResNet18 with no weights, finite `(1,3)` CPU output and Python equivalence | `torchvision_model.urdu` / `.py`; `compat_frameworks.py` |
| AI-005 Transformers | Local config with vocabulary 16, hidden size 8, one BERT layer; genuine model, finite nonzero `(1,3,8)` CPU output and Python equivalence | `transformers_tiny.urdu` / `.py`; `compat_frameworks.py` |

Examples live under [`examples/science`](../examples/science/README.md), with
their separately written Python counterparts. Every paired test compares stdout
as a supplementary check; acceptance depends on numerical objects and properties.
The array and image checks follow actual [NumPy array operations](https://numpy.org/doc/stable/user/quickstart.html),
[OpenCV conversions](https://docs.opencv.org/4.x/d8/d01/group__imgproc__color__conversions.html)
and [Pillow image operations](https://pillow.readthedocs.io/en/stable/reference/Image.html).

For the analytic training case, `w=[1,-1]`, `x=[1,2]`, `y=w.x=-1` and
`loss=y²=1`. Its gradient is `2yx=[-2,-4]`; [SGD](https://docs.pytorch.org/docs/2.14/generated/torch.optim.SGD.html)
with learning rate 0.1 gives `[1.2,-0.6]`. This provides an expectation independent
of translation. float64 comparisons use tolerance `1e-12`; image/tensor float32
checks use explicit tolerances up to `2e-7`. The independently initialized BERT
paths are compared with absolute tolerance `1e-6` after matching CPU seed/state.

## Offline and state policy

Fixtures use local arrays, an in-memory PNG and a temporary self-created
checkpoint. They set offline Hugging Face flags and guard Python socket/DNS APIs.
No test calls a hub download, `from_pretrained`, an external dataset, a camera,
a GUI or a GPU. Guards, environment variables, CPU RNG and thread settings are
restored. This protects the authored test path; it is not an OS network sandbox.

The [torchvision model builder](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet18.html)
is called with `weights=None`. The tiny Transformer uses the documented
[`BertModel(BertConfig(...))` construction](https://huggingface.co/docs/transformers/model_doc/bert#bertconfig).
It needs neither pretrained parameters nor a tokenizer/download. These checks
establish framework execution, not useful language understanding or model quality.

The combined image pipeline explicitly converts color, dtype and layout; it
does not claim zero-copy behavior throughout. Sharing is demonstrated separately
for a deliberately chosen contiguous array.

## Environments observed

| Surface | Default interpreter | Project `.venv-ai` |
|---|---|---|
| Python | CPython 3.13.13, Anaconda | Same CPython via venv |
| OS / architecture | Windows 11 build 26200 / AMD64 | Same host |
| NumPy | 2.5.2 | 2.5.4 local override |
| Pillow | 12.3.0 | 12.3.0 inherited |
| torch | 2.14.1+cpu | 2.14.1+cpu inherited |
| torchvision | Absent | 0.29.1+cpu |
| OpenCV distribution | Absent | opencv-python-headless 5.0.0.93 |
| cv2 imported version | Absent | 5.0.0 |
| Transformers | Absent | 5.19.0 |
| tokenizers / huggingface-hub / safetensors | Absent | 0.23.3 / 2.2.0 / 0.8.0 |

The integrator created `.venv-ai` with `--system-site-packages`. Installed
overrides are project-local; some packages are inherited. It is not described as
a pristine environment. The default interpreter remains distinct, notably with
NumPy 2.5.2. SciPy, pandas, scikit-learn, ONNX and accelerator ecosystems were not
added or certified by these fixtures.

Actual import checks and all seven ordinary Python reference examples passed in
`.venv-ai` under the offline guard. The subsequent nine-test integration run
also passed through the production `urdupy.runtime.execute_source` API.

### Completed integration commands

All commands ran on 2026-10-15 from the project root:

| Exact command | Environment | Actual result |
|---|---|---|
| `./.venv-ai/Scripts/python.exe -u tools/run_compatibility.py --require-all --report tests/compatibility/results-ai.json` | Recorded full CPU tuple | **PASS: 9 tests passed, 0 skipped, 0 failures/errors**; test time 7.5 seconds. |
| `./.venv-ai/Scripts/python.exe -m unittest discover -s tests/compatibility -p "compat_*.py" -v` | Same tuple | **PASS: 9 tests, 0 skips**; confirms direct discovery command. |
| `./.venv-ai/Scripts/python.exe -m pip check` | Same environment | **PASS: no broken requirements found.** |
| `python tools/run_compatibility.py --report tests/compatibility/results-default.json` | Default Python with NumPy 2.5.2/Pillow/torch | **PARTIAL: 5 passed, 4 skipped**, 0 failures/errors; missing cv2, torchvision and Transformers named in skips. |
| `python -m compileall -q tests/compatibility tools/run_compatibility.py examples/science` | Default CPython 3.13.13 | **PASS** for Python source syntax; `.urdu` semantics are covered by the runtime tests above. |
| `./.venv-ai/Scripts/python.exe -X utf8 -m urdupy run examples/science/<name>.urdu`, separately for all seven names in the examples table | Full CPU tuple | **PASS: 7 CLI programs**, each exit 0 with empty stderr and expected numerical/shape output. |

Saved machine-readable evidence: [full CPU run](../tests/compatibility/results-ai.json)
and [default partial run](../tests/compatibility/results-default.json). A skipped
case in the partial run is never counted as framework support. No weights or
external datasets were downloaded by the tests. Initial imports were slower
while caches warmed; the timing above is an observed run, not a performance
guarantee.

The seven CLI names were `numpy_arrays`, `opencv_color`, `pillow_image`,
`torch_training`, `vision_tensor`, `torchvision_model` and `transformers_tiny`.
The displayed `<name>` is a table abbreviation, not literal shell syntax.

## Recreate a compatible environment

Use an isolated environment for installation and current official
[PyTorch device/platform guidance](https://pytorch.org/get-started/locally/).
The upstream [torchvision 0.29.1 release notes](https://github.com/pytorch/vision/releases/tag/v0.29.1)
specifically identify compatibility with PyTorch 2.14.1. The direct-version files
capture this session's Windows CPU choice, not a portable dependency solver result.

For the recorded tuple, in a new compatible CPython 3.13 virtual environment:

```powershell
python -m venv .venv-science
./.venv-science/Scripts/python.exe -m pip install -r requirements/compatibility.txt
./.venv-science/Scripts/python.exe -m pip install -r requirements/compatibility-torch-cpu.txt --index-url https://download.pytorch.org/whl/cpu
./.venv-science/Scripts/python.exe -m pip check
./.venv-science/Scripts/python.exe tools/run_compatibility.py --require-all
```

Install only one OpenCV provider; the recorded environment uses the headless
provider. These files pin direct dependencies and selected framework support
packages; they are not a complete transitive hash lock. Package installation may
need network access; the completed test fixtures themselves run offline.

Other Python versions, operating systems, GPU backends, distributed training,
pretrained models and exports remain unverified until separately tested and
recorded. Core interpreter support and framework wheel support are separate
claims. See [ADR-010](adr/010-ai-environments.md) for the environment policy.

## Subsequent neural-network training run — URD-027

The full optional suite now contains **11 tests**. The earlier nine-test reports
above remain the original checkpoint. The command
`./.venv-ai/Scripts/python.exe -u -X utf8 tools/run_compatibility.py --require-all --report tests/compatibility/results-training.json`
passed **11/11, zero skips/failures/errors**, in 8.422 seconds on the same recorded
Windows CPU environment. [Saved evidence](../tests/compatibility/results-training.json)
includes exact versions and individual outcomes.

The actual Urdu CLI run trained on 2,048 synthetic XOR samples for 600 epochs,
then evaluated 1,024 independently seeded test samples. Training loss fell from
0.7035979629 to 0.0025848681; held-out loss was 0.0102847088 and accuracy was
1,021/1,024 (99.707%). The schedule and hyperparameters were fixed before testing.
The four representative sign combinations were classified as `[0,1,1,0]`.
The saved state reloaded with zero maximum logit error across all test inputs;
a separate fresh Python process also loaded it and predicted correctly.

This is a toy nonlinear classification task, not evidence about real-world
image/language tasks. Full-batch CPU execution uses one thread and seed 42;
no downloaded weights, datasets or accelerator are involved. The new acceptance
tests also check independent labels via negative coordinate product, no shared
train/test rows, finite weights and rejection of nonpositive epoch counts.
See [training and checkpoint instructions](../examples/science/README.md#train-a-neural-network).
