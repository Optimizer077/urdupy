# Local prerelease and publication checklist

This checkout provides built and locally verified **`urdupy-design-lab 0.1.0a1`**
wheel and source artifacts.
The CLI/import package is `urdupy`; the source extension is `.urdu`. No PyPI or
TestPyPI upload, remote push, hosted release, or registry ownership is implied.
The scoped technical language contract is **`1.0-local`** and the metadata permits
CPython **3.12–3.15** after local Windows core checks on all four minors. Package
prerelease status and uncollected external naming feedback remain separate.
The final actual command/version results are recorded in
[implementation-handoff.md](implementation-handoff.md).

**URD-029 update:** Extras-aware artifacts now live in `dist/pip-extras/`;
the original `dist/verification.json` below is the earlier159-test, no-extras
checkpoint. New wheel installs on the same four Windows interpreter versions
and a separate3.15 source install pass162core tests each, pip check and installed
CLI commands. Conditional extra requirements do not become core dependencies.
The updated verifier evaluates requirements with no extra selected and checks
the `science`/`ai` profiles. Actual selected-extra installs also passed: science
in a clean3.13 environment and AI in the project GPU environment, retaining CUDA.
See `dist/pip-extras/verification.json`, the pip install reports and
`ai-compatibility.json` for current evidence. No upload was performed.

## Build locally

Use a supported Python in a dedicated build environment. With network access
available for small build tools:

```powershell
python -m pip install "setuptools>=77.0.3" build
python -m build --outdir dist/pip-extras
```

The outputs are a pure-Python wheel and source archive in `dist/`. The wheel
contains the `urdupy` package plus metadata/license. The sdist also carries
tests, examples, documentation, editor assets, tooling and the engineering
handbook through `MANIFEST.in`. Do not put environments, downloaded weights,
credentials, caches, or sibling projects into either archive.

When the frontend is unavailable but the configured backend is installed, a
controlled local backend invocation can exercise the same build hooks:

```powershell
python -c "import setuptools.build_meta as b; b.build_sdist('dist'); b.build_wheel('dist')"
```

Record which method actually ran. An unrun `python -m build` command is not a
successful frontend test just because direct backend hooks succeeded.

The recorded build used
`.venv-ai/Scripts/python.exe -X utf8 -m build`, with build frontend **1.6.1**.
The wheel's `WHEEL` metadata identifies the isolated generator as
**setuptools 84.0.0** and the tag as `py3-none-any`. It was built from the sdist.
The frontend environment's own installed setuptools version is not substituted
for the isolated generator version.

## Validate artifacts

Create separate clean environments for wheel and sdist tests. Install the exact
local artifact with `--no-deps`, then run `pip check`, version/help, a small script,
checking/translation, and imports from a directory outside this checkout.
Confirm `urdupy.__file__` points into the validation environment. Test the console
entry and `python -m urdupy`; neither should accidentally import source from the
working directory. Rebuild the sdist and inspect required source/doc files.

Retain final archive hashes and exact build/backend/frontend versions in the
handoff. Local Windows success is not a Linux/macOS result. A `py3-none-any` tag
describes wheel contents; it does not prove every platform was exercised.

## Completed local artifact verification

The integrator ran `tools/verify_release.py` against the actual artifacts and
saved **PASS** evidence in `dist/verification.json`, with matching hashes in
`dist/SHA256SUMS`. The packaging agent independently inspected both archives,
checked those hashes against the report, and compared every wheel Python source
file with the frozen working-tree package. The wheel has the intended name,
version, MIT license expression, `>=3.12,<3.16` requirement, console entry point
and no `Requires-Dist` runtime dependencies. Its members are only `urdupy/` and
distribution metadata. The source archive includes tests and saved evidence,
examples, docs, tools, the supplied handbook and standalone editor assets; no
environment, runtime download, build output or bytecode-cache path was present.

| Clean install | Actual recorded result on Windows AMD64 |
|---|---|
| Wheel, CPython 3.12.13 | **PASS** — 159 core tests, zero skips, `pip check`, installed CLI and isolated import |
| Wheel, CPython 3.13.13 | **PASS** — same checks |
| Wheel, CPython 3.14.6 | **PASS** — same checks |
| Wheel, CPython 3.15.0 | **PASS** — same checks |
| Separate sdist build/install, CPython 3.15.0 | **PASS** — same checks after building the source artifact in its installation environment |

Each environment contained neither NumPy nor PyTorch. Installed console
`run`, `check`, `translate` and `repl` were exercised outside the checkout;
the imported package path resolved inside the validation environment. Core API
tests used isolated interpreter imports. The CLI unit suite also retains its
separate checkout-based subprocess fixtures; these are not confused with the
installed console checks. The project `.venv` additionally provides a ready-to-run
core wheel installation.

The final documentation refresh rebuilds and rechecks the source archive while
retaining the same tested wheel bytes. Artifact-side evidence records the final
hashes; it stays outside the archives to avoid self-referential checksums. Do not
infer a remote or non-Windows result from these local checks.

## Readiness ledger

| Gate | Status | Evidence and boundary |
|---|---|---|
| Grammar/functions/compiler/runtime/imports/CLI/REPL | **PASS locally** | 159 core tests, zero skips on all four recorded Windows minors; exact commands and limits in implementation handoff |
| Scientific/AI behavior | **PASS for recorded CPU tuple** | 9 tests, zero skips and `pip check`; actual versions and operations in [AI compatibility](ai-compatibility.md) |
| Wheel/sdist builds, archives and clean installation | **PASS locally** | Four clean wheel installs and separate 3.15.0 sdist build/install above; actual artifact hashes in `dist/verification.json` and `dist/SHA256SUMS` |
| Docs/license/security/contribution | **DELIVERED** | Saved source documents and local link audit; public ownership/legal review remains separate |
| Editor assets | **JSON VALIDATED** | Local syntax assets delivered; visual editor/RTL rendering **UNVERIFIED** |
| Local technical language contract | **FROZEN: `1.0-local`** | Delegated design decision with versioned regression contract, not a community maturity claim |
| Cross-platform CI | **CONFIGURED / REMOTE UNVERIFIED** | Twelve jobs; Linux/macOS and remote execution have no recorded pass |
| Naming feedback | **NOT COLLECTED** | External native-reader/community validation remains open |
| Public distribution name/legal/ownership | **OPEN** | Recheck registry and maintainer review before publication |
| Public release authorization | **NOT GIVEN for publication** | The all-phases instruction authorized local implementation, not an upload |

## Before any public upload

The maintainer must choose/review the final public name, ownership and licensing;
review the supplied handbook's redistribution terms separately from new original
project code;
provide real project/support/security URLs; review release notes and documented
support; execute intended hosted CI jobs and resolve failures; inspect final
artifacts and install them cleanly; and explicitly authorize the publication.
Use a reviewed secret-safe publishing setup, such as Trusted Publishing where
appropriate, without adding credentials to source. This project includes no
publishing workflow or automatic upload step.

Reference: [PyPA packaging guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
and [setuptools project metadata](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html).
