# UrduPy naming workshop

Date: 2026-10-15. Task URD-004. Status: **provisional design and reader exercises**.

The project name is **UrduPy**; the requested folder and Python package spelling
are `urdupy`, and the source extension is `.urdu`. A possible Urdu reading is
`اردو پائی`; this is a display-name suggestion, not an alternative command.
The distribution name still needs registry/ownership research. Do not infer
availability from this document.

## The naming idea

Use everyday Urdu for flow (`اگر`, `ورنہ`, `ہر`, `واپس`), familiar technical
loanwords for abstractions (`فنکشن`, `کلاس`), and a small family of useful
built-in names (`دکھاؤ`, `حد`, `لمبائی`). Prefer one form a learner can find
in every tutorial. A technically precise English keyword can remain the escape
hatch while an advanced Urdu term is being evaluated.

All ease/readability observations below are **agent hypotheses**. We have not
consulted native speakers or measured beginner comprehension. The user permits
creative departures from the guide, but that permission does not supply reader
evidence. This phase prepares choices without silently adopting new synonyms.

## Audit of the guide's complete keyword list

`Retain` means keep the guide spelling in the experimental design, not stable
language approval. The executable subset and exclusions are separately documented
in [`language-design.md`](language-design.md).

| Python | Guide spelling | Decision / alternative considered | Teaching or naming concern |
|---|---|---|---|
| `if` | `اگر` | Retain; no extra `تو` | The block colon already has a job; an added word gives little benefit. |
| `elif` | `ورنہ_اگر` | Retain over `یا_اگر` | Keeps the visible relation to `ورنہ`; underscores make a single token. |
| `else` | `ورنہ` | Retain over `نہیں_تو` | Avoids confusing the Boolean negation word with an alternative branch. |
| `for` | `ہر` | Retain over `دہراؤ` | Read `ہر x میں items`; this visits iterable items, not only counted repetitions. |
| `in` | `میں` | Retain | Membership and iteration use the same counterpart as Python. |
| `while` | `جب_تک` | Retain; compare `جب_تک_سچ` in prose only | Explain that repetition continues while the condition is true; an English reading of “until” can invert it. |
| `and` | `اور` | Retain | Short-circuiting and operand results need examples; it does not always return a Boolean. |
| `or` | `یا` | Retain | Inclusive Boolean alternative, with Python short-circuit behavior. |
| `not` | `نہیں` | Retain | Keep one negation word; combinations remain `نہیں میں` and `ہے نہیں`. |
| `True` | `سچ` | Retain | A Boolean value; avoid treating it as a predicate that proves facts. |
| `False` | `جھوٹ` | Retain; `غلط` challenger | `غلط` can suggest an error; `جھوٹ` can suggest a moral judgment. Reader exercise needed. |
| `None` | `کچھ_نہیں` | Retain provisionally; NAME-004 | Absence of a value differs from an empty container. |
| `break` | `روکو` | Retain over `ختم` | Ends the innermost loop, not the whole script. |
| `continue` | `جاری` | Retain over `اگلا` | Skips the rest of one iteration; does not resume at the next statement. |
| `pass` | `گزر` | Retain provisionally; NAME-002 | A no-op placeholder; easy to confuse with loop continuation. |
| `is` | `ہے` | Retain provisionally; NAME-003 | Highest beginner semantic risk: identity differs from equality. |
| `def` | `فنکشن` | Retain over `عمل` / `تعریف` | Familiar borrowing identifies the abstraction; `عمل` is too broad. |
| `return` | `واپس` | Retain over `لوٹاؤ` | Returns to the caller; contrast with terminal output. |
| `class` | `کلاس` | Retain over `جماعت` / `سانچہ` | The borrowing transfers to Python learning; `سانچہ` is useful explanatory prose. |
| `import` | `درآمد` | Retain; `لاؤ` challenger | `لاؤ` is shorter but vague about import/module behavior. |
| `from` | `سے` | Retain | Keep Python order: `سے math درآمد sqrt`. |
| `as` | `بطور` | Retain over `نام` | Works for import aliases, exception bindings and context managers. |
| `try` | `کوشش` | Retain | Explain exception handling, not automatic repeated attempts. |
| `except` | `سوائے` | Retain; `پکڑو` challenger | `پکڑو` suggests catching but changes the guide's family; exact exception rules matter. |
| `finally` | `آخرکار` | Retain; `ہر_حال` challenger | Cleanup prose should say when it executes; this is not a guarantee against process termination. |
| `raise` | `اٹھاؤ` | Retain over `خطا_دو` | Can re-raise; an exception is not always an accidental fault. |
| `with` | `ساتھ` | Retain | Means a context manager, not generic object association. |
| `assert` | `تصدیق` | Retain provisionally; `یقین` challenger | Assertions may be disabled; never teach this as input/security validation. |
| `del` | `حذف` | Retain provisionally | Deletes a binding/item/attribute; does not mean remove a disk file. |
| `global` | `عالمی` | Retain provisionally | Refers to the current module, not every module/process. |
| `nonlocal` | `غیر_مقامی` | Retain provisionally | Rebinds a name in an enclosing function; not a network/remote variable. |
| `lambda` | `لامبڈا` | Retain as deferred candidate; compare `مختصر_فنکشن` | Short function expression, not an extra statement grammar. |
| `yield` | `پیدا_کرو` | Retain as deferred candidate; NAME-005 | Makes a generator; suspension is central to the explanation. |
| `async` | `غیر_متزامن` | Retain as deferred candidate; NAME-006 | Formal/long; neither parallel execution nor a new thread is promised. |
| `await` | `انتظار` | Retain as deferred candidate | Explain suspension on an awaitable, not `sleep` or blocking all work. |
| `match` | `منتخب` | Future only; `ملاؤ` challenger | Structural matching is broader than a menu selection; requires contextual parsing. |
| `case` | `صورت` | Future only; `حالت` challenger | Preserve ordinary uses as names outside a matching clause. |
| `type` statement | No selected word | Future only; `نوع` proposal | Do not conflate an alias declaration with builtin `قسم` / `type()`. |
| `except*` | `سوائے*` | Future contextual construct | `*` stays punctuation; this is not an additional plain keyword. |

## Audit of the built-in aliases

These are proposed bindings to genuine built-ins; they are ordinary names. A
proposed alias neither translates library methods nor adds new runtime semantics.

| Python | Guide alias | Keep / candidate | Clarification to teach |
|---|---|---|---|
| `print` | `دکھاؤ` | Keep; compare `چھاپو`, `لکھو` | Writes output; does not display a GUI or return the printed text. |
| `input` | `ان_پٹ` | Keep provisionally; compare `پوچھو` (NAME-001) | Reads a line and returns a string. |
| `range` | `حد` | Keep; compare `سلسلہ` | Upper bound excluded; a range is not a list. |
| `len` | `لمبائی` | Keep; compare `تعداد` | Number of elements; string length is not necessarily visible glyph count. |
| `list` | `فہرست` | Keep | Mutable sequence type/constructor. |
| `dict` | `لغت` | Keep | Key/value mapping, not only a language dictionary. |
| `set` | `مجموعہ` | Keep | Unique elements; distinguish from a list. |
| `int` | `صحیح_عدد` | Keep | Integer type/conversion; conversion can fail. |
| `float` | `اعشاری` | Keep; compare `اعشاری_عدد` | Binary floating point; does not promise exact decimal arithmetic. |
| `str` | `متن` | Keep | String type/conversion; encoding is a separate operation. |
| `sorted` | `ترتیب` | Keep; compare `مرتب` | Produces a new list; `.sort()` remains the Python method. |
| `enumerate` | `گنو` | Keep | Provides index/item pairs, not only a count. |
| `sum` | `جوڑ` | Keep | Aggregation; normal `+` keeps its own syntax. |
| `type` | `قسم` | Keep | Builtin behavior; no new Urdu soft-keyword declaration. |
| `open` | `کھولو` | Keep | Opens a resource using Python's behavior; teach `ساتھ` for cleanup. |

## NAME-001 — Reading input

- **Current proposed spelling / Python:** `ان_پٹ` / `input`; ordinary built-in alias.
- **Challengers:** `پوچھو` (ask), `پڑھو` (read), `لو` (take).
- **Plain Urdu:** `صارف سے ایک سطر پڑھو؛ نتیجہ متن ہوتا ہے۔`
- **Recommendation:** Keep `ان_پٹ` for the experiment. Test `پوچھو` first as
  the friendly challenger: a question-and-answer tutorial reads well with it.
- **Tradeoff:** `پوچھو` can imply a mandatory question or GUI; `input()` also
  accepts no prompt and reads redirected standard input. `پڑھو` is broad enough
  to be confused with file reads; `لو` is too broad and easily collides.
- **Typing:** `ان_پٹ` uses an underscore; `پوچھو` does not. Both use normal
  Urdu characters. Compare actual typing/correction effort, not visual length alone.
- **Simple / advanced comparison:** `نام = ان_پٹ("نام: ")` and
  `نام = پوچھو("نام: ")`; `عدد = int(input())` remains a mixed-language bridge.
- **Collision/migration:** Aliases may already be user variables. An accepted
  `پوچھو` alias must be added through an explicit version/compatibility policy;
  never replace every source occurrence of `ان_پٹ`.
- **Evidence / status:** No reader feedback. **PROPOSED; no active new alias.**
- **Tests needed:** Prompt output, newline stripping, string result, EOFError,
  shadowing, `obj.پوچھو` preservation and piped-input behavior.

## NAME-002 — A deliberate empty statement

- **Current / Python / context:** `گزر` / `pass` / syntax keyword.
- **Challengers:** `کچھ_نہ_کرو`, `خالی_چھوڑو`, `چھوڑو`.
- **Plain Urdu:** `یہاں کوئی کام نہیں کرنا؛ صرف بلاک کی جگہ پوری کرنی ہے۔`
- **Recommendation:** Keep `گزر` provisionally. `کچھ_نہ_کرو` is the clearest
  explanatory challenger; it is long but accurately names doing nothing.
- **Risk:** `گزر` or `چھوڑو` may be read as `continue`/skip. `خالی_چھوڑو`
  may imply the following body is absent. Teach a placeholder class and contrast
  it with `جاری` inside a loop.
- **Typing / examples:** Underscores make multiword proposals a single token.
  Compare `کلاس عارضی: گزر` with `کلاس عارضی: کچھ_نہ_کرو`; for an advanced
  case, an intentionally empty exception handler still swallows the exception.
- **Collision/migration:** This is a reserved-word change, not a harmless
  function alias. Any accepted replacement needs parsed-code migration,
  versioned compatibility and a negative test for keyword-shaped identifiers.
- **Evidence / status:** No reader feedback. **PROPOSED; keep legacy spelling.**
- **Tests needed:** Placeholder body, execution reaching the next statement,
  and a pass/continue/break comparison proving distinct behavior.

## NAME-003 — Identity deserves its own lesson

- **Current / Python / context:** `ہے` / `is` / comparison keyword.
- **Challengers:** `وہی`, `وہی_شے`, `عین_وہی`, `ایک_ہی`, `عین`;
  English `is` remains usable.
- **Plain Urdu:** `کیا دونوں نام اسی ایک شے کی طرف اشارہ کرتے ہیں؟`
- **Recommendation:** Keep `ہے` provisionally; test `وہی_شے` as a deliberately
  explicit challenger. No candidate yet has evidence sufficient for adoption.
- **Risk:** `ہے` resembles ordinary equality in prose; `ایک_ہی` can also mean
  equal values. `عین` is short but literary; `عین_وہی` emphasizes exactly the
  same object but remains formal. `وہی` is shorter and its object meaning may
  depend on context. `وہی_شے` may read awkwardly as an infix operator.
  `یکساں_شے` is discouraged because “similar/equal object” still suggests
  equality. Do not translate identity as `برابر`.
- **Simple / advanced comparison:** `الف = []; ب = []; ج = الف`;
  `الف == ب` is true, `الف ہے ب` is false, `الف ہے ج` is true. Prefer
  `نتیجہ ہے کچھ_نہیں` for a sentinel check; do not teach identity for numeric
  or string value comparison.
- **Typing / collision:** `ہے` is short and very common, so reserving it has a
  real identifier cost. Longer candidates add underscores. Preserve
  `obj.ہے`, imported export names and `call(ہے=value)` where supported.
- **Migration:** A changed infix token needs grammar-aware migration; strings
  describing “ہے” must remain intact. Keep explicit compatibility mode bounded.
- **Evidence / status:** No reader feedback. **PROPOSED; legacy retained.**
- **Tests needed:** Equal distinct lists, alias of one list, None sentinel,
  `ہے نہیں`, and colliding API name preservation.

## NAME-004 — Absence is not an empty container

- **Current / Python / context:** `کچھ_نہیں` / `None` / keyword constant.
- **Challengers:** `کوئی_نہیں`, `عدم`, `خالی`.
- **Plain Urdu:** `ابھی کوئی قدر مہیا نہیں کی گئی۔ خالی فہرست بھی ایک الگ قدر ہے۔`
- **Recommendation:** Keep `کچھ_نہیں` provisionally; compare `کوئی_نہیں`.
  Exclude `خالی` from preferred candidates because it encourages conflation
  with `[]`, `""` and `{}`. `عدم` is concise but formal.
- **Risk / examples:** Both long everyday phrases need an underscore. Compare
  `جواب = کچھ_نہیں` / `جواب = کوئی_نہیں`, then contrast with `جواب = []`.
  An advanced exercise distinguishes missing optional input, empty supplied
  input and `جھوٹ`.
- **Collision/migration:** Constants are syntax; preserve exactly one chosen
  spelling per language version and never rewrite data strings. A new alias
  cannot quietly become a different kind of object or special sentinel.
- **Evidence / status:** No reader feedback. **PROPOSED; legacy retained.**
- **Tests needed:** `is None` identity, implicit/bare function return, default
  sentinel, and value distinctions from False, zero and empty containers.

## NAME-005 — Producing one value and suspending

- **Current candidate / Python / context:** `پیدا_کرو` / `yield` / advanced
  syntax, deferred from the Phase 1 Urdu translator.
- **Challengers:** `دیتے_جاؤ`, `اگلا_دو`, `تھماؤ`.
- **Plain Urdu:** `ایک قدر دو اور یہیں رکو؛ اگلی فرمائش پر یہیں سے آگے چلو۔`
- **Recommendation:** Keep the guide candidate in the research registry. Test
  `دیتے_جاؤ` against it, with English `yield` shown for Python transfer.
- **Risk:** `پیدا_کرو` describes creation but not suspension; a yielded object
  may already exist. `دیتے_جاؤ` suggests repetition even for one yield.
  `اگلا_دو` sounds like requesting the next value; `تھماؤ` is ambiguous.
- **Simple / advanced shape (design only):** `پیدا_کرو عدد` / `yield number`;
  `پیدا_کرو سے اعداد` / `yield from numbers`. Explain delegation, `send`,
  generator return values and async-generator restrictions before promising them.
- **Typing/collision/migration:** All ordinary letters; multiword forms use `_`.
  A new reserved token affects identifiers. Acceptance needs generators,
  delegation and expression-context tests, not only one loop demo.
- **Evidence / status:** No reader feedback. **PROPOSED; not active Urdu syntax.**

## NAME-006 — Async without a false parallelism promise

- **Current candidate / Python / context:** `غیر_متزامن` / `async`; paired
  candidate `انتظار` / `await`; advanced syntax, deferred.
- **Challengers:** `ایسنک`, `غیر_ہم_وقت`, `بے_انتظار`; compare `ہم_وقت`
  explicitly as a misleading option rather than a preferred replacement.
- **Plain Urdu:** `یہ فنکشن معطل ہو کر دوسرے کام کو چلنے کا موقع دے سکتا ہے۔`
- **Recommendation:** Keep the guide candidate in research. Compare formal
  `غیر_متزامن` with the shorter technical borrowing `ایسنک`; pronunciation
  and spelling of the borrowing need reader feedback.
- **Risk:** `غیر_ہم_وقت` remains long and may overemphasize clock timing.
  `بے_انتظار` contradicts the usefulness of `await`. `ہم_وقت` suggests
  simultaneity; `async` alone guarantees neither a thread nor parallel work.
- **Shape (design only):** `غیر_متزامن فنکشن حاصل_کرو(): ...` versus
  `ایسنک فنکشن حاصل_کرو(): ...`; `واپس انتظار عمل()` versus
  `return await operation()`. Event-loop/library APIs keep their actual names.
- **Typing/collision/migration:** Compare underscore/formal spelling against the
  loanword, including how readers search for Python documentation. Activation
  requires async def/for/with, await placement and coroutine identity tests.
- **Evidence / status:** No reader feedback. **PROPOSED; neither challenger active.**

## Names for programs people write

Use a concrete noun for a value (`قیمت`, `تصویر`, `نتیجہ`) and a recognizable
action for a function (`اوسط_نکالو`, `فائل_پڑھو`, `سلام_دو`). Predicate names
can describe a property (`درست`, `موجود`) without borrowing reserved `ہے`.
Use readable noun phrases for classes (`طالب_علم`, `تصویر_پروسیسر`). This is
style guidance, not automatic inflection or a naming restriction.

Keep English package and protocol names: `math.sqrt`, `torch.nn.Module`,
`__init__`, `__iter__`, `forward`, `state_dict`. Retain `self` and `cls` in
teaching examples because Python readers recognize them; they are ordinary
parameters, not keywords, and an Urdu parameter name remains possible.

Avoid naming a local module `typing`, `math`, `torch` or `urdupy` when it would
shadow the package you intend to import. Prefer ASCII sample filenames during
Phase 1; Urdu filename portability is a separate cross-platform test task.

## Reader feedback worksheet — not yet conducted

Use the five numbered comparison exercises in
[`language-design.md`](language-design.md#five-comparison-exercises).
Show the Urdu snippet first without the glossary, then the Python comparison.
Aim to include multiple Urdu-reading developers and at least two beginners;
this is a recruitment plan, not a completed survey.

| Participant/session field | Record |
|---|---|
| Anonymous ID; date; consent to retain notes | ___ |
| Spoken/written Urdu familiarity; Python experience | ___ |
| Keyboard/layout; editor; OS; code direction setting | ___ |
| Snippet order and whether glossary was initially hidden | ___ |

| Exercise / tested word | Predicted behavior before glossary | Actual explanation after comparison | Typed accurately? Corrections? | Preferred candidate and reason |
|---|---|---|---|---|
| 1. Condition: `اگر`, `ہے`, `کچھ_نہیں` | ___ | ___ | ___ | ___ |
| 2. Loop: `ہر`, `میں`, `جب_تک`, `گزر` vs `جاری` | ___ | ___ | ___ | ___ |
| 3. Function: `فنکشن`, `واپس`, `دکھاؤ` | ___ | ___ | ___ | ___ |
| 4. Import and input: `سے`, `درآمد`, `ان_پٹ` / `پوچھو` | ___ | ___ | ___ | ___ |
| 5. AI/generator/async concept transfer | ___ | ___ | ___ | ___ |

Ask what each line does before asking which word “sounds better.” Record
misreadings of identity, None, loop control, return/output and suspension. Ask the
reader to type one unfamiliar spelling and edit a mixed Urdu/English call.
Do not convert these small convenience sessions into percentage claims about
all Urdu speakers.

Acceptance requires a dated record, concrete misunderstandings addressed,
maintainer decision, updated glossary, collision/negative tests, and a migration
note for a changed public spelling. Until then the worksheet stays blank and
the alternatives stay proposals.
