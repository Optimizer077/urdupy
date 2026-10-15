# ADR-007: Preserve Python priority with an opt-in Urdu fallback

- **Date:** 2026-10-15
- **Status:** Proposed M2 contract; Urdu package-initializer strategy remains OPEN
- **Owner:** Research agent
- **Affected interfaces:** finder registration, `.urdu` module resolution, packages

## Context and official evidence

Third-party Python/native modules must retain normal import behavior. Import
changes affect process state and must be opt-in.

**VERIFIED:** Python checks `sys.modules` first, then queries meta finders in order.
Its import machinery inserts a module before executing it, and removes the failed
module on an initial-load failure while preserving successfully loaded side
effects. See the [import reference](https://docs.python.org/3.13/reference/import.html).
[`PathFinder`](https://docs.python.org/3.13/library/importlib.html#importlib.machinery.PathFinder)
searches `sys.path` or the parent package's path. These are CPython contracts to
reuse, not algorithms to reproduce by manually populating `sys.modules`.

## Options considered

| Option | Benefit | Cost |
|---|---|---|
| Append an opt-in meta finder after existing finders | Existing Python, native, zip, and custom finders keep priority | Standard namespace packages can prevent Urdu initializer discovery |
| Opt-in path-entry `FileFinder` with an Urdu loader after standard suffixes | Natural per-path module/package discovery, including `__init__.urdu` | Changes suffix/path competition; hook/cache restoration is more invasive |
| A delegating finder before `PathFinder`, deferring to standard specs | Can deliberately handle a namespace result and Urdu initializer | More complexity; must prove it never displaces legitimate standard resolution |
| Build Urdu files into a separate Python output tree | Plain Python importer and package tools | Extra build step; source maps and stale generated files need handling |

## Proposed bounded decision

Start M2 experiments with an **explicitly enabled, appended meta finder**. Importing
the `urdupy` package itself must not install a hook. The finder sees unresolved
loose `name.urdu` files and unresolved `.urdu` children inside regular Python or
namespace packages. It returns `None` for unsupported paths and uses only actual
filesystem directories initially. Existing standard resolution wins across all
searched entries; an earlier `name.urdu` does not displace a later standard
`name.py`, native module, zip import, or existing namespace spec.

**VERIFIED local pitfall:** For a directory containing only `__init__.urdu`,
`PathFinder.find_spec` returned a namespace-package spec (`loader=None`,
`origin=None`, package path present) on both **3.11.9** and **3.13.13**. Therefore,
an appended finder alone cannot execute that Urdu initializer. Reproduce with:

```powershell
python docs/research/probe_environment.py
py -3.11 docs/research/probe_environment.py
```

**OPEN:** Full regular packages initialized by `__init__.urdu` need a separate M2
architecture decision/proof among the alternatives above. Until then, document
them as unsupported and surface a useful diagnostic when feasible; never silently
describe a namespace package as having executed an Urdu initializer. A standard
`__init__.py` plus `.urdu` submodules is a viable first explicit package layout.
This limitation is a release gate, not a claimed solution to all package imports.

## Loader and lifecycle contract to test in M2

The following are **HYPOTHESES / UNIMPLEMENTED**:

- Build a correct `ModuleSpec` with `.urdu` origin, original filename, loader,
  and package search locations only for supported package kinds. Implement
  `create_module` and `exec_module`; let importlib own normal module creation,
  caching, parent-child binding, and failure cleanup.
- Execute in `module.__dict__` using ADR-006's builtin environment. Preserve
  `__name__`, `__package__`, `__spec__`, `__loader__`, `__file__`, and `__path__`
  where applicable. Relative imports use the actual parent package context.
- Repeated import returns the cached object and executes once. Circular imports
  expose normal partial initialization; do not promise every circular program is
  valid. `.py` to `.urdu` needs the hook active; `.urdu` to `.py` stays ordinary.
- Registration returns an owned handle/context; repeated/nested use must not add
  duplicates or remove another owner's registration. Remove only the owned finder
  on exit, preserving unrelated concurrent changes. No `__import__` monkey-patch.
- Disabling a hook does not undo successfully imported modules; they remain in
  `sys.modules` like ordinary imports. Tests clean up only names they own.
- Initially avoid writing bytecode caches. Before enabling them, specify keys
  including source content, compiler/lexicon version, interpreter and optimization.
- Cache invalidation notices newly created/changed Urdu files. Runner-only changes
  to path/argv and owned `linecache` entries require `try/finally` restoration;
  importer registration itself should not change path/argv or erase global caches.

The [`importlib` documentation](https://docs.python.org/3.13/library/importlib.html#importlib.invalidate_caches)
provides the cache invalidation protocol; resource access and `pkgutil` discovery
are additional explicit tests, not automatic promises from finding a module.

## Required acceptance and rollback

M2 fixtures: same-directory and cross-path `.py`/`.urdu` collisions; builtin/frozen/
native/zip/custom finder precedence; module import both ways; Python and namespace
parents; nested/relative imports; repeated imports; circular partial state;
initial failure and successful side-effect caches; reload; cache invalidation;
hook nesting/uninstall; original diagnostics; globals/argv/path/linecache
restoration after success and failure. Test Urdu filenames independently on each
claimed OS, including Windows case behavior. Record each outcome.

No importer exists in M0. Rollback is to remove the experimental registration or
disable it and run Python as normal. Changing precedence or initializer semantics
later needs an ADR revision, migration examples, and regression tests before release.
