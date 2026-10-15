# ADR-005: A bounded, span-preserving translator experiment

- Date: 2026-10-15
- Status: Experimental decision for M0; production strategy remains proposed
- Owner: Compiler agent, URD-003; bounded proof for URD-005
- Interfaces: `urdupy.experimental.translate`, `translate_with_spans`, `compile_urdu`

## Scope before implementation

The supplied historical prototype is absent. The new checkout's baseline command
`python -m unittest discover -s tests -v` found **0 tests**, on CPython 3.13.13.
CPython 3.11.9 is also installed. There is no Git repository. This task owns only
`urdupy/experimental/*`, `tests/test_translation.py`, and this ADR. The integrator
owns the executable registry and shared tracking.

Implement the smallest executable experiment that tests the guide's grammar and
identifier hazards. Preserve existing characters outside explicitly recorded
keyword replacements. Keep built-in aliases as identifiers. Do not add an
importer, runner, CLI, public API stability claim, or scientific dependency.
Rollback consists of removing these experimental files after reviewing their
dependents; no historical implementation is being migrated.

## Options and provisional decision

1. Blind text or unconditional NAME substitution is small but corrupts literal
   text, attributes, named imports, and Unicode keyword argument labels.
2. Public `tokenize` plus original-source spans, narrow import/call context, and
   CPython AST validation provides a dependency-free way to investigate those
   hazards. It does not constitute a complete Python grammar.
3. A CST library or a versioned grammar-aware pre-parser could distinguish all
   binding and soft-keyword positions, at a substantially larger maintenance and
   compatibility cost. Prototype and compare this for M1 rather than assuming a
   library accepts Urdu extension syntax.
4. AST rewriting alone cannot parse the unknown Urdu statement keywords first.

Choose option 2 **only as a bounded M0 experiment**. The production choice awaits
broader fixtures and a review of tokenizer behavior on extension syntax. Python
documents `tokenize` for valid Python only; Urdu extension input therefore has no
documented stability guarantee. The module's reconstruction helper also permits
spacing changes, which is why this experiment copies original source slices.
[Official tokenizer contract](https://docs.python.org/3.13/library/tokenize.html)

## Executable contract

```python
from urdupy.experimental import compile_urdu, translate, translate_with_spans

intermediate = translate("اگر سچ:\n    گزر\n", "sample.urdu")
translation = translate_with_spans("اگر سچ:\n    گزر\n", "sample.urdu")
code = compile_urdu("اگر سچ:\n    گزر\n", "sample.urdu")
```

`translate` returns intermediate text. It checks tokenization and the f-string
restriction, but does **not** promise the result parses or executes. Built-in
aliases remain Urdu identifiers, so the text is not automatically standalone
Python. `compile_urdu` parses the intermediate text, rejects colliding reserved
bindings, and compiles a normal CPython code object. It does not execute imports,
set up aliases, register hooks, or modify interpreter globals. There is no file
reader: the caller supplies decoded `str`, normally from UTF-8 input.

`translate_with_spans` returns immutable `Translation(text, edits)`. Each `Edit`
contains the original and translated half-open character ranges, the old and new
token text, and the original 1-based line and 0-based character column. Offsets
count Python string characters, including an optional initial U+FEFF BOM; they
are not UTF-8 bytes or editor display cells. Newlines, comments, strings,
indentation, tabs, trailing spaces, and gaps between replacements are copied.
LF and CRLF have dedicated tests. Translation preserves an initial BOM;
`compile_urdu` removes exactly that initial BOM before CPython parsing.

### Reserved words and external APIs

The 31 active registry words are reserved when unqualified in UrduPy source,
including mixed Urdu/English files. This is a deliberate difference from English
Python files that happen to use those Urdu words as ordinary variable names.
They cannot name an ordinary variable, function, parameter, or imported binding.
The 15 built-in aliases are ordinary, shadowable identifiers. The six deferred
Urdu candidates are not active replacements. English hard and soft keywords
remain CPython's keywords; `match`, `case`, and `type` identifiers are untouched.

Protected contexts preserve an API's real spelling:

| Source | Experimental rule |
|---|---|
| `obj.اگر` | Preserve the attribute after `.` |
| `api(اگر=1)` | Preserve a keyword label directly inside call-like parentheses |
| `سے api درآمد اگر بطور condition` | Preserve the exported name, translate import syntax, bind a safe alias |
| `درآمد اگر.واپس بطور library` | Preserve the module path, bind a safe alias |
| `سے . درآمد thing` | Preserve relative path punctuation and locate the actual import delimiter |
| `سے .درآمد درآمد thing` | Preserve the module named `درآمد`; the next occurrence is the delimiter |
| `سے api درآمد اگر` | `translate` preserves the export; `compile_urdu` rejects its reserved binding and asks for an alias |
| `api(**{"اگر": 1})` | Standard dictionary unpacking remains an escape hatch |

The ordinary import forms are still CPython imports. An isolated import statement
is parsed to select the `from … import` delimiter when a module/export name also
spells `درآمد`; this avoids a whitespace-dependent rule. No `.urdu` import loader
is implemented. Wildcard imports remain ordinary Python; the compiler cannot
discover their exports statically. Reserved exports obtained that way still
cannot be used as bare UrduPy names. Prefer explicit aliases or a module plus
`getattr(module, "اگر")`.

Calls are recognized from nearby token shapes and a bracket stack, with a
distinction for function parameter lists. This is a heuristic, not a complete
expression parser. Final AST validation prevents a protected default parameter
inside a nested `lambda` from creating an unnoticed reserved binding. Broader
grammar combinations require additional fixtures before M1 can claim them.

### F-strings: explicit Python-only expressions

Every complete f-string is opaque to replacement. The experiment parses its
expression AST using the host CPython version and rejects active Urdu reserved
names used unqualified there. This catches even `f"{سچ}"`, which CPython would
otherwise accept as a name and potentially raise `NameError` at execution.

| Form | Result |
|---|---|
| `f"اگر {value!r:>3}"` | Preserved exactly |
| `f"{obj.اگر}"` | Attribute spelling preserved |
| `f"{api(واپس=3)}"` | Keyword label preserved |
| `f"{len('اگر واپس')}"` | Embedded string contents preserved |
| `f"{سچ}"` | Explicit `ExperimentalSyntaxError`: f-string expressions are Python-only |
| `f"{1 اگر سچ else 2}"` | Unsupported; rejected before execution |

Nested f-strings and format-spec expressions follow the same restriction. Urdu
nonreserved identifiers and built-in aliases remain ordinary Python names inside
them. For example, compute an Urdu condition into `نتیجہ` first and interpolate
`f"{نتیجہ}"`. Malformed f-strings may report a host tokenizer error or the
experiment's Python-only diagnostic; no polished diagnostic guarantee exists.

Python 3.12 changed f-string tokenization from a whole `STRING` token to
`FSTRING_START`/`FSTRING_MIDDLE`/`FSTRING_END` with expression tokens. The experiment
collapses the latter groups, including nested groups, before replacement.
Host-version syntax remains decisive: quote reuse works in the 3.13 fixture and
is rejected in 3.11. This does not backport newer grammar.
[Official 3.12 f-string changes](https://docs.python.org/3.12/whatsnew/3.12.html#porting-to-python-3-12)

### Source locations and limits

Recorded replacement ranges are enough to inspect edits and prove that gaps
were preserved. They are not a finished source-map API. No inverse mapping is
implemented for locations inside a changed token, traceback instruction spans,
multiline expressions, or editor display columns. Equal line counts are not
evidence of equal column offsets.

Tests verify the supplied `.urdu` filename and runtime line number. Native
`SyntaxError` columns refer to the **translated** source. Custom AST validator
errors convert CPython's UTF-8 byte columns to translated character columns;
they still do not map back to original Urdu columns. CPython documents AST
columns as UTF-8 byte offsets.
[Official AST location contract](https://docs.python.org/3.13/library/ast.html#ast.AST)

No original-source `linecache` integration is installed, so a traceback formatter
may show no source or look up a physical file independently. F-string restriction
errors point at the literal's start, not a mapped embedded-expression span.
The filename/line evidence must not be presented as production diagnostics.

## Executed evidence

The first focused test run deliberately failed on the absent implementation
(`ImportError`, one failed test module). After implementation, the 44-test suite
passed on both local versions. Independent integrator review found the missing
relative-only import case; new regressions reproduce it and the import delimiter
selection now handles relative paths and keyword-shaped module/export names.
Final focused verification on 2026-10-15:

| Command, from project root | Environment | Actual result |
|---|---|---|
| `python -X utf8 -m unittest discover -s tests -p test_translation.py -v` | CPython 3.13.13, Windows x64 | PASS, 48 tests, 0 skipped |
| `py -3.11 -X utf8 -m unittest discover -s tests -p test_translation.py -v` | CPython 3.11.9, Windows x64 | PASS, 48 tests, 0 skipped |
| `python -X utf8 -m unittest discover -s tests -v` | CPython 3.13.13, Windows x64 | PASS, 57 tests, 0 skipped, including integrator's 9 design tests |
| `py -3.11 -X utf8 -m unittest discover -s tests -v` | CPython 3.11.9, Windows x64 | PASS, 57 tests, 0 skipped, including integrator's 9 design tests |

`-X utf8` is used because this Windows console's default output encoding cannot
print every Urdu character. The suite has no required nonstandard dependency,
network request, model weight, or scientific library. No other Python minor,
platform, package build, or native extension compatibility was verified here.

The negative comparator intentionally substitutes every matching `NAME` in
three separate fixtures. It produces invalid Python for each of these imports,
attributes, and keyword labels:

| Input | Blind NAME substitution | Experiment |
|---|---|---|
| `from api import اگر as condition` | `if` used as exported name: invalid | Unchanged, compilable |
| `obj.واپس` | `.return`: invalid | Unchanged, compilable |
| `api(سچ=1)` | `True=1`: invalid | Unchanged, compilable |

An additional isolated real Python module fixture proves that keyword-shaped
exports resolve to the original objects through safe aliases and attributes.
The suite compares Urdu/Python function and control-flow values, real built-in
output, Unicode kwargs, exceptions, source gaps/spans, BOM/CRLF handling,
lookalikes, soft keywords, ordinary async/generator/lambda pass-through, normal
and nested f-strings, and explicit f-string limitations. The version-dependent
`type` statement test expects 3.11 to reject that newer Python grammar rather than
counting it as a skipped supported feature.

## Production decision and handoff

URD-003's M0 comparison and proof are complete for review. URD-005 has a bounded
experiment, **not** a completed M1 compiler. Preserve its negative API-context
fixtures when choosing a production parser. No accepted keyword spelling or
public runtime interface is changed by this experimental ADR.

The next scoped tasks are:

1. Compare a versioned grammar-aware pre-parser/CST approach against these fixtures
   and additional Python grammar combinations; settle the undocumented tokenizer
   dependency before promising supported source compatibility.
2. Specify Urdu f-string expression support separately, across the 3.11/3.12+
   boundary, with exact embedded-expression mappings and soft-keyword handling.
3. Design bidirectional Unicode source maps and diagnostic/linecache isolation
   before claiming original source columns or debugger support.
4. Add a separately reviewed runner and opt-in importer after the lexical and
   built-ins contracts are accepted. Relative import syntax tests do not prove
   `.urdu` package loading.
5. Validate the current stable CPython identified by the research agent in CI;
   two local minors do not establish the intended release support range.

The integrator alone updates the shared handbook, compatibility matrix, and
handoff. Rollback removes or disables this opt-in experiment and its dependent
demonstrations after reviewing the file list; keep the regression cases as design
evidence when replacing its implementation.
