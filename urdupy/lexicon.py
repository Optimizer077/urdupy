"""Single experimental spelling registry, separate from ordinary built-in aliases.

CORE means retained from the guide, not a stable-language guarantee. REVIEW and
FUTURE entries have no native-speaker acceptance evidence. Changing a spelling
requires a naming proposal and an explicit migration decision.
"""

from types import MappingProxyType

# (Urdu spelling, Python counterpart, design-review status)
_KEYWORD_ROWS = (
    ("اگر", "if", "CORE"),
    ("ورنہ_اگر", "elif", "CORE"),
    ("ورنہ", "else", "CORE"),
    ("ہر", "for", "CORE"),
    ("میں", "in", "CORE"),
    ("جب_تک", "while", "CORE"),
    ("اور", "and", "CORE"),
    ("یا", "or", "CORE"),
    ("نہیں", "not", "CORE"),
    ("سچ", "True", "CORE"),
    ("جھوٹ", "False", "CORE"),
    ("کچھ_نہیں", "None", "REVIEW"),
    ("روکو", "break", "CORE"),
    ("جاری", "continue", "CORE"),
    ("گزر", "pass", "REVIEW"),
    ("ہے", "is", "REVIEW"),
    ("فنکشن", "def", "CORE"),
    ("واپس", "return", "CORE"),
    ("کلاس", "class", "CORE"),
    ("درآمد", "import", "CORE"),
    ("سے", "from", "CORE"),
    ("بطور", "as", "CORE"),
    ("کوشش", "try", "CORE"),
    ("سوائے", "except", "CORE"),
    ("آخرکار", "finally", "CORE"),
    ("اٹھاؤ", "raise", "CORE"),
    ("ساتھ", "with", "CORE"),
    ("تصدیق", "assert", "REVIEW"),
    ("حذف", "del", "REVIEW"),
    ("عالمی", "global", "REVIEW"),
    ("غیر_مقامی", "nonlocal", "REVIEW"),
)

KEYWORDS = MappingProxyType({urdu: python for urdu, python, _ in _KEYWORD_ROWS})
KEYWORD_STATUS = MappingProxyType({urdu: status for urdu, _, status in _KEYWORD_ROWS})

# These names are documentation candidates, not active translator replacements.
# English Python constructs remain available in the experiment.
DEFERRED_KEYWORDS = MappingProxyType({
    "لامبڈا": "lambda",
    "پیدا_کرو": "yield",
    "غیر_متزامن": "async",
    "انتظار": "await",
    "منتخب": "match",
    "صورت": "case",
})

# Production language configuration. The M0 experiment keeps its original
# registry above so its explicit limitations and regression evidence remain
# reproducible. Production additions use the guide's existing candidate spellings;
# no friendly synonym is silently introduced.
PRODUCTION_KEYWORDS = MappingProxyType({
    **KEYWORDS,
    "لامبڈا": "lambda",
    "پیدا_کرو": "yield",
    "غیر_متزامن": "async",
    "انتظار": "await",
})
SOFT_KEYWORDS = MappingProxyType({"منتخب": "match", "صورت": "case"})

# Values name the actual built-in objects. These are identifiers, not keywords:
# users may shadow them using normal Python scope rules.
BUILTIN_ALIASES = MappingProxyType({
    "دکھاؤ": "print",
    "ان_پٹ": "input",
    "حد": "range",
    "لمبائی": "len",
    "فہرست": "list",
    "لغت": "dict",
    "مجموعہ": "set",
    "صحیح_عدد": "int",
    "اعشاری": "float",
    "متن": "str",
    "ترتیب": "sorted",
    "گنو": "enumerate",
    "جوڑ": "sum",
    "قسم": "type",
    "کھولو": "open",
})
