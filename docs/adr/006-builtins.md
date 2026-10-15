# ADR-006: Resolve convenience aliases through module builtins

- **Date:** 2026-10-15
- **Status:** Proposed contract for M1; no public runtime delivered in M0
- **Owner:** Research agent; implementation and test integration belong to M1
- **Affected interfaces:** execution namespaces, alias registry, module exports

## Context and evidence

`دکھاؤ` should call real `print`, and user-defined names must follow ordinary
Python scoping. Adding every alias to module globals makes those names appear
as module exports even when the program never defines them.

**VERIFIED from official sources:** The [execution model](https://docs.python.org/3.13/reference/executionmodel.html#builtins-and-restricted-execution)
describes builtins lookup through the globals' `__builtins__`, while identifying
that binding as a CPython implementation detail. The
[`exec` documentation](https://docs.python.org/3.13/library/functions.html#exec)
allows a supplied builtins dictionary. Separate globals/locals have different
semantics, so module execution should use the same module dictionary for both.
This design is CPython-specific; it is not an arbitrary-Python-runtime promise.

## Options considered

| Option | Benefit | Cost |
|---|---|---|
| Add aliases to each module's globals | Simple, explicit inspection; alias export is easy | Pollutes ordinary exports; deleting a global alias removes its fallback |
| Copy builtins for each Urdu module and add aliases there | Normal global/local shadowing; avoids implicit alias exports | CPython-specific internal setup; per-module snapshot behavior needs tests |
| Require explicit alias imports in every file | Pure standard Python setup; visible dependencies | Extra beginner boilerplate; less convenient language entry experience |

## Proposed decision

Choose the copied builtins dictionary for UrduPy-owned execution. Keep setup an
internal implementation contract. The translator does not rewrite builtin names.

1. Copy `vars(builtins)` once for each new Urdu module execution environment.
2. Add only the versioned registry's aliases, taking objects directly from that
   copy: the object for `دکھاؤ` is the same object as its `print` entry; `فہرست`
   is the real `list` type. No wrapper callables or replacement type hierarchy.
3. Bind that dictionary under the module globals' `__builtins__` before execution;
   execute with the module dictionary as both globals and locals.
4. Do not mutate the process `builtins` module or another module's dictionary.
5. Keep aliases out of module globals unless the program explicitly binds them.

**Proposed behavior:** Module assignment/import shadows the alias; deleting that
binding restores builtin lookup. Function parameters and local assignments shadow
normally, including Python's `UnboundLocalError` for reading an assigned local
before its assignment. An alias is absent from `vars(module)` and normal star
exports unless the user explicitly defines/exports it. Attributes such as
`obj.دکھاؤ` retain their ordinary meaning. The verified fixture subset and the
remaining implementation gate are separated below.

Each module snapshots the current builtins objects at creation. Later rebinding
`builtins.print` does not update an earlier copy or its alias. That is a deliberate
observable consequence, to document and test; object identity is promised at
environment construction, not against every later global monkey-patch. A module
can inspect or modify its own supplied mapping; this mechanism is not a sandbox.

## Compatibility, migration, rollback

The attached historical prototype is not present, so this phase has no existing
runtime to migrate. If imported historical programs relied on injected aliases
as exports, offer explicit user bindings or `__all__` entries; do not silently
preserve accidental exports by polluting the new default. A stable runtime needs
a versioned migration note before changing this behavior later.

Rollback before M1 acceptance: leave the runtime unimplemented and revise this
proposal. After acceptance, replace only the setup helper behind regression
coverage; preserve the documented lookup/export semantics or version the change.

## Verification and remaining gate

**VERIFIED bounded experiment:** On both local interpreters, these commands
passed **9 tests** on 2026-10-15:

```powershell
python -X utf8 -m unittest discover -s tests -p test_design.py -v
py -3.11 -X utf8 -m unittest discover -s tests -p test_design.py -v
```

The integrator's `tests/test_design.py` fixture demonstrates actual builtin
objects, function/parameter shadowing, absent alias globals, isolated mappings,
ordinary conversion exceptions, and calls to a real Python API with keyword-shaped
export/attribute/keyword labels. It also checks distinct None/False/empty values,
identity semantics, and deferred-name boundaries. A helper inside a test is not
a public runner; this ADR implements no execution helper. Full-suite results
belong to the final handoff.

M1 must run tests for actual object identity, globals/parameters/locals shadowing,
deletion fallback, imports shadowing aliases, star-export behavior, two-module
isolation, mutation isolation, ordinary English builtins, exceptions, and no
process-wide additions. Compare an equivalent Python module and test functions
after top-level execution finishes. Claim the runtime only after those tests pass.
