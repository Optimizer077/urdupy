# ADR-015: Explicit complete Urdu dependency spellings

- Date: 2026-10-15
- Status: Accepted and implemented locally under the expanded URD-031 request
- Owners: Integrator, catalog, examples and CLI agents
- Interfaces: Opt-in source mode, library name catalog, Urdu CLI

The maintainer now requests that dependency imports, attributes, keyword arguments,
model protocols and backend text values can all be written without English. This
supersedes the early charter non-goal, without changing existing source semantics.

## Decision

A leading `# اردوپائی: مکمل` comment explicitly enables a reserved Urdu library
vocabulary. The compiler lowers identifier tokens in all positions consistently,
including assignments, parameters, keyword labels and native protocol definitions.
Import aliases bind real backend modules. No tensors, arrays, modules or classes
are proxied, and no dependency module or global import mechanism is patched.
Existing `.urdu` files without the directive retain their original behavior.

Readable Urdu names cover familiar scientific and standard-library interfaces.
Every remaining identifier has an exact, reversible `اصل_` spelling using Unicode
codepoints in Urdu decimal digits. Discovery produces these spellings from actual
installed objects; users need not invent or type an English API name. Arbitrary
backend strings likewise have reversible `متن_` spellings decoded by `اصل_متن`.
Strings/comments are never translated implicitly. Native error types, backend
data, repr output and third-party documentation remain their native values.

Reserved library spellings are translated consistently even in user definitions;
do not use two different aliases for the same native identifier as distinct local
variables. Ordinary names outside the catalog remain ordinary Urdu identifiers.
Unrecognized dependency identifiers need no new release: the reversible spelling
works in imports, attributes, names, keyword arguments and protocol declarations.

## Alternatives

Library forks duplicate huge native runtimes and diverge from upstream. Runtime
proxies compromise native type identity, subclassing, autograd and dispatch. A
handwritten subset alone fails the user's complete-surface request. Global
translation without opt-in breaks existing Urdu identifiers and APIs. This design
keeps native execution while providing a total lexical representation.

## Verification and rollback

Required evidence: preservation of the original baseline; four-minor core tests;
source maps/debug labels; actual native NumPy/torch/vision/NLP/plotting runs;
zero-ASCII-letter example sources; arbitrary identifiers/text roundtrips; Urdu
CLI discovery/installation entry points; clean wheel/sdist installation. Detailed
results will be recorded in the URD-031 handoff. Rollback removes this additive
directive path, catalog, localized entry point and examples; legacy mode survives.
