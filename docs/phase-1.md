# Phase 1 — Language design and evidence

Date: 2026-10-15. This phase corresponds to **M0** in `AGENTS.md`.

**Status: COMPLETE.** Final evidence and remaining boundaries are recorded in
[`handoff.md`](handoff.md). The 57-test suite and all five paired examples pass on
both recorded local interpreters. This completes M0, not the later milestones.

## Scope and acceptance

Create a new UrduPy design project, not a claimed continuation of the historical
prototype. Deliver a careful grammar and function design, a versioned experimental
lexicon, candidate comparisons, bilingual examples, architecture decisions,
official Python/package research, a bounded translation experiment with regression
tests, and a truthful handoff for M1.

The experimental implementation is evidence for design decisions. It does not
establish full Python compatibility, a production runtime, `.urdu` import support,
AI-library support, or public-release readiness. Controversial spellings stay
provisional until feedback from Urdu-reading developers is recorded.

## Baseline

- Project directory did not exist. No source, tests, README, packaging, compiler,
  runtime, importer, CLI, or historical prototype was provided.
- Workspace is not a Git repository. Agents coordinate using separate owned files;
  no commits or worktrees can serve as historical evidence in this phase.
- On the newly created empty `tests/`, `python -m unittest discover -s tests -v`
  reported **0 tests**, `NO TESTS RAN`, exit 1 on Python 3.13. This is an empty
  baseline, not a passing feature suite.
- Default Python: CPython 3.13.13. A second local Python 3.11 is available;
  exact environment and completed runs will be recorded in the final handoff.
- The initial discovery command accidentally ran in the parent workspace and
  failed with a `TypeError` resolving an unrelated `tests` namespace. It provides
  no UrduPy verification. The command was rerun in the new project as above.

## Ownership and integration

| Owner | Task IDs | Exclusive edit scope |
|---|---|---|
| Integrator | URD-001, registry integration, tracking | `AGENTS.md`, `README.md`, `pyproject.toml`, `urdupy/__init__.py`, `urdupy/lexicon.py`, roadmap, final handoff |
| Language agent | URD-004, design portion of URD-025 | `docs/language-design.md`, `docs/naming-proposals.md`, `docs/adr/004-lexicon.md`, `examples/*` |
| Compiler agent | URD-003, bounded proof for URD-005 | `urdupy/experimental/*`, `tests/test_translation.py`, `docs/adr/005-translator.md` |
| Research agent | URD-002, M0 package research, contracts | `docs/research/*`, `docs/adr/006-builtins.md`, `docs/adr/007-imports.md`, `docs/adr/008-python-versions.md`, `docs/adr/009-distribution.md` |

Only the integrator edits the executable lexicon. Agents read the full handbook
before code changes, agree interfaces by message, run focused tests, and report
evidence. Each owner reports completed work to the integrator, who alone updates
the shared handbook tables to avoid conflicting writes.

## Rollback

This is a new isolated folder. Revert only files introduced by this phase after
reviewing the file list; do not change sibling projects or the attached guide.
The experimental compiler stays explicitly experimental and can be replaced
without promising a stable public API. No package is published or remote changed.
