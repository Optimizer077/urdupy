# Offline scientific examples

Each `.urdu` example has an independent `.py` counterpart. Packages, library
attributes, `__init__` and `forward` keep their actual Python spellings. Optional
dependencies belong in a compatible environment; they are not base requirements.

| Example | Operation |
|---|---|
| `numpy_arrays` | Urdu function transforms a genuine array with broadcasting. |
| `opencv_color` | Synthetic BGR/RGB/gray conversion and nearest resize. |
| `pillow_image` | Two-pixel in-memory PNG roundtrip. |
| `torch_training` | Real Urdu-defined nn.Module, analytic gradient and SGD. |
| `vision_tensor` | Color/layout/dtype conversion and a tiny convolution. |
| `torchvision_model` | Pixel transforms and ResNet18 with `weights=None`. |
| `transformers_tiny` | Tiny local-config BERT; no pretrained weights/tokenizer. |
| `train_xor` | 600-epoch nonlinear classifier, held-out evaluation and saved weights. |

With the runtime CLI and scientific environment available, from the project root:

```powershell
python -X utf8 -m urdupy run examples/science/numpy_arrays.urdu
python -X utf8 -m urdupy run examples/science/torch_training.urdu
python -X utf8 -m urdupy run examples/science/transformers_tiny.urdu
python tools/run_compatibility.py --require-all
```

Use the relevant environment's Python executable, such as
`./.venv-ai/Scripts/python.exe`, when dependencies are installed there. Direct
example runs use local data/configuration and make no intentional network calls.
The compatibility suite additionally enforces its Python socket guard, scopes
the CPU seed/thread settings and compares both language paths numerically.

`torch_training` fixes its weights/input: output -1, loss 1, gradient `[-2,-4]`,
then SGD produces weights `[1.2,-0.6]`. `vision_tensor` converts to RGB and
float32 `[0,1]`, then permutes HWC to CHW and adds the batch axis for NCHW. Copies along this
pipeline are intentional. The sharing test in the suite is a separate controlled
NumPy/tensor example.

Framework constructors use local random initialization, not useful pretrained
models. These examples demonstrate integration, not model quality, accelerator
support or every library API. Exact completed commands and environment versions
are recorded in [AI compatibility](../../docs/ai-compatibility.md).

## Train a neural network

`train_xor.urdu` trains a real 337-parameter PyTorch network with two hidden
layers: **2 → 16 → 16 → 1**, tanh activations, Adam and binary cross-entropy
with logits. Urdu declares the class, functions, loop and context managers;
PyTorch's `forward`, `.backward()` and optimizer APIs keep their original names.

From the project root, using the existing CPU environment:

```powershell
.\.venv-ai\Scripts\python.exe -X utf8 -m urdupy run examples/science/train_xor.urdu -- --output runs/xor
```

Two random coordinates in `[-1, 1)` produce label 1 when their signs differ,
and 0 when they agree. Training uses 2,048 samples; the fixed 600-epoch schedule
finishes before evaluation on 1,024 separately generated test samples. The test
set does not select hyperparameters or stopping time. Seed 42 fixes initialization;
seeds 43 and 44 generate the two splits.

The recorded CPU run reduced training loss **0.703598 → 0.002585** and classified
**1,021/1,024 test samples correctly (99.71%)**. All four representative XOR
answers were correct. These are toy-task results, not real-world model accuracy.

The command saves `runs/xor/model.pt` (tensor `state_dict`) and `metrics.json`
(configuration, loss history, accuracy, versions and SHA256 hashes). It reloads
the checkpoint with `weights_only=True` and verifies exact predictions on the
test inputs. `runs/` is a local output directory excluded from version control;
rerunning with the same output replaces these two generated files. Use a new
`--output` directory to keep another experiment; `--epochs` and `--seed` are
optional. Reproducibility is verified in the recorded CPU environment, not
guaranteed bit for bit across different hardware or library versions.

The independent Python counterpart is `train_xor.py`. Optional acceptance tests
compare its full trained weights and metrics against the Urdu path, check that
the splits have no shared rows, and verify serialization. Run them with:

```powershell
.\.venv-ai\Scripts\python.exe -X utf8 -m unittest tests.compatibility.compat_training -v
```

To use the saved network from Python, from the project root:

```python
import runpy
import torch

example = runpy.run_path("examples/science/train_xor.py")
model = example["عصبی_نیٹ"]()
model.load_state_dict(torch.load("runs/xor/model.pt", map_location="cpu", weights_only=True))
model.eval()
with torch.no_grad():
    probabilities = model(torch.tensor([[-0.75, 0.75], [0.75, 0.75]])).sigmoid()
print(probabilities)  # near 1 and near 0
```
