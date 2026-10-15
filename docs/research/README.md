# Research entrypoint

Phase 1 / M0 research distinguishes **VERIFIED**, **HYPOTHESIS**, and
**OPEN / UNVERIFIED** evidence. No public runtime/importer, installable release,
or scientific compatibility was produced by this research work.

- [Python releases, actual local versions, tokenizer boundary, proposed CI, and PyPI observations](python-and-packaging.md)
- [Small offline NumPy, OpenCV, and PyTorch integration plan for M3](offline-integration-plan.md)
- [Reproducible offline environment/tokenizer/namespace observation](probe_environment.py)
- [ADR-006: module builtins alias contract](../adr/006-builtins.md)
- [ADR-007: import precedence, packages, and lifecycle](../adr/007-imports.md)
- [ADR-008: measured Python-version policy](../adr/008-python-versions.md)
- [ADR-009: distribution naming and packaging gates](../adr/009-distribution.md)

Key findings on 2026-10-15: official latest stable is **CPython 3.15.0**;
local research observations ran on **3.13.13 Anaconda** and **3.11.9**. PyPI
returned 404 for both candidate names, which establishes no registration right.
An appended import finder alone cannot execute `__init__.urdu` when Python has
already claimed its directory as a namespace package. The detailed notes retain
these limits so later phases can resolve them explicitly.
