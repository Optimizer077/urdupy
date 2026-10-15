# Local stability and compatibility policy

UrduPy distinguishes three versions/statuses:

- **Package:** `0.1.0a1`, a local prerelease, not a published stable release.
- **Local language contract:** **`1.0-local`**, the documented technical spellings,
  grammar, namespace and API rules for this implementation. It is exposed as
  `urdupy.LANGUAGE_SPEC_VERSION`; it is not a public ecosystem maturity rating.
- **Evidence:** exact tests/environments; a contract does not manufacture results
  on an unrun interpreter, platform, library combination or editor.

The user's delegated local design authority permits the agents to choose the
technical contract and continue implementation. No reader survey, beginner
comprehension study, community consensus or public release approval is inferred.
The original [naming workshop](naming-proposals.md) retains those open questions.
See [ADR-012](adr/012-local-release-policy.md).

## Commitments for this contract

Preserve the documented 35 hard keyword spellings, two contextual spellings,
15 ordinary builtin aliases, Python statement shapes, punctuation and library
API names. Reserved-word collision rules are part of the language contract.
Alias object identity and ordinary shadowing are runtime behavior, not source
substitution. Do not silently make friendly candidate synonyms active.

Preserve the documented compiler/runtime/importer/CLI interfaces and the tested
import-priority/namespace behavior. The `urdupy.experimental` module retains its
separate M0 behavior; promoting a new compiler does not rewrite historical tests.
Keep source diagnostics tied to original saved source within the mapped cases.

Any intended deviation must have an ADR, failing/passing regression evidence,
documentation and a migration note. Additive syntax can still change identifier
meaning; treat newly reserved words as a compatibility change. Even a prerelease
must not change a documented spelling silently.

## Version and migration rules

Package bugfixes repair behavior toward the recorded contract. They do not change
grammar meaning as a hidden side effect. A deliberate incompatible language
change increments the contract's major version, explains the affected source,
provides before/after examples and identifies a last compatible package version.
Prefer a documented deprecation period when old/new behavior can coexist
unambiguously. Do not add ambiguous synonyms merely to avoid a version decision.

An interpreter minor enters support after its claimed suites run in a clean
environment. The metadata allows 3.12–3.15 after the core suite passed on all four
minors on Windows AMD64; exact patch/build/platform evidence remains explicit.
Linux/macOS jobs are configured but have no recorded remote execution. Adding
another minor updates tests,
metadata and release notes together. Dropping one needs an announced boundary
and last compatible release. Native scientific wheel support is tracked separately.

The small editor grammar is a convenience with approximate highlighting; no
language server, debugger or complete type-checking support is promised. A local
MIT license is provided for original code. Hosted release infrastructure,
publication ownership and remote CI runs remain separate external gates.

## Review and rollback

Keep a regression suite covering both ordinary Python and Urdu, including
attributes/imports/keyword labels, Unicode source, f-strings, packages/circular
imports, namespaces, CLI state and optional libraries. A skipped integration
does not satisfy its gate. Preserve known failures in the
[implementation handoff](implementation-handoff.md).

Rollback a focused change or disable its opt-in feature while retaining the
regression case. Never remove a test to redefine a failure as success. Source
translation changes must not be repaired by changing user data strings. Review
artifact paths before deleting generated builds or isolated environments.
