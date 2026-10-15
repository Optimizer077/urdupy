# Install the local UrduPy prerelease

The local distribution is **`urdupy-design-lab`**; its import package and command
are both **`urdupy`**. Install from this checkout or its built artifacts. No PyPI
publication, name reservation or registry ownership is claimed. The dated
[registry observations](research/python-and-packaging.md) are research only.

The package's interpreter envelope is **CPython 3.12–3.15**. The local core suite
passed on **3.12.13, 3.13.13, 3.14.6 and 3.15.0**, all on the recorded Windows
AMD64 host. Exact commands, builds and feature results are in the
[implementation handoff](implementation-handoff.md). Linux/macOS and other
architectures remain unverified. Twelve CI jobs are configured across four minors
and three operating systems; configuration does not establish remote pass results.

The built wheel passed clean installation, 159 core tests and installed CLI
checks on each recorded minor; the source archive separately passed its build
and clean installation on 3.15.0. Those environments had no NumPy/PyTorch and
passed `pip check`. See [release evidence](release.md) for the artifact checks.

## Install from the checkout

Select your intended Python explicitly, then create an environment. Windows:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install .
.venv\Scripts\python -m urdupy --version
.venv\Scripts\python -m urdupy --help
```

Linux/macOS, with a suitable installed `python3.13`:

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/python -m urdupy --version
```

The build frontend may fetch the small setuptools build backend. The installed
core has **zero required runtime dependencies** and does not install NumPy,
OpenCV, PyTorch or model weights. Use `pip install -e .` instead when developing
against this source tree. Activating the environment is optional when using its
explicit Python path; after activation, `urdupy` is the equivalent console entry.

If the required backend is already installed in a controlled offline environment,
`python -m pip install --no-deps --no-build-isolation .` avoids an isolated build
download. This requires `setuptools>=77.0.3` in that environment. Record the actual
backend/frontend versions when reproducing a release build.

## Automatic dependency installation

From the `urdupy` checkout, choose the features you want:

| Command | Pip installs |
|---|---|
| `python -m pip install .` | UrduPy compiler/runtime/CLI; no external runtime dependencies. |
| `python -m pip install ".[science]"` | UrduPy plus NumPy, Pillow and one headless OpenCV provider. |
| `python -m pip install ".[ai]"` | Science libraries plus torch, torchvision, Transformers, Matplotlib, arabic-reshaper and python-bidi. |

Pip resolves these declared dependencies and their transitive requirements
automatically using standard [packaging extras](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#dependencies-and-requirements).
No custom setup.py, import-time installer or source scanning is involved. A user
program that imports other libraries still needs those libraries installed in the
usual way. Selecting an extra does not download datasets or pretrained weights.

The direct versions match the working Windows/Python3.13 environments. Availability
of native wheels on other interpreters/platforms is separate from the core's
Python envelope. These pins are not a complete transitive hash lock. Prefer a
virtual environment; avoid co-installing both OpenCV providers that supply `cv2`.

### CPU or CUDA PyTorch

The AI extra uses public-version requirements and leaves device/index choice to
pip. To request the recorded CPU builds explicitly, install them first, then the
extra from the ordinary configured index:

```powershell
python -m pip install torch==2.14.1+cpu torchvision==0.29.1+cpu --index-url https://download.pytorch.org/whl/cpu
python -m pip install ".[ai]"
```

For the recorded Windows/RTX5060Ti CUDA13.0 environment:

```powershell
python -m pip install torch==2.14.1+cu130 torchvision==0.29.1+cu130 --index-url https://download.pytorch.org/whl/cu130
python -m pip install ".[ai]"
```

Matching `+cpu` and `+cu130` builds satisfy the extras' public-version pins, so
pip can retain that installed build. The actual AI-extra install retained
torch2.14.1+cu130/torchvision0.29.1+cu130 with CUDA available. A new machine should
select its build using [official PyTorch guidance](https://pytorch.org/get-started/locally/);
setup does not infer the device, install drivers or choose a CUDA runtime for it.

The current project-local installations are `.venv` for the core and `.venv-resnet`
for the complete AI extra. Use their explicit Python/console paths or activate
the intended environment. It is not installed globally into system Python.

### Install the new local artifacts

The extras-aware artifacts are in `dist/pip-extras/`, preserving earlier artifact
reports in `dist/`. A wheel accepts an extra on its path:

```powershell
python -m pip install "dist/pip-extras/urdupy_design_lab-0.1.0a1-py3-none-any.whl[ai]"
```

Use `--force-reinstall --no-deps` when deliberately replacing an older local
wheel with the same prerelease version in an existing core environment; pip may
otherwise treat it as already installed. Fresh environments avoid that ambiguity.

## Install a built wheel (core only)

The prerelease wheel is named like
`urdupy_design_lab-0.1.0a1-py3-none-any.whl`. Use the exact file in your local `dist`
directory rather than asking a package index for a similarly named project:

```powershell
python -m pip install --no-deps dist/urdupy_design_lab-0.1.0a1-py3-none-any.whl
python -m pip check
python -m urdupy --version
```

Do not co-install the historical `urdupy-demo` and this distribution into the same
environment; different distribution names can provide conflicting `urdupy` files.
A fresh virtual environment gives a clearer migration than overwriting an unknown
prototype installation. Uninstall this build with
`python -m pip uninstall urdupy-design-lab`.

## First program

Save UTF-8 text as `hello.urdu`:

```urdu
نام = "دنیا"
دکھاؤ("سلام", نام)
```

Then run:

```powershell
python -m urdupy check hello.urdu
python -m urdupy run hello.urdu
```

See [CLI](cli.md), [tutorial](tutorial.md), and [local editor support](../editor/README.md).
If the terminal cannot display Urdu glyphs, select a font and UTF-8 output setup
appropriate to it; `python -X utf8 -m urdupy ...` selects Python's UTF-8 mode.
Saving valid UTF-8 source and rendering glyphs are separate concerns.

Scientific/AI environments are optional and independently versioned. Use the
[AI compatibility record](ai-compatibility.md) for actual tested combinations,
reproduction commands and missing-dependency outcomes. UrduPy does not choose a
GPU runtime or promise that all scientific wheels support every interpreter/OS.
