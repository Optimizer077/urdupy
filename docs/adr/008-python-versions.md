# ADR-008: Separate research targets from tested Python support

- **Date:** 2026-10-15
- **Status:** Proposed policy; no stable supported range in M0
- **Owner:** Research agent
- **Affected interfaces:** grammar adapters, compatibility matrix, package metadata

## Context

**VERIFIED:** The official [3.15.0 release page](https://www.python.org/downloads/release/python-3150/)
labels it stable and dates it 2026-10-09. Research was retrieved on 2026-10-15.
The installed interpreters are 3.13.13 Anaconda and 3.11.9, both AMD64 on the
Windows host. Official current release status does not establish local execution.
See [full research and exact inventory](../research/python-and-packaging.md).

## Options considered

| Option | Benefit | Cost |
|---|---|---|
| Declare broad `>=3.11` immediately | Simple metadata; wide intended reach | Claims eligibility for untested new grammar/tokenizers |
| Target only latest stable initially | Smaller future maintenance surface | Latest interpreter is not installed; no local feature evidence yet |
| Publish measured experiments first, then gate a support range by CI | Truthful M0 output; explicit upgrade work | No installability promise in this phase |

## Proposed decision

Choose measured experiments now. Record exact interpreters and suite scope;
avoid claiming production support from passing bounded translation fixtures.
Omit installable project metadata in M0 rather than encoding an unverified range.
Tool-only configuration may be added independently when useful.

M1's desired CI targets are 3.11, 3.12, 3.13, 3.14, and latest stable 3.15,
prioritizing 3.15 installation and 3.12 tokenizer-boundary validation. This is a
proposal, not a guarantee that all five will be supported. Gate each minor by
core grammar/runtime fixtures, then M2 import/diagnostic fixtures before claiming
those features. Test clean upstream CPython as well as the local Anaconda build.
Each OS/architecture and scientific-library combination needs its own evidence.

**OPEN:** Minimum long-term minor, exact release CI matrix, availability of native
wheels, latest-minor grammar coverage, and non-Windows execution. The final
`requires-python` must represent the actual accepted range; README/classifiers
must agree with it. Do not infer 3.12 success from passing 3.11 and 3.13.

## Migration, verification, rollback

Adding a newly tested minor is an explicit compatibility update. Dropping one
needs a documented release boundary, rationale, and a last supported version.
Maintain host-version fixtures for f-strings, soft keywords, new literals,
annotations, diagnostics, and new import forms.

Research probes ran on both local versions; no 3.12/3.14/3.15 UrduPy suite ran in
this task. Integrator reports project tests separately. Before metadata exists,
rollback simply revises this plan; after release, withdraw an unsupported claim
and fix the affected version without silently weakening tests or retroactively
marking skipped suites passed.
