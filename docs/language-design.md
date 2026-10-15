# UrduPy language design — Phase 1

Date: 2026-10-15. Language configuration: experimental Phase 1, not a stable spec.
Task: URD-004 and the design portion of URD-025.

UrduPy puts Urdu words around Python's existing programming model. A learner can
read `اگر`, `ہر`, `فنکشن` and `واپس`, then compare the same program with
Python. Libraries retain their own names and real Python objects. The creative
work in this phase is the vocabulary, teaching progression and precise function
contract, with alternatives evaluated in the
[`naming workshop`](naming-proposals.md).

## What exists and what is a design

| Layer | Phase 1 status | Meaning |
|---|---|---|
| Guide vocabulary and naming comparisons | Written; disputed names provisional | No native-speaker acceptance is claimed. |
| 31 keyword spellings and 15 built-in alias names | Versioned experimental registry | Registry membership alone does not prove every grammar context works. |
| Token/context translation proof | Experimental; see [ADR-005](adr/005-translator.md) | Tested examples and negative cases define its evidence boundary. |
| Five Urdu/Python program pairs | Check with `python examples/verify_examples.py` | Uses an explicit isolated built-in alias dictionary, not a production runner. |
| Function semantics described below | Proposed Python-preserving contract | Only exercised cases count as experimentally verified. |
| Advanced Urdu lambda/yield/async/await/match/case/type | Deferred | Examples explicitly marked design-only do not establish implementation. |
| CLI, `.urdu` imports, exact diagnostic columns, AI integration | Future milestones | No `urdupy run`, import hook, or AI support is promised in Phase 1. |

The copied handbook describes a separate historical prototype. This checkout
began with no source and an empty test baseline. Do not apply its historical
seven-test result to this project.

## One grammar, a small new vocabulary

The intended statement structure follows Python: the condition follows `اگر`,
the iterable follows `میں`, parameters go in parentheses, and `:` begins a
block. Four spaces are the recommended indentation style; indentation groups
statements. No `ختم`, `تو` or sentence-ending marker is added.

`:` کے بعد اگلی سطروں کو چار خالی جگہیں آگے لکھیں۔ ایک ہی بلاک کی سطریں ایک
برابر فاصلے پر ہوں۔ بلاک ختم کرنے کے لیے دوبارہ پچھلے فاصلے پر آ جائیں۔

The fragment below is a design summary, not a complete parser grammar.
`expression`, `target`, `parameters` and `suite` mean the corresponding Python
forms on the selected interpreter. It deliberately leaves expression precedence,
parameter validity and detailed exception rules to CPython.

```text
condition  := "اگر" expression ":" suite
              { "ورنہ_اگر" expression ":" suite }
              [ "ورنہ" ":" suite ]
for_loop   := "ہر" target "میں" expression ":" suite
              [ "ورنہ" ":" suite ]
while_loop := "جب_تک" expression ":" suite
              [ "ورنہ" ":" suite ]
function   := { "@" expression NEWLINE }
              "فنکشن" NAME "(" parameters ")" [ "->" expression ] ":" suite
class      := { "@" expression NEWLINE }
              "کلاس" NAME [ "(" arguments ")" ] ":" suite
return     := "واپس" [ expression_list ]
import     := "درآمد" dotted_name [ "بطور" NAME ]
              | "سے" module "درآمد" imported_names
```

The loop order `ہر عدد میں اعداد` is an intentional bridge to `for number in
numbers`; Urdu prose may use a different order. Do not add a competing
`اعداد میں ہر عدد` syntax. `جب_تک شرط` repeats **while the condition is true**.
It is not an “until true” loop. These choices preserve Python's control-flow
meaning. See the [Python compound statement reference](https://docs.python.org/3.13/reference/compound_stmts.html).

Preserve ASCII punctuation/operators, `0-9`, calls, slicing, indexing, list/dict
displays, comprehensions and English keywords where the experiment supports
them. `،`, `؛`, Urdu full stops and Eastern Arabic numeric literals do not
become Python punctuation/numerals through translation. Urdu characters are
welcome inside strings and valid identifiers.

## The everyday words

| Urdu | Python | Plain Urdu explanation |
|---|---|---|
| `اگر` / `ورنہ_اگر` / `ورنہ` | `if` / `elif` / `else` | شرط کے مطابق ایک راستہ چنیں۔ |
| `ہر` / `میں` | `for` / `in` | فہرست یا دوسری قابلِ تکرار شے کی ہر قدر لیں۔ |
| `جب_تک` | `while` | شرط سچ رہنے تک دہراتے رہیں۔ |
| `روکو` | `break` | اندر والا موجودہ لوپ ختم کریں۔ |
| `جاری` | `continue` | موجودہ چکر کا باقی کام چھوڑ کر اگلے چکر پر جائیں۔ |
| `گزر` | `pass` | یہاں کوئی کام نہ کریں؛ یہ جگہ پُر کرنے کی سطر ہے۔ |
| `فنکشن` / `واپس` | `def` / `return` | کام کا نام دیں؛ اس کا جواب بلانے والے کو دیں۔ |
| `دکھاؤ` | `print` alias | نتیجہ سکرین یا مقررہ آؤٹ پٹ پر لکھیں۔ |
| `ان_پٹ` | `input` alias | ایک سطر پڑھیں؛ حاصل ہونے والی قدر متن ہے۔ |
| `حد(1, 5)` | `range(1, 5)` | 1، 2، 3، 4؛ آخری حد شامل نہیں۔ |
| `لمبائی` | `len` alias | عناصر کی تعداد لیں۔ |

The complete audit, including exceptions, scope declarations and advanced
candidates, is in [`naming-proposals.md`](naming-proposals.md). `دکھاؤ` and
`ان_پٹ` are names bound to built-ins; they are not grammar keywords. For example,
an ordinary user function named `دکھاؤ` should be able to shadow the alias under
the proposed runtime policy. Phase 1's example verifier supplies aliases through
a copied per-program built-ins dictionary; it does not modify global `builtins`.
See [ADR-006](adr/006-builtins.md) for the proposed production policy.

### Truth, absence, equality and identity

`سچ` and `جھوٹ` are the two Boolean values. `کچھ_نہیں` is Python's `None`:
an absence marker, not an empty list. Empty containers and zero can be false in
a condition without being `None`. `==` compares values; provisional `ہے`
compares whether two references point to the **same object**. [Python comparisons](https://docs.python.org/3.13/reference/expressions.html#comparisons)
define the underlying behavior.

```urdu
الف = []
ب = []
ج = الف
دکھاؤ(الف == ب)           # True: برابر قدریں
دکھاؤ(الف ہے ب)           # False: دو الگ فہرستیں
دکھاؤ(الف ہے ج)           # True: اسی فہرست کے دو نام
دکھاؤ(الف ہے کچھ_نہیں)    # False: خالی فہرست بھی ایک شے ہے
```

The first `اور`/`یا` lesson can use Booleans. Later teach Python's short-circuit
operand behavior rather than promising a Boolean result for every expression.
Use `نہیں` for negation. The composed operators retain Python order:
`قدر نہیں میں اعداد` (`value not in items`) and
`قدر ہے نہیں کچھ_نہیں` (`value is not None`). Their mildly awkward Urdu
word order is an explicit compatibility tradeoff, not natural-language parsing.

## Functions: a precise contract with a simple first lesson

```urdu
فنکشن مربع(عدد):
    واپس عدد * عدد

جواب = مربع(4)
دکھاؤ(جواب)
```

`فنکشن` ایک کام کو نام دیتا ہے۔ قوسین میں اس کام کو دی جانے والی قدروں کے
نام ہیں۔ `واپس` جواب بلانے والے کو دیتا ہے۔ `دکھاؤ` صرف آؤٹ پٹ لکھتا ہے۔

There is no required `main` function. A function definition creates a callable;
its body runs when called. An ordinary function with no explicit returned value
returns `None`, including a bare `واپس`. Calling `دکھاؤ` does not make its
text the caller's return value. This follows the [Python function tutorial](https://docs.python.org/3.13/tutorial/controlflow.html#defining-functions).

### Parameters and calls

This is the proposed full everyday signature shape:

```urdu
فنکشن بل(قیمت: int, /, تعداد: int = 1, *اضافی: int,
          رعایت: int = 0, **تفصیل: str) -> dict:
    کل = قیمت * تعداد + sum(اضافی) - رعایت
    واپس {"amount": کل, "label": تفصیل.get("نام", "عام")}

دکھاؤ(بل(100, 2, 5, رعایت=10, نام="کتاب"))
```

| Form | Contract | Urdu explanation |
|---|---|---|
| `قیمت, /` | Parameters before `/` are positional-only. | انہیں نام کے بجائے جگہ کے حساب سے قدر دیں۔ |
| `تعداد=1` | Positional or keyword parameter with a default. | قدر نہ دیں تو 1 استعمال ہوگا۔ |
| `*اضافی` | Collect excess positional arguments in a tuple. | مزید بے نام قدریں ایک tuple میں جمع ہوں گی۔ |
| `رعایت=0` after `*اضافی` | Keyword-only; bare `*` can establish the same boundary. | یہ قدر صرف `رعایت=...` لکھ کر دیں۔ |
| `**تفصیل` | Collect otherwise unmatched string-keyed keyword arguments. | باقی نام والی قدریں dictionary میں آئیں گی۔ |
| `*قدریں`, `**اختیارات` in a call | Unpack an iterable or mapping into a call. | پہلے سے جمع قدروں کو الگ آرگومنٹس کے طور پر دیں۔ |

`بل(100, تعداد=2, رعایت=10)` is valid. `بل(قیمت=100)` cannot supply the
required positional-only parameter. `فنکشن سلام(نام, *, سابقہ="سلام")`
requires `سابقہ` by keyword. Missing required arguments, duplicate values,
unexpected keywords without `**kwargs`, and invalid positional/keyword combinations
raise Python's own errors. UrduPy adds no argument reordering or automatic
translation of keyword labels. See [Python special parameters](https://docs.python.org/3.13/tutorial/controlflow.html#special-parameters).

Use simple one- or two-parameter functions first. Teach `/`, `*` and `**` only
after ordinary calls; their presence in the language does not require beginner
programs to use them.

### Defaults and mutable objects

Defaults are evaluated when the definition executes, not once per call. The
same mutable default would be shared. Teach a `None` sentinel for a fresh list:

```urdu
فنکشن شامل_کرو(عدد, اعداد=کچھ_نہیں):
    اگر اعداد ہے کچھ_نہیں:
        اعداد = []
    اعداد.append(عدد)
    واپس اعداد
```

Do not “helpfully” copy every list/default or turn this into call-time default
evaluation; that would change Python semantics. A literal default has the
ordinary ordering restrictions. This and decorators follow the
[Python function definition reference](https://docs.python.org/3.13/reference/compound_stmts.html#function-definitions).

### Scope, closures and rebinding

Function parameters and assignments create local bindings unless the relevant
scope declaration applies. `عالمی` means the current module's binding;
`غیر_مقامی` rebinds an already defined name in an enclosing function. It
does not create that outer binding. A method does not automatically treat bare
class-body names as closed-over local variables: use `self.نام` or `cls.نام`.
These are the proposed inherited rules from the [Python execution model](https://docs.python.org/3/reference/executionmodel.html).

```urdu
فنکشن گنتی_بناؤ():
    تعداد = 0
    فنکشن اگلا():
        غیر_مقامی تعداد
        تعداد += 1
        واپس تعداد
    واپس اگلا

گنو_بار = گنتی_بناؤ()
دکھاؤ(گنو_بار(), گنو_بار())    # 1 2
```

This closure is a target contract and can be exercised separately using the
experimental API. The five paired examples establish only their checked cases.
Do not promise all scope-sensitive syntax solely from this snippet.

### Decorators and annotations

Keep `@`, decorator expressions, `: type` and `-> type` unchanged. Decorators
wrap the created function under Python rules; with `@outer` then `@inner`,
application is `outer(inner(function))`. Keep real decorators such as
`@staticmethod`, `@classmethod`, `@property` and `@functools.wraps` in their
actual spelling. A decorator may return an object that is not a function.

Annotations describe interfaces; UrduPy does not add automatic runtime type
checking. Keep public/library annotations such as `int`, `str`,
`typing.Iterable` and `np.ndarray`. Their evaluation/introspection behavior
depends on the CPython version and future imports; do not freeze one evaluation
policy for all Python versions. See [Python's typing documentation](https://docs.python.org/3/library/typing.html).

The proposed lexicon also provides type aliases such as `صحیح_عدد` for `int`.
Use real English type names in interoperation examples first; changing the
source spelling does not translate third-party annotation strings or give IDEs
automatic `.urdu` support.

### Methods, classes and Python protocols

```urdu
کلاس ٹوکری:
    فنکشن __init__(self, اشیا):
        self.اشیا = list(اشیا)

    فنکشن __len__(self):
        واپس len(self.اشیا)

    @classmethod
    فنکشن بناؤ(cls, *اشیا):
        واپس cls(اشیا)
```

Instances are ordinary Python objects. `self` and `cls` are conventional
parameter names, not keywords. A bound instance method receives its instance;
`@classmethod` receives the class; `@staticmethod` adds neither automatically.
Inheritance, `super()` and Python's protocols keep their existing meaning.
Special methods such as `__init__`, `__len__` and `__iter__` must keep their
spelling so Python can find them. The same applies to framework entry points
such as PyTorch's `forward`. [Python's data model](https://docs.python.org/3.13/reference/datamodel.html)
is the contract being inherited, not a second Urdu object model.

### Generators and async: design-only Urdu spellings

`پیدا_کرو` remains a candidate for `yield`; it is not a different form of
`واپس`. A generator yields a value and suspends, resuming when advanced again.
`yield from` delegates. `غیر_متزامن` / `انتظار` remain candidates for
`async` / `await`; neither promises a new thread or parallel execution.
See [yield expressions](https://docs.python.org/3.13/reference/expressions.html#yield-expressions).

```urdu
# Design only: these Urdu advanced words are not active in the Phase 1 translator.
فنکشن مربع_دو(اعداد):
    ہر عدد میں اعداد:
        پیدا_کرو عدد * عدد

غیر_متزامن فنکشن حاصل_کرو(عمل):
    واپس انتظار عمل()
```

English `yield`, `async`, `await`, `lambda`, `match`, `case` and supported
`type` statement syntax remain the design's Python bridge, subject to the
interpreter and experimental compiler exclusions. Async generators, exception
groups, pattern matching and type-parameter syntax require dedicated tests
before claiming full support.

## Imports, API names and collisions

```urdu
درآمد math بطور ریاضی
سے statistics درآمد mean بطور اوسط
دکھاؤ(ریاضی.sqrt(81), اوسط([2, 4, 6]))
```

Names after the dot are library members; do not translate `sqrt`, `mean`,
`torch.nn.Linear`, `parameters` or `state_dict`. A colliding Python export
should be imported under a safe local name:

```urdu
# Illustrative only: assumes a real external api module exports this symbol.
سے api درآمد اگر بطور شرط
جواب = شرط(**{"واپس": 3})
```

The experiment protects tested attribute/import/keyword-label positions and
rejects unqualified active reserved words left as identifiers. Use
`getattr(obj, "اگر")` and `call(**{"اگر": value})` for an explicit Python
escape hatch. String keys remain data. No backtick or extra quoting grammar is
introduced. Import resolution between `.py` and `.urdu` is a future runtime
contract in [ADR-007](adr/007-imports.md); these examples import installed Python
standard-library modules only.

## Spelling, typing and mixed direction text

Save `.urdu` files as UTF-8. Use ordinary Urdu `ک` (U+06A9) and `ی` (U+06CC)
in canonical spellings; Arabic `ك` (U+0643) and `ي` (U+064A) are different
characters. No obligatory diacritics, zero-width joiners or bidirectional control
characters appear in the examples. An underscore `_` joins a multiword token;
a space creates separate tokens. Python normalizes identifier names using NFKC;
this does not authorize global spelling correction of source or strings. See
[Python identifier rules](https://docs.python.org/3/reference/lexical_analysis.html#names).

Recommended editing practice for Phase 1:

1. Keep the code editor's base paragraph direction left-to-right; Urdu glyphs
   still shape normally. This is a recommendation to test in a reader's editor,
   not a claim that every editor behaves identically.
2. Use a font with Urdu glyph support and enable visible whitespace. Confirm
   that `:`, commas, parentheses and `=` remain visually understandable around
   Urdu names and English calls.
3. Use ASCII `0-9`, quotes, comma, colon and bracket characters for syntax.
   Urdu punctuation remains fine inside a string or comment.
4. Compare logical cursor movement, selection/copy behavior and actual saved
   text if a mixed-direction line looks displaced. Do not fix a visual issue
   by inserting invisible direction controls into code.
5. Do not promise glyph-width diagnostic columns. Source character spans,
   UTF-8 byte positions and editor display columns are different measures.

Use ASCII example filenames for the initial tooling path. Urdu filenames and
module names need Windows/macOS/Linux, archive, shell and import tests. Current
single-host examples do not establish that portability. The feedback worksheet
records editor/keyboard setup so actual friction can inform naming choices.

### Known experimental boundary

All f-string text is preserved. Urdu active syntax words in an f-string
expression are unsupported by the bounded experiment; use an English expression
or compute an Urdu expression in a preceding statement. Literal Urdu text,
tested attribute references and keyword labels inside f-strings are separate
cases. Consult the current compiler ADR and tests for the exact rejection rule.
Full f-string grammar and precise Unicode diagnostic mapping remain future work.

## Five comparison exercises

These are reading exercises for the workshop, not completed usability evidence.
For execution, the five complete core pairs are in [`examples/`](../examples/README.md).
Show each Urdu block before its Python equivalent; ask the reader to predict
the result and explain the significant words.

### 1. Choose a branch

```urdu
عمر = 20
اگر عمر >= 18:
    دکھاؤ("بالغ")
ورنہ:
    دکھاؤ("کم عمر")
```

```python
عمر = 20
if عمر >= 18:
    print("بالغ")
else:
    print("کم عمر")
```

Ask: what prints, and what changes when `عمر = 12`? Then use the earlier
three-list example to distinguish `ہے` from `==` and an empty list from None.

### 2. Visit values

```urdu
ہر عدد میں حد(1, 4):
    دکھاؤ(عدد * عدد)
```

```python
for عدد in range(1, 4):
    print(عدد * عدد)
```

Ask: is 4 included? What changes when `گزر`, `جاری` or `روکو` is the first
line of the body? Separately show `جب_تک عدد < 4` and check loop polarity.

### 3. Return an answer

```urdu
فنکشن جمع(الف, ب=1):
    واپس الف + ب

جواب = جمع(4)
دکھاؤ(جواب)
```

```python
def جمع(الف, ب=1):
    return الف + ب

جواب = جمع(4)
print(جواب)
```

Ask: what value enters `جواب`? If `واپس` changes to `دکھاؤ`, what gets
printed, and what does the caller receive? Introduce `/` and `*` only after
this distinction is understood.

### 4. Use a Python library

```urdu
سے math درآمد sqrt بطور جذر
دکھاؤ(جذر(81))
```

```python
from math import sqrt as جذر
print(جذر(81))
```

Ask: which name belongs to the library and which is local? Then compare
`نام = ان_پٹ("نام: ")` with proposed `نام = پوچھو("نام: ")` on a card
explicitly labeled alternative. Does either wording imply the input is a number?

### 5. Keep a real AI API — design only

```urdu
# Requires future AI validation and an installed torch; not run in Phase 1.
درآمد torch
کلاس چھوٹا_ماڈل(torch.nn.Module):
    فنکشن __init__(self):
        super().__init__()
        self.layer = torch.nn.Linear(4, 2)

    فنکشن forward(self, x):
        واپس self.layer(x)
```

```python
import torch
class چھوٹا_ماڈل(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.layer = torch.nn.Linear(4, 2)

    def forward(self, x):
        return self.layer(x)
```

Ask: why do `torch.nn.Module`, `__init__` and `forward` keep their names?
Then show a separate English generator/async concept card before comparing
the naming challengers for `yield` and `async`. Do not imply the model example
proves training, tensor interoperability or framework compatibility.

Record responses in the [feedback worksheet](naming-proposals.md#reader-feedback-worksheet--not-yet-conducted).
The class/protocol core pair supplies a dependency-free bonus exercise.

## Next design gate

Phase 1 ends with an inspectable proposal, bounded code evidence and unresolved
naming questions stated explicitly. M1 should grow a production compiler/runner
one tested construct at a time, collect reader feedback for controversial names,
and keep the migration policy in [ADR-004](adr/004-lexicon.md). No naming
preference becomes stable merely because an example executes.
