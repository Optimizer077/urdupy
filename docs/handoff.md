# Phase 1 handoff — completed M0

Date: 2026-10-15. Project: **UrduPy**, folder/package `urdupy`, extension `.urdu`.
Local experiment identifier: `0.1.0a1`; language specification: `0.1-draft`.
No public release or stable language acceptance is claimed.

## Delivered

- [Grammar and function design](language-design.md): Python-shaped blocks,
  expressions, signatures, calls, defaults, return/output, scope, decorators,
  annotations, classes and protocols, with clear Urdu explanations.
- [Naming workshop](naming-proposals.md): complete guide vocabulary audit,
  detailed alternatives for input/pass/identity/None/yield/async, spelling/RTL
  guidance, five comprehension exercises and a blank human feedback worksheet.
- [Single experimental registry](../urdupy/lexicon.py): 31 keyword mappings and
  15 ordinary built-in alias names. Six advanced Urdu candidates stay deferred.
- [Experimental translator](../urdupy/experimental/translator.py): original-source
  span edits, bounded context protection, compilation without execution and
  explicit rejection of unsupported Urdu f-string expressions.
- [Five runnable example pairs](../examples/README.md): conditions, loops,
  function contracts, actual standard-library imports and class protocols;
  compared against ordinary Python and independently specified expected results.
- [Architecture decisions](adr/004-lexicon.md) and [research entrypoint](research/README.md):
  translator options, proposed builtins/import contracts, dated official Python
  and PyPI evidence, and an offline scientific integration plan for M3.
- [Roadmap](roadmap.md), [phase scope/ownership](phase-1.md), retained handbook
  tracker and [changelog](../CHANGELOG.md).

## Starting state

The requested folder did not exist. No compiler, runtime, importer, CLI,
packaging, tests or historical prototype was supplied. The parent workspace is
not a Git repository; no commit, branch, remote or merge evidence is invented.
Initial discovery in the parent failed resolving an unrelated `tests` namespace.
The corrected new-folder baseline found **0 tests**, `NO TESTS RAN`, exit 1.
The historical seven-test snapshot in the guide belongs to a different checkout.

## Verification

All commands below ran from the project root; final runs returned exit 0.
Tests require only the Python standard library and make no network requests.

| Exact command | Actual environment | Result |
|---|---|---|
| `python -X utf8 -m unittest discover -s tests -v` | CPython 3.13.13, Anaconda, Windows AMD64, 64-bit | **PASS — 57 tests, 0 skips** |
| `py -3.11 -X utf8 -m unittest discover -s tests -v` | CPython 3.11.9, Windows AMD64, 64-bit | **PASS — 57 tests, 0 skips** |
| `python examples/verify_examples.py` | CPython 3.13.13 | **PASS — 5/5 pairs** |
| `py -3.11 examples/verify_examples.py` | CPython 3.11.9 | **PASS — 5/5 pairs** |
| `python docs/research/probe_environment.py` | CPython 3.13.13 | **PASS — inventory, f-string tokens, namespace-package observation** |
| `py -3.11 docs/research/probe_environment.py` | CPython 3.11.9 | **PASS — same observations on older tokenizer** |

The 57-test suite contains 48 translation regressions and nine namespace/design
experiments. It checks preserved strings/comments/attributes/imported API names,
Unicode keyword arguments, relative-import syntax, English soft keywords,
ordinary Python pass-through fixtures, f-string restrictions, LF/CRLF/BOM,
Unicode spans, host-version syntax, real exception behavior and alias scoping.
Python API collision fixtures import actual temporary module objects and restore
their owned interpreter state.

Each example pair compares stdout and recursively compares values **and types**
against both Python and independently written expectations. The function example
also checks five matching signatures, argument errors, return/output distinctions
and independent lists created through a None default. Classes use real Python
protocols/decorators. These are bounded fixture results, not full grammar coverage.

Observed platform strings were `Windows-11-10.0.26200-SP0` for 3.13 and
`Windows-10-10.0.26200-SP0` for 3.11 on this host; both report AMD64. No other
OS/interpreter/native-library combination ran. Official-current-version research
is distinct from this execution evidence.

Final read-only artifact audit: **18 Markdown files, 55 local file links, no
missing targets**; **18 UTF-8 Python/Urdu source files, no literal Unicode format
controls**. Temporary namespace-probe directories were fully removed. This checks
saved text and file targets, not rendering in every editor or remote-link uptime.

## Review and corrected findings

Three agents owned separate language, compiler and research file scopes. The
integrator reviewed their contracts/code and independently reran all final
commands. The research agent also independently reviewed the README, roadmap and
namespace suite and reran an earlier 53-test checkpoint on both interpreters.

- The first focused compiler test failed before its implementation existed.
  The completed implementation passes its 48-test focused suite on both minors.
- Review found a missing relative-only import case. Regression coverage now
  includes `سے . درآمد thing`, parent-relative paths and a module named
  `درآمد`; CPython parsing selects the correct delimiter without executing it.
- An initial example verifier inherited its own future-annotations flag when
  compiling the Python reference, producing a signature mismatch. Reference
  compilation now uses `dont_inherit=True`; signature checks remain strict.
- Source-span review added BOM-first-line and literal Unicode line-separator
  cases. Custom AST errors convert byte columns to translated character columns;
  original-source error mapping remains future work.

There are no known failing final checks within the Phase 1 acceptance scope.
Naming judgments remain agent hypotheses; no native-speaker feedback or maintainer
ratification of stable spellings was fabricated.

## Remaining boundaries

1. The translator uses lexical heuristics and the host tokenizer on extension
   syntax outside the tokenizer's documented valid-Python input guarantee. Its
   successful fixtures do not justify promotion to a production parser.
2. Active Urdu keywords inside f-string expressions are unsupported and explicitly
   rejected. Ordinary names/aliases, literal text and tested API contexts remain
   usable. Deferred Urdu advanced words are not syntax in this experiment.
3. There is no public runtime, installed CLI, REPL, `.urdu` loader, regular Urdu
   package initializer, exact original-column map, debugger or linecache service.
   The example/test namespace is a design fixture, not a shipped runtime.
4. A directory with only `__init__.urdu` is claimed by standard Python as a
   namespace package. An appended finder cannot execute that initializer; M2 must
   resolve the architecture gate documented in ADR-007.
5. Python 3.12/3.14/3.15, other platforms, scientific/AI libraries, native wheels,
   package builds and clean installation remain **UNVERIFIED**. No heavy package
   or model weights were downloaded. No release support range is advertised.
6. PyPI HTTP 404 observations establish no ownership, legal clearance or right
   to register either candidate name. Installation metadata and publishing remain
   later work. No source was pushed, uploaded, published or sent to another person.

## Next safe task and rollback

Begin **Phase 2 / M1, URD-005**. Compare a grammar-aware production approach
against the preserved API-collision fixtures; then scope URD-006 f-strings and
URD-007 runtime alias setup separately. Prioritize tests on the officially
researched current stable CPython, with exact recorded results before claims.
Collect human naming feedback before accepting disputed spellings.

Rollback only this new isolated folder's introduced files after inspecting them;
do not touch sibling projects or the original attached handbook. Keep the bounded
regression cases as evidence if replacing the experimental compiler. The phased
goal ends at completed M0; later milestones remain planned work.
