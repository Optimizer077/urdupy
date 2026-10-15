# Phased development

## Current implementation status (2026-10-15)

The maintainer requested continuous work through the later phases. M0 is
historical; production M1/M2, recorded CPU M3, offline-NLP/REPL/docs/editor M4
and the local `1.0-local` M6 contract are implemented and verified. M5 local
wheel/sdist builds and four-minor clean wheel installation also pass. See
[the implementation handoff](implementation-handoff.md) for exact current results.
Public publishing, hosted CI runs and community maturity remain explicit external
gates. The original phase definitions below remain the design roadmap.

Phase numbers are one-based; milestone IDs are retained from the guide so the
original task IDs remain useful.

| Phase | Guide milestone | Result and exit gate |
|---|---|---|
| **1 — Design and evidence** | **M0** | Written grammar/function spec, naming comparisons, provisional registry, baseline, translator experiment and regression fixtures, architecture contracts, official version/name research, risks and handoff. |
| 2 — Language core | M1 | Production translator and runner, complete bounded grammar support, f-string policy, alias resolution, `run`/`translate`, no corrupted strings or library names. |
| 3 — Modules and diagnostics | M2 | Opt-in `.urdu` modules/packages, Python precedence, circular/relative imports, source maps, `check`, state restoration. |
| 4 — Scientific and AI evidence | M3 | Offline NumPy, OpenCV, PyTorch and combined CPU scenarios; recorded package/platform versions. |
| 5 — Advanced use and education | M4 | Offline Transformers experiment, usable diagnostics, RTL/editor guide, optional REPL if implemented. |
| 6 — Package readiness | M5 | Packaging metadata after the supported range is tested, wheel/sdist installation, CI, release documentation and explicit publication approval. |
| 7 — Stable language | M6 | Community naming feedback, versioned grammar and migrations, mature editor support and a tested 1.0 contract. |

## Deliberate Phase 1 choices

- Start from a new project. The separate historical prototype and its seven tests
  are not present and do not count as this project's baseline.
- Keep one canonical spelling per concept in the experiment. Compare creative
  alternatives in proposals rather than silently adding synonyms.
- Explore namespace resolution in a test fixture. A production runtime and import
  hook belong to later phases.
- Use a small flat package for the experiment, rather than create empty production
  compiler/runtime subsystems that imply working features.
- Coordinate agents through owned files in a shared folder. The workspace has no
  Git repository, so no fictitious branches, commits or merge evidence is recorded.
- Defer `pyproject.toml` installation metadata. A tested minimum alone does not
  establish a fully verified interpreter range; the local distribution name is
  researched without claiming PyPI ownership. Run the lab from this checkout.
- Keep research of the latest stable CPython distinct from local verification.
  A release listed on python.org has not thereby passed UrduPy tests.

## Next safe work

Start Phase 2 with URD-005 and the collision fixtures in the experiment. Resolve
the limits of token-context heuristics before promoting the translator to a
public API. Then address URD-006 f-strings and URD-007 production built-in alias
resolution. Keep controversial language names provisional pending human feedback.
