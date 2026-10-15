# UrduPy local language reference

This reference describes the production frontend's **`1.0-local`** technical
contract for CPython **3.12–3.15**.
Package and language versions are separate; see [stability](stability.md).
The original Phase 1 design laboratory remains available through
`urdupy.experimental` with its older limitations. Use `urdupy.compiler` and the
runtime/CLI for the implementation described here. Actual environments and
remaining limits are recorded in [implementation evidence](implementation-handoff.md).

## Structure and source

UrduPy inherits CPython's statement shapes, expression precedence, indentation,
ASCII punctuation, operators, calls, comprehensions, indexing, decorators,
annotations and object model. Blocks use `:` and indentation; four spaces are
recommended. No filler words, sentence endings, conjugation or automatic argument
reordering are added. English Python syntax is retained, subject to the explicit
Urdu reserved-word rules below. It is not unrestricted natural-language Urdu.

Save UTF-8 source; UTF-8 BOM is permitted. LF and CRLF are accepted. Use ASCII
digits `0-9` and ordinary Python punctuation in syntax. Unicode identifiers follow
the host Python's identifier/NFKC rules. The compiler does not transliterate names
or globally correct Arabic/Urdu letter variants. Suspicious invisible characters
must not be used to visually reorder code; consult actual diagnostic tests for
rejected source forms. Runtime source positions refer to saved source; visual
glyph width and editor cursor columns can differ from character/UTF-8 positions.

## Hard keywords

These 35 Urdu spellings are reserved as unqualified source names. Their counterpart
has the same Python meaning; this is one preferred spelling per concept.

| Urdu | Python | Urdu | Python |
|---|---|---|---|
| `اگر` | `if` | `ورنہ_اگر` | `elif` |
| `ورنہ` | `else` | `ہر` | `for` |
| `میں` | `in` | `جب_تک` | `while` |
| `اور` | `and` | `یا` | `or` |
| `نہیں` | `not` | `سچ` | `True` |
| `جھوٹ` | `False` | `کچھ_نہیں` | `None` |
| `روکو` | `break` | `جاری` | `continue` |
| `گزر` | `pass` | `ہے` | `is` |
| `فنکشن` | `def` | `واپس` | `return` |
| `کلاس` | `class` | `درآمد` | `import` |
| `سے` | `from` | `بطور` | `as` |
| `کوشش` | `try` | `سوائے` | `except` |
| `آخرکار` | `finally` | `اٹھاؤ` | `raise` |
| `ساتھ` | `with` | `تصدیق` | `assert` |
| `حذف` | `del` | `عالمی` | `global` |
| `غیر_مقامی` | `nonlocal` | `لامبڈا` | `lambda` |
| `پیدا_کرو` | `yield` | `غیر_متزامن` | `async` |
| `انتظار` | `await` | | |

`ہر x میں items:` mirrors `for x in items:`. `جب_تک condition:` repeats while
the condition is true. `x نہیں میں items` maps to `x not in items`;
`x ہے نہیں کچھ_نہیں` maps to `x is not None`. `سوائے*` preserves the normal
exception-group punctuation. Assertions remain Python assertions and are not a
general security/validation mechanism.

`سچ`/`جھوٹ` are Booleans. `کچھ_نہیں` is None, distinct from false, zero and
empty containers. `ہے` means object identity; `==` means equality. `اور`/`یا`
retain Python's short-circuit operand-return behavior rather than always returning
a Boolean. These meanings are intentionally precise even where natural Urdu
reading might suggest a different comparison or loop direction.

## Contextual keywords

`منتخب`/`صورت` correspond to `match`/`case` only in their statement/pattern
contexts. Ordinary identifiers with those spellings remain possible elsewhere:

```urdu
منتخب = "عام نام"
عدد = 2
منتخب عدد:
    صورت 1:
        دکھاؤ("ایک")
    صورت _:
        دکھاؤ("دوسرا")
```

Python's wildcard `_`, pattern operators and guards remain unchanged. There is
no Urdu word for the `type` statement in this contract. Keep English `type` in a
type-alias statement and `قسم` for the ordinary builtin alias described below.
Host-version restrictions on Python syntax still apply.

## Functions, generators and async

```text
فنکشن name(parameters) [-> annotation]: suite
واپس [value]
کلاس Name[(bases_and_keywords)]: suite
غیر_متزامن فنکشن name(parameters): suite
انتظار awaitable
پیدا_کرو value
پیدا_کرو سے iterable
```

Parameters, `/`, `*`, `*args`, `**kwargs`, defaults, annotations, decorators and
call binding follow Python. Defaults are evaluated at definition time; mutable
defaults are not automatically copied. A bare return or ordinary fall-through
returns None. `دکھاؤ` writes output; it does not return the displayed value.

`عالمی` applies to a module binding; `غیر_مقامی` rebinds an existing enclosing
function binding. Locals and parameters shadow builtins normally. Keep protocol
names such as `__init__`, `__iter__`, `__len__`, `__enter__`, and `forward` exact.
Annotations do not introduce runtime type enforcement.

`پیدا_کرو` suspends a generator and yields a value, unlike return. `پیدا_کرو سے`
delegates to an iterable. `غیر_متزامن` and `انتظار` retain coroutine/awaitable
semantics; neither implies a new thread, parallel execution or a new event loop.
`لامبڈا x: x + 1` retains lambda's expression-only body.

## Builtin aliases are ordinary names

| Urdu name | Actual builtin | Urdu name | Actual builtin |
|---|---|---|---|
| `دکھاؤ` | `print` | `ان_پٹ` | `input` |
| `حد` | `range` | `لمبائی` | `len` |
| `فہرست` | `list` | `لغت` | `dict` |
| `مجموعہ` | `set` | `صحیح_عدد` | `int` |
| `اعشاری` | `float` | `متن` | `str` |
| `ترتیب` | `sorted` | `گنو` | `enumerate` |
| `جوڑ` | `sum` | `قسم` | `type` |
| `کھولو` | `open` | | |

Runtime-created module builtins contain references to the actual CPython objects,
with a separate dictionary per module. A user assignment/function/parameter can
shadow an alias. Aliases are not automatically inserted as module globals or
star exports. The copied dictionary snapshots builtins when the environment is
created; subsequent global monkey-patching does not retroactively update that
copy. This is an execution convention, not a sandbox or separate type hierarchy.
`پوچھو` and other friendly candidates are not accepted synonyms.

## Strings, f-strings and API collisions

Strings, comments and f-string literal text are data and retain their spelling.
The production compiler handles Urdu syntax inside replacement expressions and
nested format fields; debug f-string labels retain original expression text.
The supported syntax is still that of the selected host CPython. The legacy
experimental API deliberately has stricter f-string rules.

Native 3.14+ template strings with Python expressions pass through unchanged.
Urdu syntax needing translation inside template interpolations is explicitly
rejected because the interpolation's expression text is observable metadata;
compute the result first and interpolate a nonreserved name. Native 3.15 English
`lazy import`/`lazy from ... import ...` forms pass through; no Urdu spelling for
`lazy` is introduced. Earlier hosts retain their own grammar restrictions. See
the [compiler contract and source-map limits](compiler.md).

Protect real API attributes, imported symbols and call keyword labels:

```urdu
# Assumes a Python module named api exports an attribute named اگر.
درآمد api
سے api درآمد اگر بطور شرط
جواب = شرط(واپس=3)
دوسرا = api.اگر(**{"واپس": 4})
```

Import a keyword-shaped export under a nonreserved local alias. Use
`getattr(obj, "اگر")` or `call(**{"اگر": value})` as explicit Python escape
hatches. Quoted keys remain data. UrduPy does not translate external package
names, methods, keyword argument labels, signatures or protocol spellings.

## Modules and execution

`درآمد`, `سے` and `بطور` retain Python import statement shapes and relative-dot
syntax. Top-level files execute normally; no custom main function is required.
The Urdu importer is opt-in and not installed simply by importing `urdupy`.
Python programs can use the owned `install_importer()` context to import `.urdu`
files. Use the production runtime/CLI to set up aliases and import discovery.

The finder runs immediately before standard `PathFinder` and first asks it for
a spec. A concrete Python/native/zip module wins across the full search path,
even if an earlier entry contains a same-named `.urdu` file. Earlier custom,
builtin and frozen finders retain priority. A regular Urdu package uses
`package/__init__.urdu` when no concrete standard candidate resolves. It can
supply an initializer where Python would otherwise discover a namespace;
a loose `.urdu` module does not displace that namespace.

Normal importlib module identity, caching and partial circular initialization
apply. Relative imports and package metadata use the actual module context.
Closing the hook does not remove successfully imported modules. No translated
bytecode cache is written. `iter_urdu_modules(path)` provides explicit Urdu module
discovery; standard `pkgutil` is not monkey-patched.

See the current [runtime/import ADR](adr/013-runtime-imports.md) and
[implementation handoff](implementation-handoff.md) for actual fixtures and
bounded exclusions. The M0 [import ADR](adr/007-imports.md) remains the historical
record of the appended-finder problem that prompted this choice.

## Scope of the contract

The compiler remains a frontend to CPython, with a tested grammar boundary and
host tokenizer dependency. No universal “100% Python” claim, alternative VM,
rewritten library ecosystem or cross-platform editor guarantee follows. Exact
version/platform/library runs live in evidence, not in this vocabulary table.
See [stability policy](stability.md), [CLI](cli.md), and
[AI compatibility](ai-compatibility.md).
