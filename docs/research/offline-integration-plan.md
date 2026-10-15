# M3 offline scientific integration plan

Status: **HYPOTHESIS / NOT RUN**. These are proposed acceptance tests after M1
translation and M2 runtime/import contracts pass. They are not examples of
already supported UrduPy library behavior.

## Environments and evidence

Use separate, disposable CPU test environments for core-only, NumPy, vision, and
PyTorch. Keep the base package free of scientific dependencies. Record the exact
Python, OS/architecture, distribution versions, wheel sources, UrduPy revision,
commands, and outcomes. Reconsult official installation guidance when building
those environments; this design session establishes no compatible version tuple.

Do not install anything or download weights for M0. Missing optional dependencies
mean **SKIP** with a reason; an incompatible available environment means **FAIL**
or **BLOCKED**, not support. Check base-package behavior in a core-only environment.
Choose one OpenCV provider for a vision environment; do not place competing `cv2`
providers together. PyTorch device/runtime choices belong to its environment.

For each fixture, execute Urdu and Python equivalents under the same interpreter
and compare actual objects and numeric results, not only printed output. Preserve
`numpy`, `cv2`, `torch`, `__init__`, `forward`, and public library attributes.

## Proposed fixtures

| ID | Small input and operation | Required assertion |
|---|---|---|
| AI-001 | `np.arange(6, dtype=np.int64).reshape(2, 3)`; Urdu function doubles and broadcasts a fixed length-three array | Genuine `np.ndarray`; exact shape/dtype and element equality with Python; indexing and sum match |
| AI-002 | One-pixel BGR array `[[[10, 20, 30]]]`, `dtype=np.uint8`; `cv2.cvtColor(..., cv2.COLOR_BGR2RGB)`; a fixed resize | RGB exactly `[30, 20, 10]`; expected array shape and uint8 dtype; equal Python result; no GUI/files/camera |
| AI-003 | Urdu class subclasses `torch.nn.Module`; one `nn.Linear(2, 1, bias=False)` with explicit fixed weights, fixed CPU input and target; squared scalar loss | `isinstance` genuine module; known output; finite nonzero gradient; `SGD.step()` changes expected weights and matches Python |
| AI-004 | Small synthetic BGR NumPy image -> RGB -> contiguous float array -> tensor -> channel reorder -> tiny fixed layer | Exact channel order and shapes; documented dtype/range; Python-equivalent tensor/output with explicit tolerance |

AI-003 should include an independent analytic expected gradient, so two identical
translation errors cannot pass solely by comparison. Use fixed parameter values
and a fixed target that guarantees nonzero gradients; a seeded random model alone
is less explicit. Start in CPU float64 when supported by the chosen operations,
record tolerances, and use `optimizer.zero_grad()` between steps. Save/reload via a
temporary local `state_dict` fixture only after the minimal training case works.

For AI-004, make any array copy explicit. Do not casually claim zero-copy sharing
after color conversion, channel reordering, or dtype conversion. An optional
separate test may verify sharing with a chosen contiguous array. Test `torchvision`
separately with its matching environment and no pretrained downloads.

## Official API references

- [NumPy quickstart](https://numpy.org/doc/stable/user/quickstart.html) explains
  array shape, dtype, indexing, reshape, and broadcasting used by the plan.
- [OpenCV color conversions](https://docs.opencv.org/4.x/d8/d01/group__imgproc__color__conversions.html)
  documents the real `cvtColor` operation and color-conversion constants.
- [PyTorch autograd tutorial](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)
  documents backward computation and gradient tracking; fixture design still
  needs execution against the exact installed version.

**OPEN:** Exact mutually installable Python/NumPy/OpenCV/PyTorch/torchvision
versions and platforms. No wheel compatibility, accelerator behavior, or network
installation was verified. Transformers and pretrained inference stay in M4 and
separate opt-in demonstrations.
