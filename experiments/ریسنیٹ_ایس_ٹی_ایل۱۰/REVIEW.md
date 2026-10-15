# Independent implementation review

Reviewed the model, dataset, training and inference source while the 50-epoch
CUDA run was active. The initial review was read-only. A subsequent isolated fix
changed only the inference helper, which training never imports. Training,
model, dataset and plotting source remained frozen; run outputs were untouched.
The official test set was not evaluated as part of this review or fix.

No material defect was found affecting the recorded configuration: width 64,
96×96 input, 50 epochs, batch size 64, CUDA with float16/float32 autocast.

- Training and validation losses multiply each batch mean by its sample count
  before dividing by the total; accuracy uses total correct predictions.
- The 4,000/1,000 training/validation split is disjoint and stratified. Channel
  normalization statistics use only the 4,000 training images.
- Checkpoint selection uses validation accuracy, retaining the first epoch on
  ties. The official 8,000-image test set is evaluated after training and selection.
- The saved weights are a tensor `state_dict` with Urdu module names. Inference
  reconstructs width and class count from the report and explicitly loads on CPU.
- Checkpoint verification compares two evaluation-mode float32 models after
  loading the same weights. It does not overwrite the earlier mixed-precision
  test predictions or claim CPU and CUDA outputs are bitwise identical.
- The final state includes optimizer, scheduler, scaler and generator states;
  the documentation correctly avoids claiming an automatic resume interface.
- Relative CLI paths resolve from the caller's current directory. Default data
  and results paths resolve from the experiment directory.

The review identified and fixed a bounded preprocessing inconsistency for
resized configurations such as 48×48: PIL resizing before tensor conversion
differed from dataset preparation's uint8 tensor resizing by at most one
intensity level in a synthetic test. `پیشگوئی.urdu` now uses the Urdu helper
`تصویر_تیار_کرو`: PILToTensor → antialiased uint8 tensor Resize →
ConvertImageDtype(float32) → Normalize. This matches the dataset path exactly.
The active run's native 96×96 STL-10 inputs were unaffected by the original
inconsistency, and the training implementation remains unchanged.

Executed `.venv-ai/Scripts/python.exe -X utf8
experiments/ریسنیٹ_ایس_ٹی_ایل۱۰/test_inference.py -v`: **2/2 PASS** in 1.627 s.
The checks prove exact normalized tensor equality with `اعداد.جسامت_بدلو` at
48×48 and 96×96, and exercise the inference entry point with a dummy classifier,
captured input tensor, CPU checkpoint loading and three ordered Urdu class
names/probabilities. They use synthetic PNG images, not official test data or
trained weights.

Existing executed model evidence: five offline model tests passed, including
eight residual blocks, real gradients, projection math, checkpoint reload and
exact output agreement with a torchvision ResNet-18 using the same small-image
stem and transferred weights. This review itself did not rerun training or
validate a final accuracy, because the actual run was still active.
