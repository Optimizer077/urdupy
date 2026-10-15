# UrduPy — Agent Engineering Handbook, Language Charter, and Project Tracker

> **Repository file:** `AGENTS.md`  
> **Project:** UrduPy — Urdu-first Python language frontend  
> **Primary deliverable:** A reliable, installable, documented `.urdu` language running on CPython  
> **Working principle:** *Easy Urdu grammar; real Python power; no silent breakage.*  
> **Document status:** Retained charter plus verified local implementation tracker; external publication/hosted/community gates remain open.  
> **Last charter revision:** 2026-10-14  
> **Intended readers:** Codex, Cursor, Claude Code, coding agents, reviewers, maintainers, and contributors.

> **Local Phase 1 scope (2026-10-15):** This is a new folder; the separate historical
> prototype was not supplied. Phase 1 maps to M0, research/design plus a bounded
> experimental compiler lab. Read `docs/phase-1.md` and `docs/roadmap.md` with this
> handbook. The maintainer explicitly authorizes creative naming/grammar design
> and multiple agents. Controversial spellings remain provisional; candidate
> comparisons do not establish human acceptance. Only the integrator edits shared
> tracker tables; other agents report evidence through their assigned documents.
> No Git repository exists here: owned file scopes replace branch/worktree merge
> coordination for this phase. Installation metadata is deferred pending the
> version policy; there is no public CLI, production importer or release claim.

> **Superseding continuation (2026-10-15):** The maintainer now explicitly requests
> **all remaining phases without stopping**. `docs/all-phases.md` records current
> production scope, ownership, baseline and gate decisions. The M0 statements above
> and its handoff remain dated history. Production work proceeds in separate
> modules while preserving the 57-test M0 baseline. Routine decisions and justified
> deviations are delegated to the agents; no external publication or fabricated
> remote/community verification is implied.

---

## 0. Mandatory Instructions for Every Agent

> **URD-031 superseding scope (2026-10-15):** The maintainer explicitly requests
> an Urdu-only programming surface, including PyTorch, NumPy and dependencies.
> This supersedes the early non-goal against translated library APIs. Implement
> an opt-in `# اردوپائی: مکمل` source mode with native backend objects, an Urdu
> library vocabulary and a reversible Urdu spelling for arbitrary API identifiers.
> Keep ordinary/mixed source behavior compatible. ADR-015 records this additive
> interface; no public upload is implied. Baseline: 162 core tests and five example
> pairs PASS on CPython 3.13.13, clean Git worktree. Integrator owns compiler,
> runtime, shared tracking, ADR and integration. Catalog agent owns
> `urdupy/urdu_catalog.py`; examples agent owns `examples/مکمل_اردو/` and
> `tests/compatibility/compat_urdu_only.py`; CLI agent owns localized CLI changes
> and dedicated CLI tests. Core tests use no optional dependencies. Rollback:
> remove the opt-in mode and its additive catalog/CLI/examples, retaining old APIs.

**Read this entire file before making any code change.** Treat it as the project's operational contract and persistent task tracker. Do not treat an attractive demo as proof of correctness. Make incremental, testable changes, and leave enough information for the next agent to resume safely.

On each new session, **in order**:

1. Read `AGENTS.md`, `README.md`, `pyproject.toml`, the compiler, runtime, importer, CLI, existing tests, and the current worktree state.
2. Identify which commands actually work in this checkout. Detect Python versions and available dependencies instead of assuming them.
3. Run the existing baseline tests **before** editing code and record the result in the progress log below.
4. Select **one** unblocked task from the tracker; create a clear scope, files to touch, tests to add, and rollback plan.
5. Check whether another agent owns a conflicting task or file. If yes, coordinate rather than overwrite.
6. Implement the smallest complete, working change. Add or modify tests that verify it and protect existing behavior.
7. Run focused tests, the project test suite, and relevant integration tests. Record exact commands and results.
8. Update the task tracker, compatibility matrix, decision log, documentation, and handoff note when applicable.
9. At the end of the session, report completed work, verification, regressions or known failures, and the next safe step.

**Never**:

- Claim a task works because its code looks plausible; execute the relevant test.
- Rewrite working subsystems without a migration plan and regression coverage.
- Introduce a new language keyword or alias silently.
- Break ordinary Python imports, CPython semantics, native library interfaces, or Unicode identifiers in order to simplify a translator.
- Rename user-visible syntax, a CLI command, a module, or a public API without a compatibility plan.
- Delete or weaken tests to make CI pass.
- Mark tests `passed` if they were skipped, blocked by dependencies, or not run.
- Add large AI frameworks to the base package dependencies.
- Download model weights or depend on external services in routine tests.
- Publish to PyPI, push to a remote repository, create releases, or use release secrets without explicit maintainer authorization.
- Hide uncertainty. If verification is unavailable, document it as **UNVERIFIED**.

**Completion means code + tests + docs + tracking, not just code.**

### Instruction priority

1. Explicit maintainer instruction for the current task.
2. This `AGENTS.md` and accepted architecture decision records (ADRs).
3. Published, versioned language compatibility guarantees.
4. Repository tests and documented public APIs.
5. Existing implementation details.

If these disagree, **stop changing that disputed surface**, record the conflict, propose an ADR, and proceed with independent work. Avoid guessing on language-breaking decisions.

---

## 1. Product Vision and Success Definition

UrduPy is an **Urdu-first language frontend for CPython**. It lets developers write control flow, declarations, variables, functions, and classes in Urdu while using the existing Python runtime, standard library, pip ecosystem, and compiled native extensions.

A beginner should be able to write a small program in Urdu without learning English control-flow keywords. An advanced developer should be able to train PyTorch models, process video with OpenCV, use NumPy arrays, import Transformers, run a web API, and debug real Python exceptions **without learning a second runtime or using rewritten library forks**.

### Product pillars

| Pillar | Required behavior | Evidence |
|---|---|---|
| **Simple grammar** | Familiar Python layout, short Urdu keywords, little special punctuation | Beginner examples and usability exercises |
| **Real CPython** | Same Python objects, libraries, execution semantics | Direct translation/runtime comparison tests |
| **True interoperability** | `.urdu` ↔ `.py` modules with documented import rules | Cross-language import integration tests |
| **Scientific/AI ready** | NumPy, OpenCV, PyTorch, etc. usable unchanged | CPU tests and separate optional GPU/model tests |
| **Safe evolution** | No hidden language/API breakage between releases | Compatibility tests, ADRs, changelog, CI |
| **Open-source release quality** | pip package, wheels, docs, tested version matrix | Clean-environment packaging verification |
| **Urdu usability** | UTF-8, clear terms, original-line diagnostics, RTL guidance | Unicode and editor/terminal smoke tests |

### Explicit non-goals for early releases

- Reimplementing Python's parser/runtime/VM, garbage collector, native extension ABI, or standard library.
- Translating all NumPy, PyTorch, OpenCV, pandas, or Transformers methods and attribute names into Urdu.
- A natural-language conversational parser, arbitrary Urdu prose-as-code, or free word-order grammar.
- An independent package ecosystem.
- Promising a new Python release is supported before tests have run.
- Making UrduPy a sandbox for untrusted Python programs.
- Requiring `.urdu` programs to define or invoke a special `main()` function.

---

## 2. Known Starting Point — Verify, Do Not Assume

An earlier **prototype** exists in the supplied UrduPy v0.1 material. The following is a verified local **historical snapshot**, not a release or forward-compatibility guarantee:

- **Snapshot verified:** 2026-10-14.
- **Local interpreter:** Python `3.13.5`.
- **Test invocation:** `python -m unittest discover -s tests -v`.
- **Observed result:** 7 tests passed.
- **Prototype project distribution name:** `urdupy-demo` in `pyproject.toml`, **not an established PyPI claim to `urdupy`**.
- **Package import name:** `urdupy`.
- **Current source components:** `urdupy/language.py`, `runtime.py`, `importer.py`, `cli.py`; example `.urdu` files and `unittest` tests.
- **Current demonstrable areas:** token-level Urdu keyword conversion; Python import pass-through; `.urdu` imports; built-in aliases; line preservation for simple error cases.
- **Not yet established:** latest Python version support, robust context-sensitive translation, full f-string/soft-keyword handling, AI framework compatibility, publishing, release CI, language stability, editor tooling, or broad source-position fidelity.

**Agents must run a fresh baseline in the actual current checkout.** If this repository is new, use this information only as a migration reference. Do not fabricate historical test results for missing files.

### Current prototype commands, if the same layout is present

```bash
python --version
python -m unittest discover -s tests -v
python -m urdupy run examples/demo.urdu
python -m urdupy translate examples/demo.urdu
python -m pip install -e .
```

If these commands do not exist yet, create working equivalents in a focused task. Record the actual result instead of claiming them available.

### Baseline hazards to investigate early

- Translating **every matching `NAME` token** can incorrectly rewrite legitimate identifiers in some syntactic contexts; `obj.اگر` being protected is not enough.
- Python soft keywords (`match`, `case`, `type`) require careful context treatment.
- Built-in aliases injected into module globals are not semantically identical to aliases resolved through a module's built-ins namespace; investigate name shadowing and export behavior.
- A keyword-replaced intermediate `.py` file may still depend on UrduPy-provided built-in aliases; do not describe it as standalone unless verified.
- Equal line counts alone do not guarantee accurate syntax-error column offsets or multi-line source mapping.
- `sys.meta_path`, `sys.path`, `sys.argv`, `linecache`, import cache, and module namespaces are shared interpreter state: changes need isolation and restoration tests.

---

## 3. Canonical Language Philosophy: **Simple Urdu Grammar**

This is a primary product requirement, **not** optional polishing.

### 3.1 Keep one predictable grammar

UrduPy v1 uses **Python's grammatical structure with Urdu lexical keywords**. Do not invent a second grammar for the same concept merely because a more conversational Urdu phrase sounds natural.

Examples of the **intended** shape:

```python
# Urdu statement form follows Python structure.
اگر عمر >= 18:
    دکھاؤ("بالغ")
ورنہ:
    دکھاؤ("کم عمر")

ہر عدد میں حد(1, 6):
    دکھاؤ(عدد)

فنکشن مربع(عدد):
    واپس عدد * عدد

کلاس طالب_علم:
    فنکشن __init__(self, نام):
        self.نام = نام
```

**Keep:** indentation, `:`, `()`, `[]`, `{}`, operators, normal Python calls, indexing, comprehensions, type annotations, decorators, and import semantics.

**Do not require:** extra filler such as `تو`, `کرو`, `ختم`, `ہو`, natural-language sentence endings, or English translated API paths to express ordinary Python statements. Some fillers might feel conversational but increase parser complexity and make copy-pasting Python examples harder.

**Avoid:** a different word order for loops, functions, classes, or imports. For example, prefer `ہر x میں items:` because it mirrors Python's `for x in items:` and is familiar across examples. Do not make an alternative `items میں ہر x` grammar during the compatibility phase.

### 3.2 Ease-of-use rules: naming and grammar

Every language-level keyword proposal must pass these checks:

1. **Meaning:** Is the word understandable in commonly used Urdu, not just formal literary Urdu?
2. **Brevity:** Prefer a short word where the meaning remains clear. Multiword terms are acceptable only for genuinely complex concepts.
3. **Consistency:** One concept should normally have **one canonical spelling**. Too many synonyms make tutorials, documentation, autocomplete, and error messages harder.
4. **Pronounceability:** A learner should be able to say the keyword aloud without explanation.
5. **Typeability:** Avoid invisible characters, unusual punctuation, difficult ligature/diacritic variants, or copy-and-paste-only spellings.
6. **Readability:** It should look reasonable beside numerals, operators, English package names, and class names.
7. **Unambiguity:** Do not overload ordinary words unpredictably or confuse `None` with empty containers, `False` with zero, or concurrency with multiprocessing.
8. **Compatibility:** Existing working `.urdu` programs must not suddenly change meaning due to a spelling revision.
9. **Orthography:** Use one preferred spelling; document common spelling mistakes with friendly diagnostics if practical.
10. **Python bridge:** A learner should see a one-to-one mapping to Python when comparing tutorials.

If the right Urdu word is uncertain, create a **Language Naming Proposal** (template in §18), compare candidates, collect native-speaker feedback, and retain a **provisional** status until accepted. Do not change the default spelling based on one agent's preference.

### 3.3 Named design constraints

- **Canonical keywords:** exactly one documented preferred spelling per Python construct after acceptance.
- **English keywords:** ordinary Python source remains valid wherever feasible. Mixed Urdu/English is allowed.
- **Urdu identifiers:** regular Unicode identifiers work as defined by CPython; they are not automatically transliterated.
- **Python package names:** `torch`, `numpy`, `cv2`, `transformers`, `math`, etc. are imported unchanged.
- **Python protocol names:** `__init__`, `__iter__`, `forward`, `state_dict`, `backward`, `parameters`, etc. remain untouched.
- **Urdu built-in aliases:** convenience names, not language syntax; they must respect reasonable shadowing behavior.
- **No automatic Urdu grammatical inflection:** no singular/plural agreement, verb conjugation, honorific grammar, gender inflection, or natural-language sentence parsing in v1.
- **Punctuation:** use ordinary Python punctuation; ASCII digits (`0-9`) are guaranteed in v1.

### 3.4 Why familiarity beats perfect literal translation

For learners, `کلاس` can be more usable than a formal Urdu alternative for `class`, and `فنکشن` may be clearer than an obscure literal translation of `function`. Optimize for comprehension and educational familiarity, not ideology about loanwords. Public documentation can explain the meaning in natural Urdu.

### 3.5 Orthography and keyboard input

- Source encoding: **UTF-8**; accept UTF-8 BOM where explicitly tested/documented.
- Canonical keywords use conventional Urdu letters, without obligatory diacritics.
- Treat Arabic `ي/ك` and Urdu/Persian `ی/ک` differences seriously; do not globally rewrite a user's strings or names to "correct" spelling.
- Handle Python's NFKC identifier rules and warn about confusing normalized names if feasible.
- Do not silently strip zero-width, bidirectional, or format characters from code; surface useful warnings for suspicious cases.
- Avoid Unicode bidirectional control characters in examples and generated code.
- Keep source formatting stable; preservation of comments and strings is mandatory.
- Keep a simple tutorial explaining keyboard layout, mixed RTL/LTR presentation, and code-block rendering.

---

## 4. Canonical Urdu Name Registry — **Review Before Changing**

**Important:** This is the **initial proposed/legacy-compatible registry**, not proof that every entry is fully implemented. It gives agents a consistent vocabulary to research, test, and stabilize. `Status` is `CORE` for intended fundamental syntax, `REVIEW` for wording/semantics requiring extra evaluation, and `FUTURE` for context-sensitive syntax that needs extra engineering. Do not publish as stable until tests and maintainer review exist.

### 4.1 Statements, control flow, Boolean values

| Python | Preferred Urdu spelling | Status | Ease/grammar guidance |
|---|---|---|---|
| `if` | `اگر` | CORE | Short, common, immediately understandable. |
| `elif` | `ورنہ_اگر` | CORE | Underscore joins a Python-identifier-shaped keyword. |
| `else` | `ورنہ` | CORE | Same family as `ورنہ_اگر`. |
| `for` | `ہر` | CORE | Read together with `میں` (`for ... in`). |
| `in` | `میں` | CORE | Keep operator/list membership semantics. |
| `while` | `جب_تک` | CORE | Easy phrase but includes underscore. |
| `and` | `اور` | CORE | Everyday conjunction. |
| `or` | `یا` | CORE | Everyday disjunction. |
| `not` | `نہیں` | CORE | One negation word across conditions. |
| `True` | `سچ` | CORE | Boolean true, not a general truth checker. |
| `False` | `جھوٹ` | CORE | Boolean false, not the same as numeric zero. |
| `None` | `کچھ_نہیں` | REVIEW | Do not use `خالی` if it makes learners think `None == []`. |
| `break` | `روکو` | CORE | Stops a loop, not the whole program. |
| `continue` | `جاری` | CORE | Continues to the next loop iteration. |
| `pass` | `گزر` | REVIEW | Consider whether `گزر` is clear to beginners; keep legacy code working. |
| `is` | `ہے` | REVIEW | Python identity comparison, **not** ordinary equality; high risk of learner confusion. |

### 4.2 Declarations, modules, exceptions

| Python | Preferred Urdu spelling | Status | Guidance |
|---|---|---|---|
| `def` | `فنکشن` | CORE | Familiar technical borrowing; preserve `def` alternative. |
| `return` | `واپس` | CORE | Returns a value; not `print`. |
| `class` | `کلاس` | CORE | Technical loanword is practical. |
| `import` | `درآمد` | CORE | Standard import counterpart. |
| `from` | `سے` | CORE | Use in `سے math درآمد sqrt`. |
| `as` | `بطور` | CORE | Alias in imports and exception bindings. |
| `try` | `کوشش` | CORE | Easy reading. |
| `except` | `سوائے` | CORE | Preserve exception syntax and `except*` behavior. |
| `finally` | `آخرکار` | CORE | Mandatory cleanup block. |
| `raise` | `اٹھاؤ` | CORE | Raises an exception; document with examples. |
| `with` | `ساتھ` | CORE | Context management; retain `as`. |
| `assert` | `تصدیق` | REVIEW | Avoid confusing an assertion with general validation. |
| `del` | `حذف` | REVIEW | Do not present as general safe file deletion. |
| `global` | `عالمی` | REVIEW | Explain Python scoping precisely. |
| `nonlocal` | `غیر_مقامی` | REVIEW | Advanced scope feature; accuracy matters more than brevity. |

### 4.3 Advanced syntax — explicit research gate

| Python | Candidate Urdu | Status | Risk / design requirement |
|---|---|---|---|
| `lambda` | `لامبڈا` | REVIEW | Borrowed word; compare with any genuinely easier alternative. |
| `yield` | `پیدا_کرو` | REVIEW | Avoid implying that returning and yielding are identical. |
| `async` | `غیر_متزامن` | REVIEW | Long and formal; test shorter clear candidates with Urdu-speaking developers. |
| `await` | `انتظار` | REVIEW | Must correctly communicate awaiting an awaitable. |
| `match` | `منتخب` | FUTURE | Soft keyword; translate **only** in match-statement context. |
| `case` | `صورت` | FUTURE | Soft keyword; must not break identifiers/attributes. |
| `type` statement | TBD, via ADR | FUTURE | `type` can be a normal name elsewhere; research Python version-specific grammar. |
| `except*` | `سوائے*` candidate | FUTURE | `*` is punctuation; verify exact Python grammar and diagnostic mapping. |

Python's wildcard `_`, ordinary `@` decorators, slash/star parameter markers, f-string formatting, and operators should remain standard Python syntax until a separately accepted ADR states otherwise.

**Soft keyword warning:** Python changes have introduced syntax whose keywords are contextual, not universally reserved. An UrduPy translator must not simply treat `منتخب`/`صورت` as unconditional `NAME` replacements.

### 4.4 Urdu built-in aliases (separate from parser keywords)

These should resolve to **the real CPython built-ins** when used in `.urdu` code. Do not convert matching identifiers by blind source replacement, and do not alter same-named attributes such as `obj.دکھاؤ`.

| Python built-in | Proposed canonical Urdu alias | Priority | Notes |
|---|---|---|---|
| `print` | `دکھاؤ` | P0 | Keep legacy spelling stable. Terminal output, not a UI widget. |
| `input` | `ان_پٹ` | P0 | Existing prototype spelling; evaluate `پوچھو` as a possible **future** friendly alternative via ADR only. |
| `range` | `حد` | P0 | Explain exclusive upper bound. |
| `len` | `لمبائی` | P0 | Number of elements/characters, not a physical length unit. |
| `list` | `فہرست` | P1 | Create/convert to list. |
| `dict` | `لغت` | P1 | Mapping/dictionary type. |
| `set` | `مجموعہ` | P1 | Set, not an arbitrary collection of all kinds. |
| `int` | `صحیح_عدد` | P1 | Preserve conversion exceptions. |
| `float` | `اعشاری` | P1 | Preserve floating-point behavior. |
| `str` | `متن` | P1 | Text representation, not an encoding promise. |
| `sorted` | `ترتیب` | P1 | Returns sorted sequence; distinguish from in-place `.sort()`. |
| `enumerate` | `گنو` | P1 | Produces `(index, item)` pairs. |
| `sum` | `جوڑ` | P1 | Numeric aggregation, not generic string concatenation. |
| `type` | `قسم` | P1 | Type inspection and type construction behavior. |
| `open` | `کھولو` | P1 | File/resource opening. |

Candidates for future discussion, **not automatically accepted**: `پوچھو` for `input`, `چھاپو` for `print`, shorter names for `async`/`await`, and aliases for common exceptions. Avoid synonym explosions. `دکھاؤ`, `حد`, and legacy aliases must continue working through any transition.

### 4.5 Naming patterns for user code, libraries, and packages

| Surface | Convention | Example |
|---|---|---|
| Urdu local variable | Short descriptive Urdu identifier | `تصویر`, `عدد`, `نتیجہ` |
| Urdu function | Clear action or noun phrase; underscores for multiword words | `اوسط_نکالو` |
| Urdu class | Readable Urdu noun, no forced transliteration | `تصویر_پروسیسر` |
| Python third-party package | **Keep original import name** | `numpy`, `torch`, `cv2` |
| Python library attribute or protocol | **Keep original name** | `torch.nn.Module`, `.forward`, `.to` |
| Urdu module filename | ASCII recommended initially for easy tooling, Urdu filenames permitted only with verified support | `calculator.urdu`; later `حساب.urdu` |
| Canonical command | `urdupy` | `urdupy run app.urdu` |
| Python distribution name | Verify PyPI availability; **never assume** | `urdupy` if available; otherwise distinct name |
| Python import package | `urdupy` subject to verified conflicts | `from urdupy import translate` |
| Source extension | `.urdu` | `model.urdu` |

Do **not** name a new package `numpy`, `torch`, `cv2`, `typing`, `asyncio`, etc. Do not create wrapper modules that shadow these imports.

### 4.6 Examples that teach the grammar correctly

**Beginner-friendly:**

```python
# A variable may be Urdu; the expression is normal Python.
عمر = 20
اگر عمر >= 18:
    دکھاؤ("آپ بالغ ہیں")
ورنہ:
    دکھاؤ("آپ کم عمر ہیں")

فنکشن جمع(الف, ب):
    واپس الف + ب

دکھاؤ(جمع(3, 4))
```

**For loops and list comprehensions:**

```python
ہر عدد میں حد(1, 5):
    دکھاؤ(عدد)

مربع = [عدد * عدد ہر عدد میں حد(1, 5)]
```

**Advanced AI — target behavior, not yet a compatibility claim:**

```python
درآمد torch

کلاس چھوٹا_ماڈل(torch.nn.Module):
    فنکشن __init__(self):
        super().__init__()
        self.layer = torch.nn.Linear(4, 2)

    فنکشن forward(self, x):
        واپس self.layer(x)

ماڈل = چھوٹا_ماڈل()
دکھاؤ(ماڈل(torch.randn(2, 4)).shape)
```

`forward` and `__init__` must remain their real Python/PyTorch protocol spellings. The same object must be a genuine subclass of `torch.nn.Module`, not a proxy to a separate interpreter model.

### 4.7 Readability acceptance exercise

Before accepting any new keyword family or changing an existing spelling:

- Prepare **five** small snippets (condition, loop, function, import, AI call) in UrduPy and equivalent Python.
- Ask multiple Urdu-reading developers (ideally including at least two beginners) what each line does, without showing the keyword glossary first.
- Record misunderstandings, typing friction, and preferred terms; do not present an informal survey as rigorous scientific evidence.
- Choose the form that is easy to understand **and** technically stable, not simply the most literary.
- Add a keyword glossary entry, at least one negative test, and a migration note if altering existing syntax.

Desired usability outcomes (targets, not claims): beginners can recognize the purpose of everyday control flow after a one-page cheat sheet; advanced developers can transfer Python concepts with minimal syntax differences; a single source statement should not have several competing canonical spellings.

---

## 5. Public Compatibility Contract

### 5.1 What "Python-compatible" must mean

UrduPy source can use normal Python expressions and imports, and translated code is compiled and executed by a supported CPython interpreter. Python objects, third-party libraries, standard exceptions, and native extension modules are not reimplemented.

Distinguish four contracts:

1. **Execution compatibility:** same ordinary CPython execution semantics after correct translation.
2. **Source compatibility:** explicitly documented Urdu syntax and supported English Python syntax.
3. **Import compatibility:** clearly defined `.py` and `.urdu` resolution, package, and caching behavior.
4. **Tooling compatibility:** debugger, type checker, IDE, stack trace, formatter, and source mapping behavior (may be partial initially).

Never collapse these into an unsupported statement that "100% of Python is supported."

### 5.2 Version policy

- Research the **latest stable CPython** from official sources at the time of each release. Do not set a hard-coded "latest" version based on this file's date.
- Select the latest stable version and a realistic earlier-version range based on actual CI and required third-party package support.
- Each supported Python minor version must pass core translator/runtime/import tests in a clean environment.
- Track major AI-library versions separately; torch/vision/native wheels often have different platform/architecture constraints.
- Pre-release Python builds may be tested separately, but are not stable support unless explicitly advertised.
- No unsupported `requires-python` classifier, README badge, or compatibility claim.

### 5.3 Source modes and naming collisions

The compiler must precisely define these situations:

- Urdu syntax words in string literals, docstrings, f-string literal portions, comments, and raw strings.
- Attribute names like `object.اگر` and `object.واپس`.
- Named keyword arguments (e.g. a Python API that accepts a Unicode keyword matching an Urdu keyword).
- Named imports from Python libraries whose exports coincide with Urdu keywords.
- Keyword-shaped local identifiers or parameter names in mixed-language code.
- Dictionaries and subscript keys that happen to contain Urdu keyword strings.
- `match`/`case`/`type` soft-keyword contexts.
- Decorator expressions, comprehensions, generator expressions, assignment expressions, and pattern matching.
- F-string embedded Python expressions and format specifications across supported Python versions.

Choose documented, predictable rules rather than silently corrupting input. In v1, reserving Urdu words as syntax may be acceptable in grammar positions, but **attribute/property names and imported APIs must not be corrupted**. Provide escape hatches when justified by real compatibility examples, without making the common grammar complex.

### 5.4 Normal Python must remain normal

```python
import math
import numpy as np

x = np.array([1, 2, 3])
print(math.sqrt(9), x.sum())
```

This should remain valid in an UrduPy file on installations where `numpy` exists. No UrduPy-only wrapper should be needed, and no identifier translation should change `np.array`, `.sum`, etc.

---

## 6. Architecture: Thin Frontend, Real CPython

Preferred conceptual pipeline:

```text
app.urdu
    |
    v
UTF-8 reader + source metadata
    |
    v
Lexer/tokenizer + context-aware Urdu grammar transform
    |
    v
Valid CPython source + mapping of transformed spans
    |
    v
CPython compile(...)
    |
    v
Python code objects / ordinary importlib execution
    |
    +----> stdlib / NumPy / OpenCV / PyTorch / other pip packages
```

Components can be designed as:

- `language/keywords.py`: versioned registry, canonical spellings, status metadata.
- `compiler/tokenizer.py`: safe Unicode and token handling.
- `compiler/translator.py`: deterministic, context-aware transformation.
- `compiler/source_map.py`: original-to-translated location mapping.
- `runtime/executor.py`: run scripts with controlled module globals, path, and argv.
- `runtime/importer.py`: opt-in import hook for `.urdu` files and packages.
- `runtime/aliases.py`: per-module Urdu aliases to actual built-in Python callables/types.
- `diagnostics/errors.py`: original Urdu lines and useful explanations.
- `cli.py` / `__main__.py`: commands and user-facing errors.

This is a **suggested** internal structure, not a demand to move files before tests justify it. If an alternative design is better, write an ADR with a compatibility and migration plan.

### Translator architecture review

Before broad changes, evaluate:

1. `tokenize` with spans and context rules.
2. A CST/grammar-aware representation where necessary.
3. A small custom pre-parser for only the new syntax, if complexity demands it.
4. CPython AST techniques **after** valid Python syntax exists (AST alone cannot parse unknown Urdu keywords).

Decision criteria: feature coverage, Unicode correctness, f-string handling, public API stability, error positions, maintenance cost across Python versions, testability, and performance.

**Never use naive `str.replace` across source text.** Preserve string/comment content exactly. Source mapping should record line and column changes; do not claim exact column fidelity just because line counts are unchanged.

### Import behavior

- Keep standard Python importing untouched unless the Urdu loader is explicitly installed by the UrduPy runtime or application.
- Prefer Python's public `importlib` finder/loader APIs.
- Avoid global monkey-patching `__import__`.
- Preserve module identity, `__name__`, `__package__`, `__spec__`, `__file__`, and `__path__` as appropriate.
- Define and test `.py` versus `.urdu` name collision precedence; begin with standard Python's modules winning when documented.
- Test packages, nested modules, circular imports, relative imports, repeated imports, and module discovery behavior.
- Do not allow the Urdu finder to supersede unrelated native/zip modules unexpectedly.
- If a Python program must import a `.urdu` module, require explicitly installed loader initialization and document it.

### Built-in alias behavior

- Aliases refer to real Python objects, not implementation copies.
- Preserve sensible lexical name resolution: local assignments, function globals, built-ins, and imports have predictable behavior.
- Review whether Urdu aliases belong in a per-module built-ins namespace rather than injected user globals; add tests before altering existing behavior.
- A user-defined `دکھاؤ` should be able to behave as a normal user-defined symbol under clearly documented semantics.
- Aliases should not unexpectedly leak into `dir(module)` or `from module import *` unless that is an accepted documented design.
- Translated source should be labeled **intermediate** if it requires an UrduPy-provided alias namespace to execute.

### Source/exception quality

- Original `.urdu` filename and line number must survive runtime exceptions.
- Prefer showing original Urdu source rather than the translated English token in tracebacks.
- Map syntax error offsets to original lines where technically possible; otherwise explain offset uncertainty.
- Use `linecache` responsibly and avoid persistent incorrect global cache state across modified files.
- Avoid catching `BaseException` indiscriminately or suppressing `KeyboardInterrupt` / `SystemExit`.
- `urdupy check` must not execute the checked script or its imports.

---

## 7. Scientific Computing and Advanced AI Interoperability

AI programming is a **first-class acceptance goal**, not merely a future marketing example.

### 7.1 Library tiers

| Tier | Library / ecosystem | Required minimum validation | Dependency policy |
|---|---|---|---|
| A | `numpy` | Array creation, arithmetic, indexing, dtypes | Optional science test environment |
| A | `scipy` | Numeric operation, sparse/statistics example | Optional science test environment |
| A | `pandas` | DataFrame transformation, serialization where appropriate | Optional science test environment |
| A | `opencv-python` / `opencv-python-headless` | Synthetic image BGR→RGB/gray, array interoperability | Select **one** OpenCV provider per environment |
| A | `Pillow` | Image object conversion | Optional vision test environment |
| A | `torch` | `nn.Module`, autograd, optimizer, inference, saving | Optional AI test environment; CPU required where available |
| A | `torchvision` | Model construction and transforms, no model download in CI | Match compatible PyTorch version |
| B | `scikit-learn` | Tiny fit/predict pipeline | Optional ML test environment |
| B | `transformers` | Small configuration/model offline and import tests | Optional NLP/LLM environment |
| B | `datasets`, `accelerate`, `safetensors` | Small local fixtures and import checks | Optional AI environment |
| B | `onnxruntime` | Small model inference where supported | Optional deployment environment |
| C | `timm`, `torchaudio`, `ultralytics` | Targeted offline-compatible smoke/integration tests | Optional independent suites |
| C | JAX, TensorFlow/Keras, MediaPipe | Compatibility research and targeted tests | Not required for first public release |
| C | FastAPI, Gradio, Streamlit | App integration and non-interactive server tests | Optional application suites |

Each tier row becomes **Verified** only when tested in a recorded environment. A plan is not a passing test.

### 7.2 Golden end-to-end AI scenarios

These are release acceptance targets. Use deterministic, small fixtures and CPU unless noted.

**AI-001 — NumPy computation in Urdu:**

- `درآمد numpy بطور np` succeeds.
- An Urdu-defined function accepts/returns `np.ndarray`.
- Broadcasting, reshape, and dtype results match equivalent Python.

**AI-002 — OpenCV image in Urdu:**

- Create a tiny synthetic `numpy.uint8` array (no external image download).
- Use `cv2.cvtColor`, resize or blur, and verify image shape/pixel result.
- Prove `.urdu` and `.py` paths produce equivalent results.

**AI-003 — PyTorch training in Urdu:**

- Define a class in Urdu source subclassing real `torch.nn.Module`.
- Keep `__init__` and `forward` exact; create `nn.Linear` and call it.
- Seed RNG; do a tiny CPU forward pass, scalar loss, `.backward()`, and optimizer step.
- Verify gradients exist and weights change as expected.

**AI-004 — Combined NumPy/OpenCV/PyTorch:**

- Synthesize an OpenCV image, convert color space, transform to `torch.Tensor`.
- Verify memory/dtype/channel order expectations and model output shape.
- No external network, camera, GUI, or GPU required.

**AI-005 — Transformers, offline:**

- Where dependency versions permit, instantiate a very small model from a local configuration, with random weights.
- Do not call `from_pretrained` on a network resource in routine CI.
- Demonstrate Urdu control flow around the original Transformers API.

**AI-006 — Optional real pretrained inference:**

- Provide a documented example with explicit user-provided or explicitly downloaded model weights.
- Mark it an **opt-in integration demonstration** with network, license, memory, and accelerator notes.

### 7.3 GPU and acceleration policy

- UrduPy itself selects no GPU runtime; **PyTorch and each installed framework manage devices**.
- Use official compatible installation instructions for CPU/CUDA/ROCm/other supported backends.
- Do not bundle CUDA as an UrduPy core dependency.
- `torch.cuda.is_available()` checks are runtime capability checks, not proof all operations support the GPU.
- GPU suites are clearly marked and skipped with explanations when no supported device exists; never count them as passed.
- CPU compatibility is essential. GPU compatibility is an additional supported-environment matrix.

### 7.4 AI names remain the library's names

Correct:

```python
درآمد torch
ماڈل = torch.nn.Linear(4, 2)
نتیجہ = ماڈل(torch.randn(1, 4))
دکھاؤ(نتیجہ.shape)
```

Incorrect design: translating `torch.nn.Linear` into a novel Urdu class path that has to be maintained for every future version of PyTorch. Any educational wrapper should be opt-in, separately versioned, and not needed for interoperability.

### 7.5 Dependency installation

- Base install: a small package without PyTorch, NumPy, OpenCV, or model weights.
- Possible extras: `urdupy[science]`, `urdupy[vision]`, `urdupy[nlp]`, `urdupy[dev]`; final names and exact dependencies require an ADR and validation.
- Avoid packaging both `opencv-python` and `opencv-python-headless` in one environment by default: both supply `cv2`.
- For PyTorch, explicitly recommend the official version/platform/device-specific installation method when an extra cannot represent safe cross-platform choices.
- Keep integration test dependencies in separate lockfiles or constraints as appropriate.
- Compatibility does not mean every scientific wheel supports every CPython version or operating system. Record what was actually tested.

---

## 8. Command-Line and Packaging Contract

### Target CLI surface

```bash
urdupy --help
urdupy --version
urdupy run app.urdu
urdupy translate app.urdu
urdupy check app.urdu
urdupy repl
```

**Availability must be indicated accurately:** `run` and `translate` exist in the prototype; `check` and `repl` are future tasks until implemented and tested.

Recommended behavior:

- `run`: execute a `.urdu` script through CPython; propagate program arguments and appropriate exit status.
- `translate`: output or write the translated Python representation, with a warning if it depends on UrduPy aliases.
- `check`: translate and compile without executing source/imports; report errors with original positions.
- `repl`: interactive statement evaluation with multiline indentation and Unicode input support (later milestone).
- `--version`: report installed package and, optionally, interpreter version.

`python -m urdupy` should provide an equivalent entry surface. No mandatory user-defined `main()` function. The package may internally use an ordinary CLI entry function such as `cli()`.

### Packaging requirements

- Use a standards-compliant `pyproject.toml` and a maintained PEP 517 build backend.
- Prefer a `src/` layout only when making a clean tested migration; do not break existing imports to achieve cosmetics.
- Pin minimum supported Python version accurately and test it.
- Publish a wheel and sdist after validating both in clean environments.
- Include license, README, project URLs, changelog, security policy, contribution guide, classifiers, and version policy.
- Verify the desired PyPI distribution name independently. `urdupy-demo` in the prototype does not give ownership of `urdupy`.
- Use Trusted Publishing/OIDC where supported; do not store long-lived API tokens in source code.
- Public publishing always requires explicit maintainer approval.

### Release versions

- Use pre-1.0 minor versions for carefully documented evolving language features.
- Even before 1.0, treat documented canonical keyword changes as breaking unless there is a compatibility strategy.
- Track **language specification version** separately when needed; a package bugfix must not silently change program meaning.
- Include a changelog entry for changed parser behavior, alias namespace, import priority, error reporting, or Python support range.

---

## 9. Non-Breakage Protocol: Before, During, After Each Change

### 9.1 Before editing

Write down:

- **Task ID / owner / scope.**
- **Why the change is necessary** and what users could notice.
- **Observable existing behavior to preserve.**
- **Existing failing bug reproduction or new test fixture.**
- **Files likely to change.**
- **Potential version, Unicode, package, and AI compatibility effects.**
- **Rollback approach** (revert the focused commit; avoid irreversible migrations).

Run the baseline. Use `git status --short`, `git diff`, and an isolated branch/worktree where possible. Never silently overwrite uncommitted work by another agent.

### 9.2 During implementation

- Keep changes small and feature focused.
- Prefer adding a failing regression test *before* fixing a translation bug.
- Do not refactor compiler, CLI, importer, and packaging in the same change unless inseparable and explicitly planned.
- Preserve backwards-compatible public API entry points or introduce deprecation warnings with tests.
- If the approach has significant compatibility risk, implement behind an opt-in flag or experimental module, not the default syntax.
- Update examples only to reflect tested language behavior, not desired future syntax.
- Tests must be deterministic, not rely on order, and restore global interpreter state they modify.

### 9.3 Before marking done

Required checks:

- [ ] Relevant focused test demonstrates the feature or regression fix.
- [ ] Previously passing tests still pass.
- [ ] Language translation preserves strings/comments and valid Python identifiers in relevant contexts.
- [ ] Mixed `.urdu`/`.py` use has not regressed.
- [ ] Python versions and optional dependencies are reported honestly.
- [ ] User-visible syntax and APIs are documented.
- [ ] No unsafe secrets, hard-coded machine paths, gratuitous downloads, or new mandatory AI frameworks.
- [ ] Changelog / task tracker / compatibility matrix updated as applicable.
- [ ] If new syntax: canonical naming review and ADR completed.
- [ ] Handoff note records how to reproduce success and remaining risks.

**Do not mark `DONE` until all applicable criteria are met.** If necessary, mark `BLOCKED` with a narrow reason and the next concrete step.

### 9.4 Severity of changes

| Risk | Examples | Minimum action |
|---|---|---|
| **Low** | Typo in docs, extra passing unit test | Focused test/review; log change |
| **Medium** | Non-public refactor, better CLI error | Baseline + focused regression tests |
| **High** | Keyword translation, aliases, imports, namespace, source maps | ADR, regression tests, multi-version checks |
| **Critical** | Language syntax rename, importer precedence, Python version drop, PyPI publish | Maintainer sign-off, migration plan, full release suite |

### 9.5 Reverting a failed change

If a change breaks core functionality:

1. Identify the first failing regression and affected scope.
2. Do not "fix" it by removing the test.
3. Revert the offending focused commit or temporarily disable a new opt-in feature.
4. Restore the last known good test state.
5. Document the failure and create a new scoped task with a reproducer.

---

## 10. Test Pyramid and Required Suites

### 10.1 Core fast suite (no network or heavy dependencies)

- Keyword mapping and canonical names.
- Strings, comments, raw strings, multiline strings, f-strings, and escaped characters.
- Unicode identifiers, normalization edge cases, BOM handling.
- Original indentation, CRLF/LF handling, and source mapping.
- Control flow, comprehensions, generators, exceptions, decorators, classes, async constructs (syntax at least).
- Normal English Python programs pass through without unwanted mutations.
- Attribute and imported symbol names are preserved.
- Imports, packages, circular imports, module caching, correct standard precedence.
- CLI, exit status, argv, syntax errors, runtime errors, module invocation.
- Built-in alias identity and name-shadowing behavior.
- Packaging metadata and clean installation when possible.

### 10.2 Critical negative/edge examples

For each, decide intended semantics and lock them in tests:

```python
# Must not turn inside strings/comments into syntax.
متن = "اگر فنکشن واپس"
# اگر ورنہ should remain a comment

# Attribute spellings can be legitimate names.
obj.اگر
obj.واپس

# If a Python function accepts a Unicode keyword named 'اگر',
# specify how users call it without corrupting the keyword argument.
# A future test can use **{"اگر": 1} as the unambiguous escape hatch.

# Imported Python symbols may be named like Urdu keywords;
# preserve access to their actual exported names by documented rules.

# Real library members must never be renamed.
result = np.mean([1, 2, 3])
weights = model.state_dict()

# Context-sensitive constructs must not rewrite unrelated names.
# match/case/type require explicit parser-aware tests.
```

Also test strings that contain `#`, quotes, different newline styles, Unicode punctuation, bidirectional controls, Arabic/Persian lookalikes, and Python's permitted identifier classes.

### 10.3 Differential verification

For every valid Urdu sample with an obvious Python equivalent:

1. Run the UrduPy version.
2. Run the equivalent Python version under the **same CPython and library versions**.
3. Compare values, stdout/stderr, exception types, important trace details, and module behavior as appropriate.
4. Report deliberate differences (Urdu aliases, source filenames) explicitly.

Do not compare only printed strings for tensor or numerical code; check numerical results, shapes, dtypes, or gradients with suitable tolerances.

### 10.4 Environment matrix

At a minimum, investigate coverage across:

- **Interpreter:** Latest stable CPython and supported earlier minors, as officially confirmed.
- **OS:** Linux, Windows, macOS, depending on CI availability.
- **Hardware:** baseline CPU; optional GPU runners.
- **Architectures:** available x86-64 and ARM builds where packages exist.
- **Library groups:** core-only, science, vision, torch/vision, NLP/LLM, server.

Never claim combinations that were not actually run.

### 10.5 Test commands

For the original prototype:

```bash
python -m unittest discover -s tests -v
python -m urdupy run examples/demo.urdu
python -m urdupy translate examples/demo.urdu
```

After adopting a validated pytest development environment, use commands such as:

```bash
python -m pytest tests/ -q
python -m pytest tests/compatibility/ -q
python -m pytest tests/integration/ -q
python -m pip check
```

These are **target conventions**, not assertions that those folders already exist. Do not report optional test-suite commands as passed if dependencies or test markers made them skip.

---

## 11. Project Roadmap and Acceptance Gates

Milestones are sequential at the integration level. Agents may research future work in parallel but cannot declare a later milestone complete when its foundation is missing.

### M0 — Research, baseline, and language design

**Deliver:** Existing-code audit; Python-version research; token-vs-CST ADR; Urdu naming ADR; import contract; core tests; package name research.

**Exit gate:** A written spec exists, baseline recorded, risk list present, controversial keyword spellings explicitly provisional.

### M1 — Robust lightweight language core

**Deliver:** Context-aware translator, Urdu keyword glossary, compiler, script runner, existing English Python pass-through, built-in alias design, tests.

**Exit gate:** All supported core grammar examples pass; no strings/comments/attributes corrupted; CLI `run` and `translate` work; no regression in existing v0.1 use cases.

### M2 — Two-way modules and diagnostics

**Deliver:** `.urdu` packages and imports, optional Python import hook, syntax checking, tracebacks, source maps, state isolation.

**Exit gate:** Cross-language imports, circular imports, line/column cases, CLI status, and package semantics pass on supported Python versions.

### M3 — Scientific + AI interoperability

**Deliver:** CPU NumPy, OpenCV, PyTorch, torchvision integration tests and examples; package/version matrix; optional scientific extras.

**Exit gate:** AI-001 through AI-004 pass on at least one documented compatible CPU environment, and no core-suite regression occurs.

### M4 — Advanced AI + developer experience

**Deliver:** Offline Transformers testing, usable diagnostics, RTL guidance, editor syntax roadmap, optional REPL, educational docs.

**Exit gate:** Documented actual feature status, sensible ergonomic examples, verified advanced-library combinations; REPL if claimed available.

### M5 — Public package readiness

**Deliver:** Verified wheel/sdist, clean pip installation, CI matrix, contributor docs, security notes, changelog, TestPyPI plan, release notes.

**Exit gate:** Release checklist fully verified, legal/name requirements resolved, explicit maintainer publication approval.

### M6 — Stable syntax and wider ecosystem (future)

**Deliver:** Mature language spec and deprecation policy, stable editor tooling, documented 1.0 contract, wider framework testing.

**Exit gate:** Stable behavior across versions and clear maintainer/community process.

---

## 12. Persistent Task Tracker — Single Source of Project State

**Rules:** Every agent must update this section when completing or blocking assigned work. Work IDs are stable; do not renumber old tasks. Use `TODO`, `IN_PROGRESS`, `BLOCKED`, `IN_REVIEW`, `DONE`, or `DEFERRED`. Add owner/session information instead of claiming another agent's task. Use a real commit/PR/test reference where possible. The table is a **plan**, not a completion claim.

### 12.1 Current project snapshot

| Field | Value |
|---|---|
| Project | UrduPy |
| Current documented phase | **All local M0-M6 engineering gates complete**; external publication/hosted/community gates separate; docs/implementation-handoff.md |
| First public release | Source public at [Optimizer077/urdupy](https://github.com/Optimizer077/urdupy); package **NOT PUBLISHED to PyPI**; local 0.1.0a1 alpha artifacts |
| Latest stable CPython support | Core PASS on 3.12.13, 3.13.13, 3.14.6 and latest stable 3.15.0; Windows AMD64; metadata >=3.12,<3.16 |
| Official PyPI project name | **UNVERIFIED** ownership/registerability; candidate endpoints returned HTTP 404 |
| Core quick-test result | **230/230 PASS, zero skips on all four production minors and clean installs**; preserved 57-test M0 baseline; URD-031 handoff |
| NumPy/OpenCV/PyTorch support | **19/19 offline CPU tests PASS, zero skips**, includes complete Urdu ResNet/SGD/AdamW/vision/BERT/graphs; 13,975 names in 24 namespaces audited |
| Current release blockers | No failing local engineering checks; external publication approval/name ownership/remote CI/community feedback remain |
| Maintainer-approved canonical grammar | Delegated technical **1.0-local** contract, 35 hard + 2 contextual words and 15 aliases; human naming feedback not fabricated |

### 12.2 Backlog

| ID | Priority | Milestone | Task | Status | Owner | Acceptance evidence |
|---|---|---|---|---|---|---|
| URD-001 | P0 | M0 | Inventory existing repo, version, tests, and APIs | DONE | Integrator | `docs/phase-1.md`: fresh folder; 0-test baseline; local interpreter observations |
| URD-002 | P0 | M0 | Verify latest stable CPython and version matrix | DONE | platform_research | `docs/research/python-and-packaging.md`, ADR-008; official 3.15.0 release research; local 3.11/3.13 probes; CI range proposed, not certified |
| URD-003 | P0 | M0 | Compare tokenizer/CST/grammar strategies | DONE | compiler_probe / integrator review | ADR-005; 48 focused regressions on both local minors; bounded proof, not production compiler |
| URD-004 | P0 | M0 | Evaluate Urdu keyword names and beginner grammar | DONE | language_design / integrator review | Grammar/function spec, naming audit/proposals, ADR-004, 5 verified pairs and blank feedback worksheet; stable naming acceptance pending |
| URD-005 | P0 | M1 | Fix context-sensitive identifier rewriting | DONE | compiler_probe / integrator | Production compiler, API collision protections; 54 compiler regressions and 159 core tests on all four minors; ADR-011 |
| URD-006 | P0 | M1 | Harden f-string, multiline and Unicode behavior | DONE | compiler_probe | Nested/debug f-strings, host newline/comment behavior and Unicode maps; 3.12/3.13/3.14/3.15 verified |
| URD-007 | P0 | M1 | Define built-in alias namespace and shadowing | DONE | Integrator | Per-module real builtins, local/global shadow/delete, no implicit exports; runtime tests; ADR-013 |
| URD-008 | P0 | M1 | Establish no-regression core test suite | DONE | Team | 159 dependency-free core tests, preserved M0 baseline; 12 CI jobs configured, remote status separate in URD-022 |
| URD-009 | P0 | M2 | Harden `.urdu` import hook and packages | DONE | Integrator / independent AI-agent review | 18 importer tests: regular/namespace packages, circular/relative/reload/resources, concrete Python/native/zip/custom priority |
| URD-010 | P1 | M2 | Add `check` command without execution | DONE | Integrator | Multiple-file check compiles without source/import execution; CLI regression tests |
| URD-011 | P1 | M2 | Improve original-source tracebacks/columns | DONE | Compiler / integrator | Original error text/start/end, mapped AST byte spans, owned LF-only source caches and REPL history tests |
| URD-012 | P0 | M3 | NumPy/science integration | DONE | AI agent / integrator | AI-001 ndarray/dtype/broadcast/indexing; NumPy 2.5.4 CPU environment; saved JSON evidence |
| URD-013 | P0 | M3 | OpenCV/Pillow integration | DONE | AI agent / integrator | AI-002 OpenCV 5.0.0.93 and Pillow 12.3.0 synthetic/local fixtures; one headless provider |
| URD-014 | P0 | M3 | PyTorch training from Urdu classes | DONE | AI agent / integrator | AI-003 real torch 2.14.1+cpu module, analytic autograd/SGD and state_dict roundtrip |
| URD-015 | P0 | M3 | OpenCV→NumPy→PyTorch flow | DONE | AI agent / integrator | AI-004 synthetic NumPy/OpenCV/tensor/model channel/dtype path; 9/9 isolated compatibility tests |
| URD-016 | P1 | M3 | torchvision version/transform integration | DONE | AI agent / integrator | torchvision 0.29.1+cpu transforms/model offline; official matched-version evidence and constraints |
| URD-017 | P1 | M4 | Transformers offline test example | DONE | AI agent / integrator | AI-005 Transformers 5.19.0 tiny local Bert config/model; no pretrained download; saved JSON |
| URD-018 | P1 | M4 | Improve Urdu diagnostics / beginner messages | DONE | Integrator / docs agent | Original-source Python exception types and concise Urdu indentation/colon hints; no invented stable error codes |
| URD-019 | P2 | M4 | Evaluate optional REPL and editor support | DONE | Integrator / packaging agent | Tested multiline REPL, session-isolated source history; editor JSON syntax/config validated, visual editor unverified |
| URD-020 | P0 | M5 | Confirm distribution name and package metadata | IN_REVIEW | Packaging agent / maintainer | Local urdupy-design-lab metadata validated; public registerability/ownership remains external OPEN gate |
| URD-021 | P0 | M5 | Build and install wheel/sdist in clean env | DONE | Integrator / independent artifact review | Isolated wheel/sdist build; wheel clean-installed on all four minors and sdist on 3.15; each 159 core tests + pip check + installed CLI; dist/verification.json |
| URD-022 | P0 | M5 | GitHub CI across supported Python versions | IN_REVIEW | Packaging agent / maintainer | 12 configured jobs; first [hosted run](https://github.com/Optimizer077/urdupy/actions/runs/38685274655) in progress after public source push; outcome pending |
| URD-023 | P1 | M5 | Release docs, changelog, security, license | DONE | Packaging agent / integrator | License/security/contributing/tutorial/reference/CLI/release/changelog and current handoff |
| URD-024 | P0 | M5 | Public release readiness and approval | BLOCKED | Maintainer | PyPI/release approval + verified gates remain; GitHub source publication separately authorized and completed in URD-030 |
| URD-025 | P1 | M0-M5 | Define Unicode/RTL testing guidance | DONE | Team | Unicode/RTL guidance and textual/span/filename fixtures on four Windows minors; other platform/editor rendering explicitly unverified |
| URD-026 | P1 | M1-M5 | Track compatibility changes and deprecations | DONE | Team | Versioned 1.0-local technical contract, immutable lexicon, ADR/migration policy, preserved M0 API and changelog |
| URD-027 | P1 | M3 | Train and save a nonlinear neural network in UrduPy | DONE | Integrator | 600-epoch CPU XOR: 1021/1024 held-out correct; exact Python/state reload; 2 focused tests and 11/11 full optional suite; results-training.json |
| URD-028 | P1 | M3 | Urdu ResNet with actual STL-10 training and Urdu graphs | DONE | Integrator + model/data/plot agents | Full-width96px ResNet18, 50epochs RTX5060Ti; epoch44 bestval77%, test6188/8000=77.35%; 22 offline tests + independent raw-label/hash audit PASS; four Urdu PNG/SVG pairs visually reviewed |
| URD-029 | P1 | M5 | Pip dependency extras and verified local installation | DONE | Integrator | science/ai extras; actual pip AI/science/core installs; 162core tests on4clean wheel minors +315sdist; 11AI tests; CUDA retained; dist/pip-extras evidence; no publication |
| URD-030 | P1 | M5 | Publish the source as a public GitHub repository | DONE | Integrator | [Optimizer077/urdupy](https://github.com/Optimizer077/urdupy), public visibility and anonymous clone verified; initial main 841399b; cloned 162 core tests and five example pairs PASS; hosted CI in progress |
| URD-031 | P0 | M3-M5 | Complete Urdu dependency source surface and Urdu commands | DONE | Integrator + three parallel agents | 763 aliases and total identifier/text spellings; six zero-Latin examples; 230 core tests on four clean wheel minors + 3.15 sdist; 19 AI tests; 13,975 names/24 namespaces; installed CUDA autograd PASS; docs/urdu-only-handoff.md |

### 12.3 Active tasks / ownership

| Task ID | Agent / branch | Start | Files owned | Scope | State |
|---|---|---|---|---|---|
| URD-001 / integration | Integrator | 2026-10-15 | `AGENTS.md`, `README.md`, lexicon, `tests/test_design.py`, phase scope/roadmap/handoff | Baseline, shared registry, namespace experiment, review, tracking | DONE (M0 scope) |
| URD-002 / contracts | platform_research | 2026-10-15 | `docs/research/*`, ADR-006/007/008/009 | Official research, proposed namespace/import/version/name contracts | DONE (research/contracts only) |
| URD-003 / proof | compiler_probe | 2026-10-15 | `urdupy/experimental/*`, `tests/test_translation.py`, ADR-005 | Bounded span/context translation experiment | DONE (M0 scope) |
| URD-004 / names | language_design | 2026-10-15 | Language/naming docs, ADR-004, `examples/*` | Grammar, function design, alternatives, bilingual exercises | DONE (design; naming provisional) |

| URD-005/006/011 | compiler_probe | 2026-10-15 | Production compiler/maps/tests/docs, ADR-011 | Four-minor compiler and source fidelity | DONE / frozen |
| URD-007/009/010/018/019 | Integrator | 2026-10-15 | Runtime/importer/CLI/REPL and focused tests, ADR-013 | Execution/imports/diagnostics/state | DONE / frozen |
| URD-012..017 | language_design (AI role) | 2026-10-15 | Optional compatibility suites, paired science examples, constraints and evidence | Offline real-library integration | DONE / frozen |
| URD-020..023/026 | platform_research (packaging role) | 2026-10-15 | Metadata/manifest/CI/editor/license/docs, ADR-012 | Local packaging/technical contract; external gates separate | DONE drafts; integration verification |
| URD-030 | Integrator / main | 2026-10-15 | README.md, AGENTS.md, publication handoff and Git configuration | Public GitHub source repository; preserve language/runtime and existing ignored local artifacts | DONE |
| URD-031 | Integrator + catalog/examples/CLI agents | 2026-10-15 | Integrator: compiler/runtime/shared docs; agents: separate catalog, CLI/verifier, examples/tests | Complete Urdu source mode, native objects and legacy compatibility | DONE; independently reviewed |

Only one agent should **directly edit the canonical keyword registry at a time**. Coordinate merge timing for importer/translator interfaces. Parallel agents should prefer separate tests/docs or clearly partitioned files.

### 12.4 Recently completed work

| Date | Task ID | Evidence | Files changed | Notes |
|---|---|---|---|---|
| 2026-10-14 | BASELINE-REFERENCE | Seven `unittest` tests passed using Python 3.13.5 in the supplied prototype checkout | None in original prototype | Historical starting point only; not proof of new changes |
| 2026-10-15 | URD-001 | `docs/phase-1.md`, `docs/handoff.md` | New folder, scope, registry, tracking | Empty baseline recorded honestly; no Git/prototype present |
| 2026-10-15 | URD-002 | Official source links and both research probes | Research notes and ADR-006/007/008/009 | Stable-version research is separate from tested support; name/package gates OPEN |
| 2026-10-15 | URD-003 | 48 focused tests; integrated 57/57 on both local minors | Experimental compiler, regression suite, ADR-005 | Independent review fixed relative-only import gap; production compiler remains M1 |
| 2026-10-15 | URD-004 | 5/5 paired examples on both local minors | Grammar/function spec, naming workshop, ADR-004, examples/verifier | Disputed spellings provisional; no human survey claimed |
| 2026-10-15 | URD-030 | Public GitHub repository, matching remote main 841399b, anonymous clone; cloned 162 core tests and five pairs PASS | README.md, AGENTS.md, implementation handoff, initial source commit | Source publication only; hosted CI in progress and PyPI remains unpublished |

### 12.5 Open blockers and risks

| Risk ID | Issue | Impact | Mitigation | Status |
|---|---|---|---|---|
| R-001 | Token substitution in non-keyword positions | Can break valid Python APIs | Syntax context tests, ADR, compiler hardening | OPEN |
| R-002 | Soft keywords / f-string changes across Python minors | Compatibility regressions | Version matrix, feature fixtures | OPEN |
| R-003 | Urdu/Arabic Unicode lookalikes and RTL controls | Confusing source, diagnostics | Naming policy, lint warnings, tests | OPEN |
| R-004 | Python-vs-Urdu module naming collisions | Unpredictable imports | Documented precedence, hook tests | OPEN |
| R-005 | Native scientific wheel/platform compatibility | Install/runtime failures | Optional packages, matrix, official install guides | OPEN |
| R-006 | PyPI distribution name availability | Release naming may change | Registry verification, fallback name | OPEN |
| R-007 | Names too formal/long for beginners | Language adoption friction | Naming proposal + usability review | OPEN |
| R-008 | Agent parallel edits causing regressions | Lost work or hidden breakage | Task ownership, focused commits, CI gates | OPEN |

---

## 13. Agent Roles, Concurrency, and Coordination

An agent may hold more than one role, but task ownership and integration checks remain mandatory.

### Research & Language Design Agent

Research current CPython language/tokenizer support, Unicode, naming, source grammar, Python/Urdu usability tradeoffs, and ADRs. **Do not silently alter canonical names.**

### Compiler Agent

Own context-aware parsing/translation, keyword recognition, f-strings, soft keywords, mapping, and compiler regression tests. Maintain source-to-source determinism.

### Runtime & Imports Agent

Own execution environments, alias namespace, module loading, metadata, import isolation, tracebacks, and `.py`/`.urdu` integration tests.

### AI Compatibility Agent

Own NumPy/OpenCV/PyTorch validation, deterministic CPU fixtures, version records, device notes, optional advanced suites, and user-visible AI examples. **Do not change grammar solely to make one AI example pass.** Report compiler issues to the compiler owner.

### Packaging, Release & Docs Agent

Own `pyproject.toml`, version policy, CLI docs, build/wheel/sdist checks, CI matrix, PyPI procedures, beginner education, and release gates. Do not publish independently.

### Integrator / Reviewer

Own merge ordering, regression gates, cross-agent contract review, task status integrity, and accepted ADR checks. The integrator should try not to be the sole reviewer of risky compiler changes.

### Multi-agent merge protocol

1. Choose non-overlapping task IDs and branch/worktree scopes.
2. Record ownership in §12.3.
3. Agree on interfaces before parallel coding (e.g. `translate`, `compile_urdu`, loader registration API).
4. Make isolated focused commits; no unreviewed sweeping repo rewrites.
5. Run your focused tests and baseline tests.
6. Integrate one change at a time; rerun the baseline after each integration.
7. Resolve conflicting files through deliberate review, not blind overwrite.
8. Update the tracker and handoff immediately after integration.

**Review must include tests for behavior, not only code style.** If two agents disagree about a language spelling or public behavior, require a short ADR and maintainer decision before merging that interface.

---

## 14. Documentation and Education Guidelines

User-facing docs should be understandable by people with varying experience, including Urdu speakers new to programming.

### Writing style

- Use straightforward English for developer infrastructure explanations and **clear Urdu** for language tutorials; bilingual glossaries are encouraged.
- Present UrduPy code and equivalent Python side by side for key concepts.
- Avoid unexplained computer-science jargon in beginner material.
- Explain what `فنکشن`, `واپس`, `اگر`, `ہر`, and `میں` mean through short programs.
- Explain the difference between `دکھاؤ` (output) and `واپس` (return) explicitly.
- Explain true/false/None independently rather than describing all as "empty" or "nothing".
- Explain the role of indentation and why block-ending `:` matters.
- Do not translate external library API names in tutorials; explain them in Urdu commentary instead.
- Keep code examples runnable; add tests or automated execution checks for documentation snippets where feasible.
- Document source encoding, CLI invocation, `.urdu` imports, and basic troubleshooting.

### Beginner curriculum, in order

1. Hello world, strings, and `دکھاؤ`.
2. Variables and basic arithmetic.
3. `اگر`, `ورنہ`, comparisons, and Boolean values.
4. `ہر`, `جب_تک`, `حد`, and lists.
5. `فنکشن`, parameters, and `واپس`.
6. Imports and the standard library.
7. Classes and objects.
8. NumPy arrays and basic AI math.
9. OpenCV images and PyTorch model examples.
10. Modules, error handling, async and advanced Python interoperability.

### Error message principles

Prefer:

> `SyntaxError` at `مثال.urdu:5`: block after `اگر` requires indentation. (`اگر` means Python `if`.)

over vague messages such as "Your Urdu is wrong." Provide stable error codes only when a catalog exists. Keep the Python exception type visible for advanced debugging and web documentation.

---

## 15. Design Decisions / ADR Process

Create accepted ADR files later under `docs/adr/` if useful; until then, record summary decisions and links here. An ADR is required for changes to:

- Canonical Urdu spellings or accepted alternative aliases.
- Parser strategy or source mapping contract.
- Grammar shape or punctuation.
- Default `.py`/`.urdu` import precedence.
- Runtime alias injection or namespace scope.
- Version support policy.
- Public CLI/API compatibility.
- Mandatory dependencies and distribution naming.
- Release versioning expectations.

### Current decision register

| ADR ID | Topic | State | Current direction |
|---|---|---|---|
| ADR-001 | Runtime | PRINCIPLE ACCEPTED | Compile/execute through CPython, not new VM |
| ADR-002 | Basic grammar | PRINCIPLE ACCEPTED | Python statement shapes and punctuation with Urdu keywords |
| ADR-003 | External libraries | PRINCIPLE ACCEPTED | Keep original import names and external APIs |
| ADR-004 | Keyword lexicon | PROVISIONAL | [Naming decision](docs/adr/004-lexicon.md); guide spellings retained experimentally; alternatives and human feedback pending |
| ADR-005 | Compiler technique | M0 EXPERIMENT / M1 OPEN | [Bounded tokenizer/span proof](docs/adr/005-translator.md); production grammar strategy requires broader evidence |
| ADR-006 | Built-in alias resolution | IMPLEMENTED LOCALLY | [Original proposal](docs/adr/006-builtins.md), [accepted runtime](docs/adr/013-runtime-imports.md); copied real builtins and scoping tested |
| ADR-007 | Import loader | SUPERSEDED FOR PRODUCTION | [Historical finding](docs/adr/007-imports.md); [ADR-013](docs/adr/013-runtime-imports.md) resolves regular initializers and tests Python priority |
| ADR-008 | Python version range | ACCEPTED LOCAL 3.12-3.15 | [Research](docs/adr/008-python-versions.md), current metadata and four-minor source/clean install evidence; other OSes unverified |
| ADR-009 | PyPI name | PROPOSED / OWNERSHIP OPEN | [Distribution decision](docs/adr/009-distribution.md); HTTP 404 observations do not prove registerability |
| ADR-010 | AI extras | IMPLEMENTED CPU ENVIRONMENT POLICY | [Isolated optional libraries](docs/adr/010-ai-environments.md); zero core dependencies, actual 9/9 offline tests |

| ADR-011 | Production compiler/maps | ACCEPTED LOCAL CONTRACT | [Production frontend](docs/adr/011-production-compiler.md); 54 focused cases on all four minors; explicit template boundary |
| ADR-012 | Local packaging/stability | ACCEPTED LOCAL CONTRACT | [Local release policy](docs/adr/012-local-release-policy.md); alpha package, 1.0-local grammar, external gates distinct |
| ADR-013 | Runtime/imports/state | ACCEPTED LOCAL CONTRACT | [Owned execution and Python priority](docs/adr/013-runtime-imports.md); runtime/import/CLI/REPL regressions and installed checks |
| ADR-014 | Pip dependency extras | ACCEPTED LOCAL CONTRACT | [Standard optional dependencies](docs/adr/014-pip-extras.md); science/ai automatic pip resolution, zero-core dependencies and explicit device selection |
| ADR-015 | Complete Urdu library spellings | ACCEPTED LOCAL CONTRACT | [Explicit source mode](docs/adr/015-complete-urdu-surface.md); native objects, curated aliases and exact total fallback |

### ADR template

```markdown
# ADR-NNN: Short title

- **Date:** YYYY-MM-DD
- **Status:** Proposed / Accepted / Rejected / Superseded
- **Owners:** Agent or maintainer
- **Affected interfaces:** ...
- **Context and user problem:** ...
- **Options considered:** At least two viable options
- **Decision:** ...
- **Why:** Evidence and tradeoffs
- **Compatibility impact:** Existing programs, docs, tests, libraries
- **Alternatives rejected and why:** ...
- **Migration/deprecation plan:** ...
- **Verification:** Exact test commands/results
- **Rollback strategy:** ...
```

---

## 16. Quality Gates for Pull Requests and Releases

### 16.1 PR/agent completion gate

A change may enter review only if:

- Task ID exists and scope matches.
- Formatter/linter/tests specified by the repo pass or failures are explicitly reported.
- Public changes are documented and tested.
- Language grammar changes have accepted naming review/ADR.
- Source translation regressions are tested, particularly Unicode and identifier contexts.
- No new required heavy AI framework exists in core.
- Commit/PR summary states compatibility impact and rollback instructions.

### 16.2 Release candidate gate

Before calling a release ready:

- [ ] Official release Python support range verified and correctly declared.
- [ ] Core fast suite passes on every declared version/platform target.
- [ ] No unresolved P0 regression or unknown syntax corruption.
- [ ] Documented AI compatibility claims have recorded library/version/platform evidence.
- [ ] `.py`/`.urdu` imports and appropriate tracebacks verified.
- [ ] CLI help, package entry points, and `python -m urdupy` verified.
- [ ] `pip install` works from built wheel in a clean environment.
- [ ] sdist is complete and buildable in a clean environment.
- [ ] Dependency conflicts and `pip check` reviewed.
- [ ] README, beginner tutorial, grammar reference, changelog, license, and security policy updated.
- [ ] Distribution name, ownership, and project metadata reviewed.
- [ ] PyPI/TestPyPI publishing method reviewed for secret safety.
- [ ] Actual release approval from maintainer recorded.

A **pre-release** may have known limitations, but they must be clearly identified; do not mark a failed gate green by rewriting the label.

---

## 17. Project Compatibility Matrix — Fill Only With Evidence

Use this table to record **actual runs**, not hopes. Add rows with exact Python/library versions and test command references. `UNVERIFIED`, `PASS`, `FAIL`, `SKIP`, `BLOCKED` are distinct.

| Date | Python | OS/arch | UrduPy commit | Library versions | Test suite / command | Result | Notes |
|---|---|---|---|---|---|---|---|
| 2026-10-14 | 3.13.5 | Local environment (details not recorded) | Prototype snapshot | Core standard library | `python -m unittest discover -s tests -v` | PASS (7 tests) | Historical reference; not a release matrix |
| 2026-10-15 | 3.15.0 latest stable | Windows AMD64 / normal CPython | Local 0.1.0a1 / 1.0-local; no Git | Standard library | Exact .runtimes/cpython315 interpreter; unittest discover -s tests -q | PASS (159, zero skips) | Full production core, not only research |
| 2026-10-15 | 3.13.13 Anaconda | Windows build 26200 / AMD64 | Local 0.1.0a1 draft; no Git | Standard library | `python -X utf8 -m unittest discover -s tests -v` | PASS (57 tests, 0 skips) | Bounded M0 experiment; not full grammar/runtime support |
| 2026-10-15 | 3.11.9 | Windows build 26200 / AMD64 | Local 0.1.0a1 draft; no Git | Standard library | `py -3.11 -X utf8 -m unittest discover -s tests -v` | PASS (57 tests, 0 skips) | Older tokenizer family; no broad version range implied |
| 2026-10-15 | 3.13.13 / 3.11.9 | Same Windows host | Local draft; no Git | Standard library | `python examples/verify_examples.py`; `py -3.11 examples/verify_examples.py` | PASS (5 pairs on each) | Stdout, typed values/expectations, signatures and defaults; fixture namespaces |
| 2026-10-15 | 3.13.13 / 3.11.9 | Same Windows host | Local draft; no Git | Standard library | `python docs/research/probe_environment.py`; `py -3.11 docs/research/probe_environment.py` | PASS (observations) | F-string tokenizer difference; namespace initializer pitfall confirmed |
| 2026-10-15 | 3.13.13 | Windows AMD64 CPU | Local 0.1.0a1 / 1.0-local | NumPy 2.5.4 | AI-001 | PASS | Recorded isolated CPU run; results-ai.json; no weights/network |
| 2026-10-15 | 3.13.13 | Windows AMD64 CPU | Local 0.1.0a1 / 1.0-local | OpenCV-headless 5.0.0.93 / Pillow 12.3.0 | AI-002 | PASS | Recorded isolated CPU run; results-ai.json; no weights/network |
| 2026-10-15 | 3.13.13 | Windows AMD64 CPU | Local 0.1.0a1 / 1.0-local | torch 2.14.1+cpu | AI-003 | PASS | Recorded isolated CPU run; results-ai.json; no weights/network |
| 2026-10-15 | 3.13.13 | Windows AMD64 CPU | Local 0.1.0a1 / 1.0-local | OpenCV-headless 5.0.0.93 / NumPy 2.5.4 / torch 2.14.1+cpu | AI-004 | PASS | Recorded isolated CPU run; results-ai.json; no weights/network |
| 2026-10-15 | 3.13.13 | Windows AMD64 CPU | Local 0.1.0a1 / 1.0-local | transformers 5.19.0 | AI-005 | PASS | Recorded isolated CPU run; results-ai.json; no weights/network |

| 2026-10-15 | 3.12.13 / 3.13.13 / 3.14.6 | Windows AMD64 / normal CPython | Local 0.1.0a1 / 1.0-local; no Git | Standard library | Each exact interpreter -X utf8 -m unittest discover -s tests -q | PASS (159 each, zero skips) | Separate actual runs on all three minors |
| 2026-10-15 | 3.13.13 isolated .venv-ai | Windows AMD64 CPU | Local 0.1.0a1 / 1.0-local | numpy 2.5.4; cv2 distribution 5.0.0.93; Pillow 12.3.0; torch 2.14.1+cpu; torchvision 0.29.1+cpu; transformers 5.19.0 | tools/run_compatibility.py --require-all; saved results-ai.json | PASS (9/9, zero skips) | AI-001..005; no model weights or test network |
| 2026-10-15 | 3.13.13 default Anaconda | Windows AMD64 CPU | Local source | numpy 2.5.2; Pillow 12.3.0; torch 2.14.1+cpu | Optional runner; results-default.json | PARTIAL (5 pass / 4 skip) | Missing cv2/torchvision/Transformers; not conflated with isolated pass |
| 2026-10-15 | 3.13.13 .venv-ai | Windows AMD64 CPU | Local source, URD-027 | Same full CPU tuple; torch 2.14.1+cpu | tools/run_compatibility.py --require-all; results-training.json | PASS (11/11, zero skips) | Adds full nonlinear training/Python agreement/save/reload; 99.71% on separate synthetic test set |
| 2026-10-15 | 3.13.13 .venv-resnet | Windows AMD64 / RTX5060Ti16GiB, driver591.74 | Local source, URD-028 | torch2.14.1+cu130, torchvision0.29.1+cu130, CUDA13.0, cuDNN9.24; numpy2.5.4, Pillow12.3.0, matplotlib3.11.2, arabic-reshaper3.0.1, python-bidi0.6.11 | 50epoch actualSTL10 run; 22 experimenttests; saved-results verifier | PASS | 77.35% on8000 test, selectedvalepoch44; exact checkpoint logits; UrduPNG visual review/SVGXML; source/hash/labels/counts audit |
| 2026-10-15 | 3.13.13 | Windows AMD64 | Initial public source 841399b / URD-030 | Standard library only | `python -X utf8 -m unittest discover -s tests -q`; `python -X utf8 examples/verify_examples.py` | PASS (162 core, zero skips; five pairs) | Fresh publication baseline; hosted CI is separate and pending |

If a test is skipped because `torch` or another dependency isn't installed, write **SKIP** with the reason rather than "supports torch." Record hard-to-reproduce accelerator details when relevant.

---

## 18. Working Templates — Use These Instead of Unstructured Notes

### 18.1 New task proposal

```markdown
#### URD-NNN — Descriptive title
- **Owner:** Agent / branch
- **Priority:** P0/P1/P2
- **Milestone:** M0..M6
- **State:** TODO / IN_PROGRESS / BLOCKED / IN_REVIEW / DONE
- **Problem:** One paragraph, user impact
- **Scope:** Exactly what will change
- **Out of scope:** Explicit exclusions
- **Interfaces touched:** Compiler/runtime/imports/CLI/docs/packaging
- **Current behavior and baseline:** Exact repro and test result
- **Plan:** Small implementation steps
- **Acceptance tests:** Exact scenarios and commands
- **Risks:** Keywords, Unicode, Python versions, external libs, API
- **Rollback:** Revert scope or feature flag
- **Evidence at completion:** Commit/PR, tests, docs, matrix
```

### 18.2 Grammar or naming proposal

```markdown
#### NAME-NNN — Python construct / Urdu concept
- **Proposed canonical Urdu word:** ...
- **Current/legacy spelling:** ...
- **Python counterpart:** ...
- **Alternatives considered:** ...
- **Plain Urdu explanation:** ...
- **Why a beginner will understand it:** ...
- **Possible confusion:** ...
- **Ease of typing / Unicode spelling concerns:** ...
- **Grammar context:** Keyword / soft keyword / identifier alias
- **Examples (simple / advanced):** ...
- **Collision/identifier risk:** ...
- **Compatibility and migration impact:** ...
- **Review evidence / native speaker feedback:** ...
- **Decision:** PROPOSED / ACCEPTED / REJECTED
- **Tests and documentation needed:** ...
```

### 18.3 Work-session log / handoff

```markdown
#### Session YYYY-MM-DD — Agent / Task IDs
- **Starting branch/commit:** ...
- **Starting baseline:** command and result
- **Work completed:** ...
- **Files changed:** ...
- **New tests:** ...
- **Validation:** command -> PASS / FAIL / SKIP with counts
- **Python + library versions actually used:** ...
- **Unresolved issues:** ...
- **Potential regressions / compatibility notes:** ...
- **Next safest task:** ...
- **Review status:** ...
```

### 18.4 Regression report

```markdown
#### REG-NNN — Summary
- **First detected:** YYYY-MM-DD
- **Affected code/commit:** ...
- **Minimal `.urdu` reproducer:** ...
- **Expected Python-equivalent behavior:** ...
- **Actual behavior:** ...
- **CPython version:** ...
- **Dependencies and versions:** ...
- **Severity:** Low / Medium / High / Critical
- **Root cause:** ...
- **Regression test:** ...
- **Fix and verification:** ...
- **Rollback / mitigation:** ...
```

### 18.5 Release note / changelog fragment

```markdown
## [Version] - YYYY-MM-DD
### Added
- ...
### Fixed
- ...
### Changed (behavior / compatibility)
- ...
### Deprecated
- ...
### Verified Compatibility
- Python ... / platform ... / NumPy ... / torch ... / cv2 ...
### Known Limitations
- ...
### Migration Notes
- ...
```

---

## 19. Initial Research Assignments: Give Agents Real Homework

Before expanding the compiler, agents should answer the following in evidence-backed design notes:

**Grammar & names**

1. Which current Urdu keyword names are most intuitive to a Pakistani Urdu-speaking beginner?
2. Is `غیر_متزامن` too formal as an everyday `async` keyword? Compare at least two alternatives and existing compatibility impact.
3. Do users understand `گزر` as `pass`, `پیدا_کرو` as `yield`, `ہے` as identity comparison, and `کچھ_نہیں` as `None`?
4. What is the simplest way to document Urdu spellings and avoid Arabic/Persian character mismatches?
5. How should English Python identifiers that coincide with Urdu reserved words be accessed when importing third-party libraries?
6. Are Urdu source filenames practical across Windows/macOS/Linux, archives, Git tooling, and Python's importer?
7. What common RTL editor issues can be documented without inventing an entirely new editor?

**Compiler**

8. On supported CPython versions, which syntax can a public-tokenizer-based translator handle correctly?
9. Which f-string cases, soft keywords, exceptions, and Python syntax require a more context-aware approach?
10. How can translated-source spans map precisely to original Unicode columns and errors?
11. Can the transformer leave ordinary English Python syntax bit-for-bit intact under specified conditions?
12. What is the minimum trustworthy test fixture matrix across Python releases?

**Runtime & AI**

13. Can Python's importlib semantics be preserved for `.urdu` packages, circular imports, and import precedence?
14. Which built-in alias mechanism best preserves Python name resolution and module introspection?
15. Which Python, PyTorch, torchvision, and OpenCV versions can be installed together on current supported platforms?
16. What small offline integration programs sufficiently demonstrate tensor gradients, OpenCV image processing, and real NumPy behavior?
17. Does the base package remain usable with zero scientific libraries installed?
18. Which PyPI distribution name is legally and technically available, and what is the migration route from `urdupy-demo`?

All answers should distinguish **verified**, **hypothesis**, and **open question**. Record decisions before turning them into defaults.

---

## 20. Recommended Next Steps for the First Coding Agent

Follow this exact sequence unless the existing repository is significantly different:

1. Read this file and inventory current code and tests.
2. Run baseline tests and record Python/version/OS and results.
3. Start URD-001 and URD-003: create a minimal regression fixture demonstrating token-name context hazards (strings, attributes, named imports, keyword arguments, `match`/`case`, f-strings).
4. Research version requirements and record URD-002 findings based on official CPython information.
5. Audit the §4 keyword registry for comprehension/typeability concerns, without prematurely renaming existing working keywords.
6. Draft ADR-005 with a testable translator strategy that preserves Python-native library identifiers.
7. Implement the smallest context-correct improvement (URD-005), keeping existing API stable; run tests.
8. Write a tiny offline NumPy/OpenCV/PyTorch compatibility test plan. Implement it only after the core translator has explicit regression coverage.
9. Update tasks, decisions, matrix, and handoff before stopping.

If execution capability is limited, do not fabricate results: commit a reliable design and tests that can later be run, mark them **UNVERIFIED**, and describe how to verify them.

### Definition of project success

UrduPy is successful when a learner can write understandable Urdu code **and** an experienced Python developer can use genuine PyTorch, NumPy, OpenCV, Transformers, and other installed libraries with ordinary Python objects, documented syntax, predictable imports, accurate diagnostics, and confidence that future UrduPy releases will not casually break their programs.

**Maintain the core promise: Urdu where it helps humans, Python compatibility everywhere it matters.**

---

## 21. Session Updates (append newest entries here)

- **2026-10-15 — URD-031 GitHub publication authorized.** Maintainer explicitly
  requests `push` after the complete Urdu surface implementation. Fresh baseline:
  230 core tests and five paired examples PASS on Python3.13.13; fetched
  origin/main equals local main at eed8d2a with no divergence. Reviewed 36 changed
  source/test/documentation files, 407,825 bytes before this log entry; no file
  exceeds1MB and credential/private-key token-pattern scan has no findings.
  Publication scope is this reviewed local update to Optimizer077/urdupy main.
  Environments, datasets, checkpoints, run/build output and dist remain ignored.
  This subsequent instruction authorizes the GitHub update; earlier URD-031
  no-public-upload statements describe the implementation phase. Remote commit
  identity and clean local status are verified after pushing.

- **2026-10-15 — URD-031 complete Urdu dependency surface.** Maintainer expands
  the old library-name non-goal and requests parallel agents. Fresh baseline:
  clean eed8d2a, 162 core tests + five pairs PASS, Python3.13.13 WindowsAMD64.
  Three agents owned catalog, CLI/verifier and examples/AI tests; integrator
  implemented explicit `# اردوپائی: مکمل` span lowering and runtime/import/REPL
  integration. ADR-015 records reserved spellings and legacy compatibility.
  763 curated entries plus exact Urdu-digit spellings reach all other identifiers
  and arbitrary strings. Native objects/gradients/protocols remain native.
  Six zero-Latin sources run NumPy, vision, SGD/AdamW/checkpoints, offline BERT,
  full ResNet18 and Urdu graph; all six actual main executions PASS. Current
  core230 tests PASS on clean wheel installs on3.12.13/3.13.13/3.14.6/3.15.0
  and separate clean3.15sdist build/install, no optional libraries, both consoles.
  Optional suite19/19 PASS; namespace audit13,975 names/24namespaces PASS.
  Independent15-test review repaired incompleteconsoleimports, escapedUrdukeyword
  exports and relativeencodedimports. Four README/guide snippets execute.
  Actual synthetic AdamW120-step loss3.77983999 ->0.00000151653; Urdu graph
  visually inspected by agent/integrator. Local core/GPU venvs pip-upgraded;
  outsidecheckout installed CUDA autograd PASS, torch2.14.1+cu130 retained.
  Final artifacts/checksums/reports: dist/urdu-only; handoff documents exact
  scope and fallback limitations. This maps source spellings, not external prose
  or native repr/messages. Old STL10 results remain unchanged. No public upload,
  new dataset or model-weight download; no observed regressions. Rollback removes
  additive mode/catalog/console/examples only. Final docs are included in rebuilt
  artifacts and verified again before delivery.

> **Agent instruction:** Append concise verified session summaries beneath this marker after each meaningful change. If this file becomes too large, propose an ADR to move historical entries to `docs/project-log.md` while preserving a short index here. Do not silently remove past decisions, completed task evidence, or known failures.

- **2026-10-15 — URD-030 started: public source repository.** Maintainer asks to
  push this project publicly and selects the local GitHub account Optimizer077.
  Starting Git state: empty main branch, no commits and no remotes. Baseline:
  `python -X utf8 -m unittest discover -s tests -q` -> PASS 162, zero skips;
  `python -X utf8 examples/verify_examples.py` -> PASS five pairs, on Python
  3.13.13 / Windows. Scope: inventory and initial source commit, create public
  Optimizer077/urdupy, push main, verify remote visibility and commit identity,
  update clone instructions and publication evidence. No conflicting active
  file owner. Reviewed 128 candidate files (747,021 bytes); no secret-pattern
  findings or credential filenames, and no file exceeds 1 MB. Existing ignore
  rules exclude environments, datasets, checkpoints, run output and build files.
  No source/API/grammar changes or new tests are needed for this publication.
  Rollback for documentation is a focused revert; removing public access is a
  separate maintainer decision. This authorizes GitHub source publication only;
  PyPI, release creation and native-speaker acceptance remain separate gates.

- **2026-10-15 — URD-030 completed.** Created the public repository
  https://github.com/Optimizer077/urdupy and pushed all 128 reviewed source files
  as main commit 841399b5ad6f39350ca1d16bcd9270e617e37539. Git origin points to
  that HTTPS repository and main tracks origin/main. Anonymous GitHub API reads
  confirm public visibility, README availability and matching remote commit;
  `git ls-remote --heads origin main` independently matches local HEAD.
  A fresh anonymous clone also passes all 162 core tests and five example pairs;
  its disposable checkout is ignored under .verification. The first hosted CI
  run 38685274655 is in progress, not a claimed pass. Updated
  README clone instructions, tracker, compatibility matrix and implementation
  handoff. Baseline remains 162 core tests and five paired examples PASS; no
  implementation changes or observed regressions. Datasets, checkpoints,
  environments, generated run/build output and credentials were not uploaded.
  No PyPI package, release or tag was published. Next safe step is to inspect
  the hosted CI result; remaining PyPI/name/community gates stay explicit.

- **2026-10-15 — Documentation/diagram pass (docs only).** User asked for a
  review, a block diagram, guidance on linking torch and other libraries, proper
  docs and a more visual README. Baseline before edits: 162/162 core tests and 5/5
  example pairs on 3.13.13. Added docs/architecture.md, docs/python-libraries.md,
  docs/README.md, two SVG assets (rendered in headless Edge and inspected), and
  rewrote README.md while keeping its status claims. MANIFEST.in also ships docs
  SVGs. Every Urdu sample in the new docs ran: README/guide torch snippets in
  .venv-ai (torch 2.14.1+cpu), and the hero example matches its Python twin. An
  Urdu-named module/package layout (حساب.urdu, اوزار/__init__.urdu) ran via CLI,
  check and Python install_importer on Windows. Relative links/anchors checked.
  No code, grammar, dependency or tracker-status changes; dist artifacts not rebuilt.

- **2026-10-15 — URD-029 started.** User requests a pip package with automatic
  dependency installation, then asks to install UrduPy using pip. Fresh baseline
  before changes passes159 core tests (2.626s). Add standard optional-dependencies
  metadata for science and complete AI examples; preserve zero-dependency core
  and existing distribution/import/CLI identity. Update artifact metadata checks
  to distinguish extra-scoped requirements from unconditional dependencies;
  document pip commands and explicit CPU/CUDA wheel choice. Build wheel/sdist,
  install/verify core in clean environments and actually install .[ai] into the
  existing local GPU environment without replacing its matching CUDA wheels.
  Add packaging metadata regression checks and ADR. No publishing, import-time
  installers, custom setup hooks or system Python modifications. Scope is
  pyproject/build verification/tests/docs/tracker; no grammar/model changes.
  Rollback removes optional metadata/docs/checks and reinstalls previous local
  wheel as needed. No other agent owns these files.

- **2026-10-15 — URD-028 started.** User explicitly requests Urdu ResNet,
  Urdu class names/directories, actual STL-10 training and Urdu plots. Baseline:
  `python -X utf8 -m unittest discover -s tests -q` -> PASS 159, zero skips.
  Scope is `experiments/ریسنیٹ_ایس_ٹی_ایل۱۰/` plus tracker/docs/ignore rules;
  compiler/runtime/package dependencies remain unchanged. Separate agent scopes:
  model + model tests; official data download + data tests; Urdu plotting module.
  Integrator owns training, integration, final checks and tracker. Verified host:
  Core Ultra 7 265F, 20 CPU cores, 64 GiB RAM, 600 GB free workspace; current
  torch is CPU-only. Plan: ResNet-18 block arrangement [2,2,2,2], width16 and
  48-pixel inputs for a practical CPU run; configurable full width/resolution.
  Fit4000/validation1000 stratified from official labeled5000; original test8000
  evaluated after validation-only checkpoint selection. Train a fixed20epochs;
  retain actual timing/metrics and clearly disclose reduced-width/resolution.
  Official dataset download is explicitly part of this real-data task, never
  routine tests. Tests use local synthetic fixtures only. Install RTL shaping
  helpers only in .venv-ai. Rollback removes only this new experiment and its
  tracked documentation; downloaded data/checkpoints are local ignored outputs.

- **2026-10-15 — URD-027 started, integrator.** User asks to train a neural
  network. Fresh baseline: `python -X utf8 -m unittest discover -s tests -q`
  passes 159 tests, zero skips. Scope: a paired Urdu/Python CPU XOR training
  example, optional learning/checkpoint tests, local saved model/metrics and
  documentation. No other agent owns these new files. Preserve compiler,
  grammar, dependency metadata and existing one-step analytic fixture. Plan:
  train a seeded 2-16-16-1 MLP with Adam for 600 full-batch epochs on 2,048
  synthetic samples; evaluate once on 1,024 separately generated test samples;
  save weights/metrics and verify reload predictions. Acceptance: substantial
  loss decrease, at least 97% held-out accuracy, all four Boolean XOR answers,
  exact reload and Urdu/Python agreement. Test data does not choose stopping
  time or optimizer settings. Rollback removes only the new example/tests/docs
  and locally generated run directory. Optional tests stay outside core discovery.

- **2026-10-15 — URD-028 hardware refinement before training.** Direct GPU
  inventory found RTX5060Ti16GiB/driver591.74 despite the existing CPU-only
  PyTorch build. Created separate .venv-resnet with official torch2.14.1+cu130
  and matching torchvision0.29.1+cu130; real CUDA matrix multiplication passed
  and sm120 is supported. The final fixed schedule is now50epochs, width64,
  native96x96, batch64 with mixed precision; CPU defaults remain an optional
  smaller configuration. No test outcomes selected these settings. Labeled
  official files individually passed all four upstream MD5 checks; unused
  unlabeled archive tail is unnecessary and explicitly unverified.

- **2026-10-14 — Charter created.** The initial handbook defines Urdu naming and beginner grammar rules, compatibility principles, AI library priorities, risks, work tracking, verification requirements, and release gates. It does **not** claim these features are implemented.

- **2026-10-15 — Phase 1 baseline / URD-001.** Created `urdupy/` as a new project;
  no previous implementation or tests were present. The parent workspace is not a
  Git repository. Initial test discovery accidentally ran in the parent and failed
  resolving an unrelated namespace; rerun inside the new project reported 0 tests,
  `NO TESTS RAN` (exit 1), not feature verification. Observed CPython 3.13.13
  (Anaconda), CPython 3.11.9 via `py -3.11`, AMD64, Windows build 26200.
  Assigned separate language, compiler-proof and research file scopes; integrator
  owns the registry and tracker. See `docs/phase-1.md` for scope and rollback.

- **2026-10-15 — Phase 1 / M0 completed, URD-001..004.** Three agents delivered
  language/naming/function design, a bounded translator proof and official platform/
  package research; integrator reviewed and ran final validation. Both
  `python -X utf8 -m unittest discover -s tests -v` (3.13.13) and
  `py -3.11 -X utf8 -m unittest discover -s tests -v` (3.11.9) passed **57/57**,
  zero skips. Both example verifier commands passed **5/5** paired programs;
  both research probes exited 0. Review corrected a relative-import gap and a
  reference-verifier future-annotations mismatch. Guide spellings are retained;
  controversial names remain provisional. No production runner/importer/CLI,
  original-column diagnostics, AI compatibility, installable metadata or release
  is claimed. Next: Phase 2 / M1 URD-005, then URD-006/007. Full evidence, risk
  boundaries and rollback are in `docs/handoff.md`; original attachment unchanged.

- **2026-10-15 — Continuous implementation / M1-M6 local gates.** Maintainer
  requested all remaining phases without stopping. Compiler, runtime, imports,
  CLI, multiline REPL, real CPU scientific/AI integrations, docs/editor assets,
  metadata/manifest/CI and a 1.0-local technical contract were implemented by
  separate agents and reviewed. Integrator independently ran 158/158 core tests
  on CPython 3.12.13, 3.13.13, 3.14.6 and stable 3.15.0; zero skips. Isolated AI
  suite passed 9/9, zero skips, with saved exact versions. Review repairs cover
  native debug-label newline/comments, one-snapshot loading, LF-only source
  caches, cross-console filenames and worker-thread execution. Local isolated
  wheel/sdist build succeeded; clean installation gate is currently running.
  External hosted CI/publication/name ownership/community gates stay explicit.

- **2026-10-15 — Final local release gate / URD-021.** Isolated setuptools build
  produced the wheel and sdist. Clean wheel installs on 3.12.13, 3.13.13, 3.14.6
  and stable 3.15.0 each passed all 158 core tests, pip check, no-science-library
  assertions and installed run/check/translate/repl commands outside the checkout.
  A separate clean sdist build/install on 3.15.0 passed the same checks. Base .venv
  now provides a ready-to-run local wheel installation. Artifact hashes/reports
  stay in dist; final documentation refresh is followed by changed-sdist recheck.
  All local engineering phases are complete. URD-020/022/024 retain only external
  ownership, hosted-run and explicit-publication gates; no pass/publication is
  fabricated. Current report: docs/implementation-handoff.md.

- **2026-10-15 — Final ownership repair before artifact freeze.** A fresh-process
  regression found anonymous execution could remove an existing module-cache
  entry when its private temporary name collided. The runtime now restores the
  previous owned value. The core suite is 159 tests (15 runtime), with actual
  installed-package selection enforced in that subprocess regression. Final wheel
  and sdist are rebuilt and clean verification is rerun against the new bytes;
  the earlier 158-test checkpoint above remains historical evidence.

- **2026-10-15 — URD-027 completed.** Trained the new paired `train_xor.urdu` /
  `.py` 337-parameter MLP on CPU: 600 epochs, 2,048 synthetic training samples,
  1,024 independent held-out samples. Training loss 0.703598 -> 0.002585;
  test correct 1,021/1,024 (99.71%); all four representative XOR labels correct.
  `runs/xor/model.pt` and `metrics.json` save tensors, configuration, history,
  metrics and hashes. Reloaded test logits match exactly, including separate
  fresh-process inference. No test-based tuning occurred. Added two optional
  tests for learning, Python weight/metric equality, labels/split independence,
  RNG/thread restoration, checkpoint roundtrip and epoch validation. Exact
  commands: `.venv-ai/Scripts/python.exe -X utf8 -m urdupy run
  examples/science/train_xor.urdu -- --output runs/xor` -> PASS;
  `.venv-ai/Scripts/python.exe -X utf8 -m unittest
  tests.compatibility.compat_training -v` -> PASS 2/2;
  `.venv-ai/Scripts/python.exe -u -X utf8 tools/run_compatibility.py
  --require-all --report tests/compatibility/results-training.json` -> PASS
  11/11, zero skips; `python -X utf8 -m unittest discover -s tests -q` ->
  PASS 159/159, zero skips; `python examples/verify_examples.py` -> PASS 5 pairs;
  `.venv/Scripts/python.exe -X utf8 -m urdupy check
  examples/science/train_xor.urdu` -> PASS without science dependencies.
  Python 3.13.13, torch 2.14.1+cpu, Windows AMD64; full optional tuple in report.
  Updated example/root README, AI compatibility, handoff and changelog. Grammar,
  runtime and base dependencies unchanged; no regressions observed in run checks.
  Existing dist artifacts predate the example and were not rebuilt. Further
  real-data training is a separate task; source changes are complete and locally
  reviewed. Rollback is limited to the URD-027 files/docs and ignored run output.

- **2026-10-15 — URD-028 completed.** User's actual STL-10 ResNet request is
  fulfilled in `experiments/ریسنیٹ_ایس_ٹی_ایل۱۰/`. Three agents implemented and
  reviewed Urdu model/data/plot scopes; integrator trained and independently
  audited actual artifacts. Classes: بنیادی_بلاک، ریس_نیٹ، تصویری_مجموعہ.
  Full-width ResNet18 [2,2,2,2] with small-image3x3 stem, 11,173,962 parameters,
  native96x96; 50epochs scratch GPU training completed in1432.159s. Selected
  earliest best validation epoch44 (77.0%); final official test77.35%,
  6188/8000, loss0.756060546875. Split4000fit/1000val/8000test, train-only
  normalization and augmentation; no ten-fold benchmark/pretrained claim.
  Command `.venv-resnet/Scripts/python.exe -u -X utf8 -m urdupy run
  experiments/ریسنیٹ_ایس_ٹی_ایل۱۰/تربیت.urdu -- --device cuda --base-width 64
  --image-size 96 --epochs 50 --batch-size 64 --threads 6` -> PASS, exit0.
  Independent `نتائج_جانچیں.urdu -- --results .../نتائج/ابتدائی_تربیت` -> PASS;
  raw4fileMD5, exact test-label order, stratified/disjoint split, all8000
  predictions, confusion/accuracy, validation selection, checkpoint/source hashes
  and4PNG/4SVG checks reconciled. All4 final PNGs visually inspected; Urdu text,
  digits, labels and units readable; SVG XML/glyph-path export checked, no separate
  SVG browser-render claim. Fresh-process saved-weight CPU inference succeeds.
  Saved weights, optimizer/history, configuration, environment, predictions,
  Urdu CSV tables, graphs and Urdu results.md-equivalent document are under
  results/ابتدائی_تربیت (actual folder name نتائج). Checkpoint max logit error0.
  `.venv-resnet/Scripts/python.exe -X utf8 -m unittest discover -s
  experiments/ریسنیٹ_ایس_ٹی_ایل۱۰ -p test_*.py -q` -> PASS22/22;
  `python -X utf8 -m unittest discover -s tests -q` -> PASS159/159;
  `.venv-ai/Scripts/python.exe -u -X utf8 tools/run_compatibility.py --require-all
  --report .../نتائج/ابتدائی_تربیت/اردوپائی_مطابقت.json` -> PASS11/11;
  all7Urdu source compile-only checks and .venv-resnet pip check -> PASS.
  Exact tuple: Python3.13.13, torch2.14.1+cu130, torchvision0.29.1+cu130,
  CUDA13.0/cuDNN9.24, RTX5060Ti16GB/driver591.74, WindowsAMD64; data/plot
  package versions in ماحول.json. Earlier CPU environment remains unchanged.
  Tiny synthetic channels-last CPU fixture initially stalled in oneDNN backward;
  restoring test-only native backend resolved it. Inference resize mismatch was
  repaired/tested without modifying active training source. No regressions found
  in applicable checks. Core/runtime/grammar/dependency metadata unchanged;
  prior wheel/sdist not rebuilt. Automatic approval review rejected recursive
  incomplete-download cleanup with `blocked by policy`; stopped unused fragments
  remain ignored in singular experiment/ and dataset/حصے (actual dataset folder
  ڈیٹاسیٹ). Only the four checksum-verified labeled files train/evaluate; full
  archive and unlabeled use explicitly false. Reproduction and safe continuation:
  experiment README; source changes need baseline/review, and future training uses
  a new output directory. No publication or further user action is required for
  the requested completed experiment.

- **2026-10-15 — URD-029 completed.** Added pip science/ai optional dependencies,
  ADR-014, documentation and3metadata regression tests. Core remains dependency-free
  and grammar/runtime unchanged. Fresh baseline159 -> final162tests. Built wheel/
  source archive under dist/pip-extras with isolated setuptools84/build1.6.1.
  `tools/verify_release.py` now distinguishes extra-scoped Requires-Dist from
  active base dependencies. Actual clean wheel installs on3.12.13/3.13.13/3.14.6/
  3.15.0 and separate3.15source install pass162tests each, pip check, no-science
  assertions and installed CLI run/check/translate/repl outside checkout imports.
  `.venv-resnet/Scripts/python.exe -m pip install ".[ai]" --report
  dist/pip-ai-install.json` succeeded, automatically installed missing dependencies,
  retained torch2.14.1+cu130/torchvision0.29.1+cu130, and CUDA remains available.
  Installed import path points to local site-packages; console--version/pip check
  pass. Full optional suite11/11 passes there, saved dist/pip-extras/ai-compatibility.json.
  Clean .venv-science-install wheel[science] install auto-resolved NumPy2.5.4,
  Pillow12.3.0 and OpenCV-headless5.0.0.93; imports/pip check pass, torch absent;
  report dist/pip-extras/pip-science-install.json. Updated .venv core via explicit
  same-version wheel reinstall; it advertises science/ai extras. Source/docs
  refreshed before final artifact build/recheck so hashes identify delivered bytes.
  Pip owns installation; no setup hooks, arbitrary import installers, drivers,
  datasets/weights, system package changes or public upload. All relevant checks
  passed; no observed regressions. Other platform/framework-wheel tuples remain
  unverified. User can invoke installed .venv-resnet/Scripts/urdupy.exe or install
  from this checkout with python -m pip install .[ai]. Public name/ownership and
  publication gates are unchanged. Rollback is optional metadata/docs and local
  package reinstall; historical artifacts in dist stay separate from pip-extras.
