# ADR-011: CPython frontend with explicit contexts and original-source locations

- Date: 2026-10-15
- Status: Implemented for prerelease review; no 1.0 claim
- Owner: Compiler agent, URD-005/006/011
- Scope: `urdupy/compiler.py`, `urdupy/source_map.py`, `tests/test_compiler.py`,
  this ADR, and `docs/compiler.md`
- Baseline: `python -X utf8 -m unittest discover -s tests -v`: 57 passed,
  CPython 3.13.13, Windows AMD64. No Git repository exists.

The maintainer has authorized continuing through every phase. The M0 experiment
and its tests stay unchanged as historical evidence. The integrator owns the
production lexicon, runtime, loader and CLI; other agents own packaging and AI
validation. Compiler changes are isolated in new files and can be rolled back by
restoring the entry-point imports after reviewing dependents.

## Decision to implement and verify

Use a new span-based token transform with explicit import, attribute, call-label,
function-parameter, soft-keyword, and f-string field contexts. Let CPython's parser
validate the resulting grammar. Parse isolated `from` statements to distinguish
Urdu import syntax from identically spelled external module/export names. Keep
hard Urdu words reserved unqualified and validate remaining bindings in the AST.
Recognize `منتخب`/`صورت` only at match/case statement positions; keep ordinary
identifiers intact. English `type` stays available; no new Urdu spelling is added.

Process 3.12+ f-string expression tokens while retaining literal pieces. If an
Urdu-translated expression uses debug `=`, emit an explicit constant-label field
followed by the value field, preserving original debug text and conversions in
both the translated intermediate and compiled execution. Ordinary English
f-strings remain unchanged.

Record every replacement, including generated debug labels. Map parse errors to
original filename/source/start/end character positions. Before compilation,
convert AST byte columns through the source map so code-object spans point into
the original UTF-8 source. Runtime/source-cache isolation remains the runtime
owner's responsibility.

Compared with unconditional token replacement, this protects actual API names;
compared with a private CPython-parser fork, it keeps the implementation small
and uses CPython to validate real grammar. A full CST/new-parser alternative
would remove more lexical heuristics but introduces another versioned grammar
dependency. The tokenizer's documented valid-Python-only input constraint still
requires an honest tested-grammar boundary and multiversion fixtures. This ADR
does not claim universal Python source compatibility.

## Implemented contract and compatibility

The production public functions are `translate`, `translate_with_map`,
`parse_urdu`, and `compile_urdu`. Parse/compile support exec/eval/single and
CPython compiler flags; the default is `dont_inherit=True`. The registry's 35
hard words are active. The two Urdu match/case spellings are contextual. No
synonym is added and the old experimental registry remains unchanged. The
[compiler reference](../compiler.md) specifies API parameters, collisions,
f-string behavior and mapping biases.

Native English code without Urdu hard-word collisions is unchanged in the
tested fixtures. Built-in aliases remain ordinary names. Imported path/export
names, attributes, keyword labels, strings and comments are protected.
The import-context discriminator parses isolated candidate statements without
executing imports. Hard reserved bindings are checked after CPython parsing.

F-string expression fields are handled on all four tested minors. Changed debug
expressions gain a generated constant-label field, so even direct execution of
the translated intermediate preserves original debug labels. This includes
conversions, explicit format specs, raw strings, quote reuse, nested expressions,
and multiline expression comments. Generated label text is a documented exception
to preserving each character at its original intermediate-source location; label
values and original f-string literal portions retain their meaning.

Native 3.14+ template strings pass through with Python expressions. Urdu keyword
translation inside template interpolations is explicitly rejected, because
interpolation objects expose their expression text. This limit also covers Urdu
translation inside a nested f-string within such an interpolation.
[CPython template metadata](https://docs.python.org/3.14/library/string.templatelib.html)
describes the observable expression string. Native 3.15 English lazy imports are
recognized as import contexts, including keyword-shaped Unicode exports; actual
3.15 grammar was probed before implementation. Earlier hosts retain their normal
syntax rejection. No Urdu `lazy` spelling is invented.

## Source maps and corrected edge cases

Replacements are immutable original/translated character spans. Physical line
tables handle LF, CRLF and bare CR, without treating Unicode literal separators
as new source lines. BOM is a transport marker excluded from logical code columns.
Parsing errors map original filename, text and available start/end positions.
Every located AST node maps its CPython UTF-8 byte columns back to original
UTF-8 bytes before compilation, so runtime instruction locations are original.
[CPython AST positions](https://docs.python.org/3.13/library/ast.html#ast.AST)
define the byte-column convention.

An edge sweep found the zero-length debug-marker removal boundary needed two
directions: an expression ending before the deleted `=` must map before it,
while a format colon starting after the deletion must map after it. A dedicated
regression verifies both neighbors and the Boolean value's original AST span.
Additional tests verify syntax/runtime rows after a multiline debug rewrite
removes an intermediate newline. These are executed location checks, not merely
equal-line-count assertions.

Mappings inside transformed tokens conservatively select the original token
boundaries. Generated label instructions map to the field opening. Visual RTL
columns, rich debugger stepping and third-party AST rewrites are outside the
current contract. The runtime owner supplies original-source `linecache` lifecycle
and process-state isolation; the compiler installs no global cache or import hook.

## Verification checkpoint

All commands are run from the project root, with no required nonstandard library,
network access, model download, or scientific dependency. On 2026-10-15, Windows
AMD64, 64-bit:

| Exact command | Actual interpreter | Result |
|---|---|---|
| `python -X utf8 -m unittest discover -s tests -p test_compiler.py -q` | 3.13.13 | PASS, 54 tests, 0 skips |
| `& 'C:/Users/Optim/AppData/Roaming/uv/python/cpython-3.12-windows-x86_64-none/python.exe' -X utf8 -m unittest discover -s tests -p test_compiler.py -q` | 3.12.13 | PASS, 54 tests, 0 skips |
| `& 'C:/Users/Optim/AppData/Roaming/uv/python/cpython-3.14-windows-x86_64-none/python.exe' -X utf8 -m unittest discover -s tests -p test_compiler.py -q` | 3.14.6 | PASS, 54 tests, 0 skips |
| `& '.runtimes/cpython315/python/python.exe' -X utf8 -m unittest discover -s tests -p test_compiler.py -q` | 3.15.0 | PASS, 54 tests, 0 skips |

The initial 47-test production checkpoint passed all four minors. The 48-test
checkpoint after the deletion-boundary fix also passed all four, with the then
integrated full suite at **105/105** on each. The final focused count above adds
two multiline location regressions and production scope/control/class-pattern/
type-bound behavior fixtures, plus the review correction below. Broader ongoing runtime/AI/packaging
suite counts belong to the integrator's later handoff, not this frozen checkpoint.
Python 3.11 is excluded from production; compiler tests explicitly skip there.

Independent integrator review requested CRLF/bare-CR debug-label comparison.
Differential execution exposed two related issues: generated string labels must
normalize physical newlines, and native direct expression comments are omitted
from debug labels. CPython 3.12.13 also has different `#` spelling behavior from
the later three tested minors, including `#` inside a quoted or nested-string
expression. A constant AST probe detects that native behavior without executing
user code or assuming a patch number. Token comment spans carry formatted-string
nesting depth so later hosts retain nested string spelling while omitting direct
comments. The new regression compares compiled Urdu and translated intermediate
execution to the host's native Python, across LF/CRLF/bare CR, direct/nested
comments, literal `#`, and nested template strings where supported. Final focused
54/54 passes on all four minors.

The fixtures cover real external Python exports/attributes/kwargs, reserved
bindings, relative import syntax, unchanged English hard/soft syntax, newer
host syntax, async/yield/except-star, function signatures/decorators, nested
match/case, f-string/debug formatting, normalizations, newline/BOM behavior,
nonexecuting parse/compile, modes/flags, SyntaxError text/start/end and original
runtime UTF-8 instruction spans. This is a bounded prerelease grammar contract,
not a claim of every possible Python program.

## Remaining risks, next work and rollback

`tokenize` is officially specified for valid Python input; its behavior on unknown
Urdu extension syntax remains an empirically tested dependency. Explicit contexts
and CPython validation reduce hazards but do not eliminate that upstream
constraint. [Official tokenizer warning](https://docs.python.org/3.13/library/tokenize.html)
is the reason to retain a compatibility corpus, multiversion CI, and the option
of a dedicated lexer/grammar-aware frontend if future syntax exposes gaps.

Template interpolation translation, a new Urdu type/lazy keyword, general visual
column mapping, performance certification, and unsupported-platform claims are
deferred. Any expansion needs a scoped proposal and fixtures. Human naming
acceptance is still separate from executable technical acceptance.

The integrator reviews and wires this compiler into runtime/importer/CLI only
after the focused tests pass. URD-005/006 and the compiler portion of URD-011 are
ready for that integration; runtime and release milestone completion is not
declared by this ADR. Rollback reverts entry-point imports to the separate lab or
disables production execution, preserving both regression suites. No publication,
remote write, or release approval is performed here.
