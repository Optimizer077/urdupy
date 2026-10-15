# ADR-014: Pip-managed optional dependency profiles

- **Date:** 2026-10-15
- **Status:** Accepted for local implementation
- **Owner/task:** Integrator, URD-029
- **Interfaces:** Build metadata, optional dependency installation, artifact checks

The user requests installation with pip, including automatic dependency setup.
UrduPy's compiler/runtime use only the standard library. The scientific and AI
examples need native libraries, which remain optional under ADR-010. Standard
extras let pip install the selected feature's requirements in the same operation.

Use `[project.optional-dependencies]`: `science` installs NumPy, Pillow and one
headless OpenCV provider; `ai` includes that profile plus matching torch/torchvision,
Transformers, Matplotlib and Urdu text helpers. Direct versions match the recorded
working environments. Transitive requirements are resolved by pip; these profiles
are not a complete transitive hash lock or a promise of wheels on every platform.

Commands from the checkout are `python -m pip install .`,
`python -m pip install ".[science]"`, and `python -m pip install ".[ai]"`.
Wheel paths can carry the same extras. The distribution remains
`urdupy-design-lab`; its import/command remains `urdupy`. It is not published on
PyPI by this change, and the local instructions never substitute an unrelated
registry package named `urdupy`.

Avoid import-time pip calls, network setup hooks and hardware probing during
build/install. Pip owns dependency resolution. Metadata has no custom package
indexes or hard-coded CUDA wheel URLs. A user can preinstall matching official
CPU/CUDA torch and torchvision builds, then select the AI extra. Exact public
version requirements also accept matching local build suffixes such as `+cu130`
or `+cpu`, so pip can retain the compatible installed build. Verify that behavior
with the actual install and wheel metadata rather than assuming it.

The base wheel now contains `Requires-Dist` entries conditional on an extra;
absence of that field is no longer the dependency-free assertion. Artifact checks
evaluate every requirement with no extra selected and require zero active base
dependencies, validate declared profiles, and prove core installation in an
environment without science packages.

Rejected alternatives: forcing all frameworks into the default install, selecting
a GPU build from setup.py, and executing pip from module imports. They couple a
portable language frontend to device-specific dependencies or hide installation
side effects. Automatic datasets, pretrained weights and public publication are
outside this task.

Verification records belong in the handoff and dist reports: built metadata,
clean core wheel/sdist installations, actual selected-extra installs and pip check.
Rollback removes the optional profiles/checks/docs; grammar and runtime remain
unchanged. References: [PyPA dependency metadata](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#dependencies-and-requirements)
and [pip local installs](https://pip.pypa.io/en/stable/topics/local-project-installs/).
