# Write your first UrduPy program

UrduPy uses Urdu words with Python's block and expression rules. Save the source
as UTF-8 in `lesson.urdu`, then run `python -m urdupy run lesson.urdu`.
No special `main()` function is required. See [installation](install.md) first.

## Values and output

```urdu
نام = "علی"
قیمت = 50
تعداد = 3
دکھاؤ("سلام", نام)
دکھاؤ(قیمت * تعداد)
```

`دکھاؤ` سکرین پر قدر لکھتا ہے۔ `نام`، `قیمت` اور `تعداد` متغیر کے نام ہیں۔
نام اردو یا انگریزی میں ہو سکتے ہیں۔ متن کو quotation marks میں لکھیں۔

This prints a greeting and `150`. Use ASCII digits `0-9`, quotes, commas,
parentheses and operators for code. Urdu punctuation is welcome inside text.
`دکھاؤ` is the real Python `print` object under another name.

## Choose a branch

```urdu
عمر = 20
اگر عمر >= 18:
    دکھاؤ("بالغ")
ورنہ:
    دکھاؤ("کم عمر")
```

`اگر` شرط جانچتا ہے؛ `ورنہ` دوسرا راستہ ہے۔ colon `:` کے بعد بلاک کی سطریں
چار spaces آگے لکھیں۔ اسی بلاک کی سطروں کا فاصلہ برابر رکھیں۔

The English equivalent uses `if` and `else` with the same indentation. Add
`ورنہ_اگر` for another condition. There is no extra word for “then” and no
block-ending word. `سچ`/`جھوٹ` mean `True`/`False`; `اور`, `یا`, `نہیں` mean
`and`, `or`, `not`. The two conjunctions retain Python's short-circuit behavior.

## Repeat work

```urdu
کل = 0
ہر عدد میں حد(1, 5):
    کل += عدد
دکھاؤ(کل)

باقی = 3
جب_تک باقی > 0:
    دکھاؤ(باقی)
    باقی -= 1
```

`ہر عدد میں ...` ہر قدر باری باری لیتا ہے۔ `حد(1, 5)` میں 1، 2، 3، 4 ہیں؛
آخری حد شامل نہیں۔ `جب_تک` بلاک کو اس وقت تک دہراتا ہے جب شرط سچ ہو۔

The first result is `10`. `روکو` ends the innermost loop. `جاری` starts its next
iteration. `گزر` performs no operation and is useful for a placeholder body.
`جب_تک` means **while true**, not “stop when this becomes true.”

## Define a function and return a value

```urdu
فنکشن مربع(عدد):
    واپس عدد * عدد

جواب = مربع(4)
دکھاؤ(جواب)
```

`فنکشن` کام کا نام اور دی جانے والی قدروں کے نام بتاتا ہے۔ `واپس` جواب بلانے
والے کو دیتا ہے۔ `دکھاؤ` صرف آؤٹ پٹ لکھتا ہے؛ یہ `واپس` کا بدل نہیں۔

A function body runs when called. With no explicit return value, it returns
`None`, written `کچھ_نہیں` in UrduPy. `None` is an absence marker; an empty list
is still a list. `جھوٹ` is the Boolean false value. These are separate objects.

`==` compares values. `ہے` compares whether two references point to the **same
object**. Two separately created `[1]` lists compare equal but are not the same
object. Use `ہے کچھ_نہیں` to check a None sentinel:

```urdu
فنکشن شامل_کرو(عدد, اعداد=کچھ_نہیں):
    اگر اعداد ہے کچھ_نہیں:
        اعداد = []
    اعداد.append(عدد)
    واپس اعداد

دکھاؤ(شامل_کرو(1), شامل_کرو(2))
```

Defaults are evaluated when the definition runs. The None pattern gives separate
lists on separate calls; a mutable `اعداد=[]` default would be shared.

## Use Python libraries as they are

```urdu
درآمد math
سے statistics درآمد mean بطور اوسط

فنکشن جڑ(عدد):
    واپس math.sqrt(عدد)

دکھاؤ(جڑ(81), اوسط([2, 4, 6]))
```

`درآمد` means `import`, `سے` means `from`, and `بطور` means `as`.
Keep package/API names such as `math.sqrt`, `numpy.array`, `torch.nn.Linear`
and `model.state_dict` in their actual spelling. UrduPy does not translate or
replace those libraries. Optional scientific packages need a separate environment;
the [compatibility record](ai-compatibility.md) reports actual runs.

## Functions with richer signatures

```urdu
فنکشن بل(قیمت, /, تعداد=1, *, رعایت=0):
    واپس قیمت * تعداد - رعایت

دکھاؤ(بل(100, تعداد=2, رعایت=10))
```

This returns `190`. Parameters before `/` are positional-only; parameters after
a bare `*` are keyword-only. `*اضافی` collects extra positional arguments and
`**تفصیل` collects extra named arguments. Calls use the usual `*items`/`**options`
unpacking. Python raises the same missing/duplicate/unexpected argument errors.
Annotations such as `عدد: int` describe an interface; they do not add automatic
type checking. Decorators retain `@` and their original callable names.

## Classes and protocol names

```urdu
کلاس ٹوکری:
    فنکشن __init__(self, اشیا):
        self.اشیا = list(اشیا)

    فنکشن __len__(self):
        واپس len(self.اشیا)

چیزیں = ٹوکری(["قلم", "کتاب"])
دکھاؤ(len(چیزیں))
```

These are real Python classes and instances. Keep `__init__`, `__len__`,
`__iter__` and framework names such as `forward` unchanged. `self` is a parameter
convention, not a special UrduPy keyword.

## Read code comfortably

Use a font that displays Urdu, visible whitespace and a left-to-right code
layout. Mixed Urdu/English glyph order can differ from logical character order;
test cursor movement, selection and copy/paste in your editor. Do not insert
invisible direction-control characters to rearrange source. Editor rendering and
terminal font support are not proven by successful UTF-8 compilation.

Canonical spellings use `ک` U+06A9 and `ی` U+06CC where present. Arabic lookalikes
`ك` U+0643 and `ي` U+064A are different characters and are not automatically
corrected. Use underscores inside multiword keywords: `ورنہ_اگر` is one token,
while `ورنہ اگر` is two. Strings/comments retain their own text.

See [language reference](language-reference.md) for the complete vocabulary,
advanced functions, f-strings, imports and collision rules;
[CLI](cli.md) for checking/translation/REPL; and
[local editor highlighting](../editor/README.md) for a small optional aid.
