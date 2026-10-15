# ADR-009: Keep UrduPy's identity while deferring public packaging

- **Date:** 2026-10-15
- **Status:** Proposed M0 naming direction; registry ownership and release OPEN
- **Owner:** Research agent
- **Affected interfaces:** distribution name, import package, CLI, release metadata

## Context and evidence

The user requested the directory name `urdupy`. The language/project name is
**UrduPy**, and the local import package is `urdupy`. These choices do not reserve
a public distribution name.

**VERIFIED observation:** Both official JSON endpoints,
[`urdupy`](https://pypi.org/pypi/urdupy/json) and
[`urdupy-design-lab`](https://pypi.org/pypi/urdupy-design-lab/json), returned HTTP
404 with `{"message": "Not Found"}` on 2026-10-15. See
[research](../research/python-and-packaging.md) for retrieval limitations.
**OPEN:** Registerability, ownership, legal clearance and future availability.
[PyPI help](https://pypi.org/help/#project-name) explains why absence of a visible
project does not prove a name can be used.

## Options considered

| Option | Benefit | Cost |
|---|---|---|
| Public distribution `urdupy` after approval and verification | Short; matches language and local imports | No ownership established; name/legal review still required |
| Distinct distribution `urdupy-design-lab` with `urdupy` imports | Signals experimental purpose; retains code spelling | Longer install command; still unreserved and can collide on import files |
| No installable distribution during M0 | Accurate scope; no premature metadata/support claims | Checkout-only experiment until packaging milestones |

## Proposed decision

Choose no installable distribution in M0. Keep `urdupy-design-lab` as a provisional
candidate, not an approved public name. The eventual short name `urdupy` remains
a release candidate only if registerability, ownership and project review succeed.
Do not run either candidate's `pip install` command as proof of ownership.

[PyPA distinguishes distribution and import packages](https://packaging.python.org/en/latest/discussions/distribution-package-vs-import-package/).
A distribution may use a different import spelling, but two installed distributions
can still conflict if both supply `urdupy` files. Do not co-install the historical
`urdupy-demo` and a replacement into a release validation environment.
[Normalization](https://packaging.python.org/en/latest/specifications/name-normalization/)
makes case and separator variations unsuitable as a way to obtain a new identity.

## Migration and release gates

There is no supplied installed prototype to migrate. Keep the guide's historical
`urdupy-demo` spelling as reference evidence only. If real users later migrate,
document uninstall/upgrade in a clean environment; preserve import and CLI names
where feasible, and test that stale files do not remain. A distribution rename
alone must not silently change grammar or alias behavior.

M5 must recheck the registry, review legal/name questions with the maintainer,
choose the final distribution and version, add standards-compliant metadata and
an accurately tested Python range, build wheel/sdist, inspect archive contents,
install both in clean environments, and test CLI/imports. Publication remains a
separate explicit maintainer action. Core dependencies must remain lightweight;
scientific integrations use optional environments and recorded constraints.

## Verification and rollback

This task performed read-only HTTPS requests; no package creation, reservation,
upload, or publication happened. A later local package build is not PyPI ownership
evidence. Rollback in M0 changes only this provisional naming note. After public
release, rename through documented migration and a release boundary, preserving
the previously published install path according to the accepted support policy.
