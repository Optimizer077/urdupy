# Compiler and source locations

The additive [complete Urdu mode](complete-urdu.md), specified in
[ADR-015](adr/015-complete-urdu-surface.md), enables a reserved library spelling
catalog with a leading `# اردوپائی: مکمل` comment. It contributes original-source
span edits before debug-label reconstruction and source-map generation. Imports
bind native modules; names, stores, parameters, keyword labels and attributes
lower consistently. No dependency imports run during translation or checking.
Without the directive the original compiler contract below remains in force.

UrduPy's prerelease compiler runs through CPython. The production entry points
live in `urdupy.compiler`; the older `urdupy.experimental` laboratory retains its
Phase 1 restrictions for reproducible historical evidence.

## Python API

```python
from urdupy.compiler import compile_urdu, parse_urdu, translate, translate_with_map

source = "فنکشن مربع(x):\n    واپس x * x\n"
text = translate(source, filename="square.urdu")
mapping = translate_with_map(source, filename="square.urdu")
tree = parse_urdu(source, filename="square.urdu")
code = compile_urdu(source, filename="square.urdu")
```

All inputs are decoded `str`. File-reading/runtime APIs own UTF-8 decoding and
execution setup. `translate` returns intermediate Python text; it does not execute
or promise that invalid source will parse. `translate_with_map` adds the original
source and location helpers. `parse_urdu` returns a CPython AST with original
locations. `compile_urdu` returns a normal code object and executes no source or
imports. Built-in aliases such as `دکھاؤ` remain identifiers; execution requires
the runtime's module-local builtins dictionary.

The parse/compile signatures accept `mode="exec"`, `"eval"`, or `"single"` and
keyword-only `flags=0`, `dont_inherit=True`, `optimize=-1`. Normal CPython flags
include top-level-await and type-comment handling. `PyCF_ONLY_AST` makes
`compile_urdu` return the mapped AST, matching built-in `compile`. Interactive
incomplete-input flags are tested. The default does not inherit this module's
future compiler flags. CPython 3.12 or newer is required; native newer syntax
still requires the interpreter that implements it.

## Supported source contract

The production registry contains 35 hard Urdu syntax words: the Phase 1 set plus
the guide's `لامبڈا`, `پیدا_کرو`, `غیر_متزامن`, and `انتظار`. They are reserved as
unqualified identifiers in mixed Urdu/English source. There is one spelling per
construct; implementation does not establish native-speaker acceptance of the
provisional names.

The tested grammar includes Python-shaped conditions/loops, Boolean/identity
operators, comprehensions, generators, lambda, function signatures, decorators,
annotations, classes, scope statements, imports, context managers, exceptions,
`سوائے*`, async functions, async iteration/context managers, and await. Python
punctuation, operators, assignment expressions, protocol names and genuine
library APIs retain their CPython meaning. The host parser validates the final
grammar; this is not a claim that every possible grammar combination is covered.

`منتخب` and `صورت` are contextual equivalents of `match` and `case`. A block
header establishes match context; case appears at that match block's case
indentation. These spellings remain ordinary identifiers elsewhere:

```python
منتخب = "عام نام"
صورت = 3

منتخب صورت:
    صورت 3 اگر سچ:
        result = منتخب
    صورت _:
        result = کچھ_نہیں
```

The first assignment uses an identifier; the later header uses syntax. Nested
match blocks, captures, guards, class/dictionary/list patterns, and mixing English
`match` with Urdu `صورت` are covered by fixtures or the host grammar. No Urdu
`type` keyword is added. English `type` statements and English soft identifiers
remain available on the relevant CPython version.

## API names and collisions

| Situation | Rule |
|---|---|
| `object.اگر` | Preserve attribute spelling |
| `api(واپس=3)` | Preserve a Unicode call keyword label |
| `سے api درآمد اگر بطور condition` | Preserve exported name and bind a safe alias |
| `درآمد اگر.واپس بطور library` | Preserve the module path |
| `سے . درآمد child` | Keep Python relative-import grammar |
| `سے .درآمد درآمد child` | Distinguish a module named `درآمد` from the delimiter |
| `سے api درآمد اگر` | Reject a reserved unqualified binding; request an alias |
| `api(**{"واپس": 3})` | Ordinary dictionary unpacking is an escape hatch |

Regular builtin aliases are shadowable names, not keywords. Wildcard imports use
normal Python semantics; static compilation does not inspect their exports.
Keyword-shaped exports still need a safe explicit alias or module attribute for
bare access. CPython's identifier normalization applies, and UrduPy does not
silently correct Arabic/Persian lookalikes or strip invisible characters.

## F-string expressions and debug labels

Urdu syntax works inside f-string expressions, nested f-strings and nested
format fields on the production interpreter range:

```python
result = f"جواب: {1 اگر سچ ورنہ 2}"
formatted = f"{7!r:>{3 اگر سچ ورنہ 1}}"
debug = f"{سچ=}"
```

These produce `جواب: 1`, two spaces followed by `7`, and `سچ=True`.
Literal text, escaped braces, raw-string behavior, conversions and format specs
retain their meaning. External attributes and keyword labels remain protected
inside expressions too. Quote reuse and expression comments use the host's
native 3.12+ grammar.

Translating a debug expression normally changes the label CPython prints. To
preserve it, UrduPy generates a constant-label field followed by the value field.
For example, `f"{سچ=}"` becomes the equivalent of `f"{'سچ='}{True!r}"`. The
translated intermediate itself prints the original label. Existing English
debug f-strings are unchanged.

Generated debug labels are an explicit exception to copying every source
character in place. The label follows the host CPython's physical-newline and
comment rules and is stored as a generated Python string constant; the debug
marker and trailing label whitespace are replaced. CRLF and bare CR normalize
to LF in the label. Direct comments are omitted under the newer native rules;
the older host behavior for `#` in debug expression spelling is detected with a
constant AST probe. This can change intermediate physical line counts.
The source map records the changes so compiled instruction lines and columns
still refer to the original program. Ordinary literal portions, strings and
comments outside this transformation are retained verbatim.

## Newer native Python syntax

On 3.14/3.15, native template strings (`t"..."`) with Python expressions pass
through unchanged, including Urdu literal text. Template interpolation objects
expose their expression's source text, so translating it would alter public
metadata. Urdu syntax inside template interpolations is explicitly rejected.
Compute a result in an ordinary expression first and interpolate its nonreserved
name. Attributes and keyword labels that need no translation remain usable.
The [CPython template API](https://docs.python.org/3.14/library/string.templatelib.html)
documents that expression text is observable.

On 3.15, English `lazy import`/`lazy from … import …` syntax is preserved,
including Unicode API exports. No Urdu spelling for `lazy` is introduced.
Earlier hosts reject newer grammar through CPython; the frontend does not
backport template strings or lazy imports.

## Source map and diagnostics

`Translation` provides `.source`, `.text`, `.filename`, and immutable `.edits`.
Each edit records original/translated half-open character spans, old/new text,
and a kind (`keyword`, `debug_label`, or `debug_marker`). Raw offsets count
Python string characters, not UTF-8 bytes or visual editor columns.

`map_position(line, column, end=False)` maps translated 1-based lines and
0-based character columns to the original program. `end=True` uses the end of a
changed token for an interior boundary. At a deleted span, a following start
maps after the deletion and a preceding end maps before it. An initial BOM is
preserved in raw text/spans but is not a visible code column. LF, CRLF, and bare
CR are supported; Unicode separators inside string literals are not physical
Python lines.

`map_error(error)` converts a parsing `SyntaxError` from intermediate text into
original filename, source text, start offset and available end offset. CPython's
AST uses UTF-8 byte columns; the compiler converts these through character spans
and writes original UTF-8 byte columns before code generation. Tests inspect
actual runtime exception instruction spans, including Unicode prefixes and
generated debug-label insertions/deletions. Semantic compilation errors such as
`واپس` outside a function also receive original source text and character offsets.

This is source-location support, not a debugger or universal editor-display map.
Inside a changed token, the range maps to the entire original token rather than
inventing a character-by-character relationship. Generated label instructions
map to the original field opening. Rich debugger stepping, visual RTL columns,
formatter integration, and arbitrary AST rewrites by callers are not covered.
The compiler does not register `linecache`; the runtime owns cache lifetimes and
traceback source display.

## Verification and boundaries

The compiler suite runs on Windows AMD64 with CPython 3.12.13, 3.13.13, 3.14.6,
and 3.15.0. Exact checkpoint commands/results are in
[ADR-011](adr/011-production-compiler.md). Tests use the standard library, real
temporary Python API objects, differential results, and original-source span
checks. No scientific library is needed by this frontend suite.

The host tokenizer's documented guarantee covers valid Python rather than Urdu
extension syntax. Explicit contexts, CPython validation, and multiversion tests
provide the supported prerelease boundary; they do not prove universal grammar
coverage. Invalid/incomplete input may be translated only through the usable
token prefix before CPython reports the original-source error. Performance on
very large generated sources and untested platforms is not certified here.
Changes to this contract require regression coverage and a migration note.
