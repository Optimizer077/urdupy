# ADR-004: A small Urdu lexicon with a separate naming research track

- **Date:** 2026-10-15
- **Status:** PROPOSED; Phase 1 experimental configuration recorded, stable language acceptance pending
- **Owner:** Language design agent; integration by the project owner
- **Task:** URD-004; design portion of URD-025
- **Affected interfaces:** Keyword registry, built-in aliases, tutorial language, source compatibility

## Context

The supplied handbook proposes an Urdu vocabulary and describes a historical
prototype. This checkout started empty. We can preserve the handbook's spellings
without claiming that the historical implementation or community approval exists
here. The user asks for creative grammar and naming work and explicitly permits
deviations where justified. Creative alternatives should be compared before they
become reserved words.

## Options

1. Adopt every guide entry and every friendly synonym immediately. This offers
   choice but expands collisions, teaching costs and compiler scope before use
   has been observed.
2. Rename disputed words immediately using the agents' judgment. This may improve
   a few examples, but intuition alone cannot establish which words Urdu readers
   find clear.
3. Retain the guide's preferred spellings in a bounded experimental vocabulary,
   separate executable entries from proposals, and prepare explicit comparison
   exercises. This is the Phase 1 recommendation.

## Proposed decision

Use one spelling for each concept in experimental examples. Preserve the guide's
31 keyword mappings through `غیر_مقامی` and its 15 proposed built-in aliases.
This count describes a registry, not support for every placement of those words.
Its spelling/status metadata and actual executable scope live in
[`urdupy/lexicon.py`](../../urdupy/lexicon.py). The compiler's own exclusions take
precedence over illustrative target grammar.

Keep six named advanced candidates (`لامبڈا`, `پیدا_کرو`, `غیر_متزامن`,
`انتظار`, `منتخب`, `صورت`) outside active Urdu translation. The `type`
statement still has no selected Urdu spelling. `سوائے*` is a future contextual
syntax question; it is not a separate identifier-shaped keyword. English Python
constructs follow the experimental compiler's documented pass-through policy.

Separate **syntax** from **built-in names**. `فنکشن` changes grammar;
`دکھاؤ` is a convenience binding to `builtins.print`. The latter remains an
ordinary name that user code may shadow under the proposed runtime contract.
No global source replacement of aliases is allowed.

Retain `ان_پٹ`, `گزر`, `ہے` and `کچھ_نہیں` for the experiment. Preserve
`پیدا_کرو` and `غیر_متزامن` as reviewed candidates in the design. Compare
alternatives in [`naming-proposals.md`](../naming-proposals.md), including
`پوچھو`, `کچھ_نہ_کرو`, `وہی_شے`, `کوئی_نہیں`, `دیتے_جاؤ` and `ایسنک`.
These are research alternatives, not additional accepted syntax.

## Rationale and limits

The invariant is a readable bridge to Python: indentation, punctuation,
expression order, function parameters and real library member names retain their
Python forms. This makes comparison examples useful and keeps naming decisions
separate from runtime design. It does not establish that a word is the best Urdu
translation or that all ordinary Python source already works.

Naming judgments in this phase are **agent hypotheses**. No native-speaker
survey or beginner comprehension result has been collected. Guide labels
`CORE`, `REVIEW` and `FUTURE` describe intention/review priority; they do not
prove implementation or acceptance. The feedback worksheet is intentionally blank.

## Collision and orthography contract

- Reserve active Urdu syntax spellings for unqualified grammar use in the
  experimental mode. Use descriptive alternatives for local/parameter names.
- Preserve attributes, imported export spellings and call keyword labels where
  explicitly tested. Import a colliding export under a nonreserved local alias:
  `سے api درآمد اگر بطور شرط`.
- Keep escape hatches in ordinary Python: `getattr(obj, "اگر")` and
  `call(**{"اگر": value})`. Do not invent quoting punctuation for identifiers.
- Compare keyword spelling exactly. Never globally substitute Arabic/Urdu
  lookalike characters, remove invisible characters or rewrite string content.
  Python's own identifier normalization remains a separate semantic rule.

## Compatibility and migration plan

There is no released local version to migrate. Preserve the guide spellings as
the reference for future prototype migration; do not claim historical source
compatibility without the historical fixtures.

Any later rename must include: a specific proposal; a bounded reader exercise;
maintainer acceptance; collision tests; a language-version change; and migration
notes. If an alias transition is accepted, add an opt-in or explicitly versioned
compatibility period. Do not reserve both spellings forever by accident. A
syntax migration tool must operate on parsed code positions, not strings,
comments, attributes or imported API spellings.

## Verification and rollback

[`examples/verify_examples.py`](../../examples/verify_examples.py) checks five
Urdu/Python pairs, stdout, typed result values and function signatures using the
experimental compiler. The paired examples are evidence for those specific
programs. Actual commands/results are recorded in
[`examples/README.md`](../../examples/README.md); the integrator records the
whole-suite result centrally. No reader feedback is claimed.

Rollback is limited to the experimental registry configuration and these design
documents/examples. A future stable registry must not inherit provisional status
silently. Full compiler/import/CLI/AI milestones remain separate.
