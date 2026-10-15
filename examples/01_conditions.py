# شرط، برابر قدریں، ایک ہی شے، اور غیر موجود قدر
عمر = 20
if عمر >= 18:
    درجہ = "بالغ"
elif عمر >= 13:
    درجہ = "نوجوان"
else:
    درجہ = "بچہ"

الف = []
ب = []
ج = الف
جواب = None
RESULT = {
    "category": درجہ,
    "equal_values": الف == ب,
    "same_distinct": الف is ب,
    "same_alias": الف is ج,
    "missing": جواب is None,
    "empty_is_missing": الف is None,
    "booleans": [True, False],
    "logic": True and not False,
}
print(درجہ)
print(RESULT["equal_values"], RESULT["same_distinct"], RESULT["same_alias"])
