# Continuous implementation goal — M1 through M6

Authorized 2026-10-15: the maintainer explicitly requested that work continue
through **all** phases, using the existing multi-agent approach and allowing
routine design decisions and documented departures from the guide.

**Completed local scope:** all implementation phases, 159 core tests on four
Python minors, nine offline AI tests, local artifacts and clean installations.
See [current evidence](implementation-handoff.md) for exact outcomes and the
external publication/hosted CI/community gates.

## Baseline and scope

M0 is retained as historical evidence, not overwritten. Starting implementation
baseline: `python -X utf8 -m unittest discover -s tests -v` passed **57/57** on
CPython 3.13.13. M0 tests and experimental APIs keep their existing behavior.
Production work uses separate modules. CPython 3.12.13 is also installed and
will be tested; the historical 3.11 experiment is separate from production's
initial minimum 3.12. The workspace still has no Git repository.

Deliver production translation, aliases, runner, CLI, modules/packages, original
diagnostics, scientific/AI offline tests, REPL/editor/education, local packaging
and clean installation, CI configuration and a versioned language contract.
Publication, remote CI execution and community feedback cannot be fabricated;
record exact external gates separately from completed local engineering.

## Ownership

| Owner | Exclusive edit scope | Sequential milestones |
|---|---|---|
| Integrator | Registry, package exports, runtime/importer/CLI, integration tests, shared README/tracker/roadmap/handoff, local environments/build verification | M1 runner, M2 imports/diagnostics, M4 REPL, integration gates |
| Compiler agent | `urdupy/compiler.py`, `source_map.py`, `tests/test_compiler.py`, compiler docs and ADR-011 | M1 grammar, M2 maps, M6 contract coverage |
| Packaging agent | `pyproject.toml`, `MANIFEST.in`, CI, license/contributing/security, install/CLI/tutorial/reference/stability/release docs, editor assets, ADR-012 | M4 education/tools, M5 local artifacts, M6 version policy |
| AI agent | `tests/compatibility/*`, `examples/science/*`, `tools/run_compatibility.py`, AI docs, ADR-010, compatibility constraints | M3 science/vision/training/combined, M4 offline Transformers |

Only the integrator edits the shared handbook and executable keyword registry.
Agents report exact evidence instead of conflicting tracker writes. Environments
created for verification remain under the project and do not alter system packages.

## Decisions and gates

- Keep guide spellings; activate its four advanced hard keywords in production
  behind explicit tests. `منتخب` and `صورت` require contextual recognition.
  No Urdu `type` spelling is accepted without a concrete need and proof.
- Keep package version `0.1.0a1` for honest prerelease packaging; version the
  technical language contract separately from distribution maturity. Human
  naming acceptance remains distinct from a tested compatibility promise.
- Initial production support candidates are CPython 3.12/3.13. Investigate newer
  stable interpreters, but declare only tested targets. No unsupported range badge.
- Use genuine builtins through copied per-module namespaces; never patch Python's
  `__import__` or process-wide builtins.
- Resolve regular `.urdu` packages with a finder that defers to standard concrete
  Python specs; test the namespace-package initializer pitfall before acceptance.
- Scientific tests use installed real CPU libraries, synthetic data and local tiny
  model configuration. No pretrained-weight downloads or routine network services.
- Build wheel/sdist locally and install each in a clean environment. CI config is
  inspectable work; remote pass status requires an actual authorized remote run.

Each integration runs focused regressions, the preserved baseline and relevant
new suites. Record failures and repairs without weakening expectations. Rollback
only new production surfaces or their focused changes; preserve M0 evidence and
sibling projects. The continuous goal completes when these local deliverables and
honest verification are complete; external results are reported separately.
