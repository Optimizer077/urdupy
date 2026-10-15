# Contributing to UrduPy

Read [AGENTS.md](AGENTS.md), the [language reference](docs/language-reference.md),
[stability policy](docs/stability.md) and relevant ADR before changing behavior.
The source distribution includes the handbook so local contributors retain its
context. The original Phase 1 notes are dated research, not current feature flags.

Use CPython 3.12 through 3.15 and a separate environment. From the project root:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -X utf8 -m unittest discover -s tests -v
.venv\Scripts\python examples/verify_examples.py
```

On Linux/macOS, use `.venv/bin/python` in place of `.venv\Scripts\python`.
The core package has no runtime dependencies. Build tooling is separate; see
[installation](docs/install.md) and [release verification](docs/release.md).

Keep changes small and runnable. Add a failing behavior fixture before fixing a
compiler, namespace or import bug. Compare Urdu source with Python under the same
interpreter; assert objects, values, errors and meaningful source positions.
Preserve strings, comments and real library attribute/protocol names. Optional
integration tests must distinguish a missing dependency from a broken installed
dependency, and must not download data or model weights while running.

Add or update an ADR for grammar, spellings, public APIs, import precedence,
runtime namespace, version range or required dependencies. The user delegated
routine local design choices for this implementation; that does not authorize a
contributor to silently change the recorded contract. Spellings need technical
regressions and a migration note. Human reading/typing feedback is welcome and
must be recorded as actual feedback, never invented or inferred from agent votes.

Work in separate owned files when agents collaborate. The integrator owns shared
trackers and final evidence. Do not overwrite another agent's pending edits.
Record exact commands, counts/skips, Python/package versions, remaining failures
and a rollback path. Check all supported minors when changing shared syntax.

No Git remote or issue tracker is assumed by this local checkout. If a maintainer
later hosts it, follow that repository's review process. A configured workflow
is not a passing remote CI run. PyPI/TestPyPI uploads, remote pushes, releases and
publication credentials need explicit authorization for that action.

New original project code is offered under [MIT](LICENSE), using the collective
holder “UrduPy contributors”; do not add invented individual ownership claims.
Keep third-party notices and licensing separate when introducing external code.
