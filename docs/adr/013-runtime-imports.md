# ADR-013: Owned execution state and Python-first Urdu packages

- Date: 2026-10-15
- Status: Implementation under verification; supersedes ADR-007's bounded M0 proposal
- Owner: Integrator; URD-007, URD-009, URD-011

## Decision

Use a per-module copied builtins dictionary containing genuine built-in aliases.
Caller dictionaries remain exec dictionaries; anonymous execution uses a temporary
real module so decorators can inspect its definition context. Imported modules
and scripts have ordinary persistent/importlib and `__main__` identities.
Anonymous returned classes do not promise persistent pickle import identities;
put such classes in a proper module.

The opt-in finder sits immediately before the existing `PathFinder`, asks it for
a standard spec, and defers whenever a concrete Python/native/zip spec exists.
Earlier custom/builtin/frozen finders keep their priority. If only a namespace
spec exists, a regular package with `__init__.urdu` can provide its initializer;
a loose `.urdu` module cannot displace that namespace. Standard concrete Python
resolution wins globally, including a later path entry's `.py` module over an
earlier `.urdu` file. This global priority is deliberate and documented.

## Alternatives

An appended finder cannot execute `__init__.urdu` after namespace discovery.
A path-entry hook integrates suffix discovery but changes per-path competition
and more cache state. A generated `.py` tree creates extra build/source-map state.
Delegation resolves the observed package problem while leaving concrete Python
priority intact. It adds one standard spec lookup for unresolved Urdu candidates.

## Ownership and diagnostics

Nested registrations share one finder through idempotent handles. Closing the
last handle removes only that finder. Already imported modules retain ordinary
`sys.modules` caching; disabling a hook does not un-import user modules.
No bytecode cache or discovery cache is written. Explicit `iter_urdu_modules`
supports discovery; standard `pkgutil` is not patched.

`run_path` restores argv/path object identities and `__main__` on success, error,
interrupt or SystemExit. Execution uses a reentrant process-state lock: these
script-level context changes are serialized, not advertised as thread-local.
Anonymous `execute_source` calls use unique default virtual filenames and do not
hold the script-state lock while user code runs, so worker threads can execute
their own source. Explicitly reusing one filename concurrently requires a
consistent source snapshot; interpreter traceback caches are not thread-local.
Temporary source-cache entries restore previous owned values and preserve a
replacement installed by another owner. Exceptions keep their real type/object;
CLI formatting can use a private captured traceback while anonymous source is
available. Physical imported files remain readable by normal traceback machinery.

## Verification and rollback

Acceptance requires focused runtime/import tests for alias identity/shadowing,
state restoration, regular/namespace parents, collision priority, circular and
relative imports, failure cleanup, resources, reload, cache invalidation and
Unicode filenames. Final exact results belong in the implementation handoff.
Revert these new modules and public exports as a focused change before release;
M0 experimental code stays intact. Once a compatibility contract is published,
precedence/namespace changes require a language/package migration boundary.
