# ADR-012: A scoped local contract and an honest prerelease

- **Date:** 2026-10-15
- **Status:** Accepted for local implementation under the user's delegated choices
- **Owners:** Integrator and packaging/docs agent
- **Interfaces:** package identity/version, language stability, release gates

## Context and authorization

The user explicitly requested continuation through all phases, authorized routine
design decisions/deviations, and asked the agents not to stop after M0. That
delegation permits choosing and testing a technical language contract locally.
It supplies no survey evidence, community consensus, public name ownership,
remote CI result, or permission to publish to an external package index.

The original M0 artifacts remain historical. New implementation and evidence
must be assessed on their own; retain failures and known limitations.

## Options considered

| Option | Benefit | Cost |
|---|---|---|
| Label the whole system 1.0 and all gates complete | One simple label | Overstates unrun platforms, uncollected feedback and external-release readiness |
| Keep every grammar decision provisional indefinitely | Avoids a premature promise | Prevents users from depending on technically tested local spellings |
| Freeze a narrowly specified local grammar while shipping a package prerelease | Useful compatibility contract with explicit evidence boundaries | Requires separate language, package and validation status records |

## Decision

Choose the scoped **`1.0-local`** technical contract. Keep the package **0.1.0a1**
while its public release remains a prerelease. Track the language separately and
promise only the documented spellings, grammar rules, aliases, precedence and
APIs covered by that contract. Broader ecosystem maturity is not implied by its
technical version. Disputed terminology keeps its recorded usability questions;
agents' naming choices are not represented as Urdu-reader validation.

Use local distribution **`urdupy-design-lab`**, import package/CLI **`urdupy`**,
and extension **`.urdu`**. The registry's 404 observation established no right to
register a name. Provide standards-compliant setuptools metadata and build
wheel/sdist locally, retaining no mandatory scientific dependencies. The initial
interpreter envelope is **3.12–3.15** after the integrated core suite passed
**159/159 tests, zero skips**, on local Windows AMD64 under **3.12.13, 3.13.13,
3.14.6 and 3.15.0**. The integrator records exact commands/builds in the final
handoff. This is no Linux/macOS, ARM or scientific-wheel guarantee.

Apply MIT to new original project code using “UrduPy contributors” as the generic
collective copyright holder. This asserts no invented personal authorship.
Maintainer review may revise licensing choices before wider distribution;
third-party material and the supplied handbook retain their own terms. Including
the guide as source context does not assert that the agents authored it or
establish permission for a future public redistribution.

CI configuration supplies twelve Windows/Linux/macOS and interpreter jobs.
Until the repository
is hosted and actual jobs run, remote outcomes remain **UNVERIFIED**. Local build
success and a pure-Python wheel tag likewise establish no unrun platform result.
No workflow publishes packages or consumes release credentials.

## Compatibility, verification and rollback

The [stability policy](../stability.md) states exact local commitments and migration
rules. The [implementation handoff](../implementation-handoff.md) records actual
commands, versions and results; the [release checklist](../release.md) keeps
unresolved external gates visible. An unrun check stays unrun.

Before distribution, revise only metadata/docs if choosing another distribution
name; preserve import/CLI and grammar where feasible. After sharing a contract,
change syntax only through a versioned migration and regression coverage. Rollback
of local packaging removes built artifacts/isolated validation environments after
reviewing their paths, leaving source/tests intact. No remote release needs undoing
because none was authorized or performed by this decision.
