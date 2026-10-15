# /، *args، keyword-only، **kwargs اور واپس بمقابلہ آؤٹ پٹ
def بل(قیمت: int, /, تعداد: int = 1, *اضافی: int,
       رعایت: int = 0, **تفصیل: str) -> dict:
    کل = قیمت * تعداد + sum(اضافی) - رعایت
    return {"amount": کل, "label": تفصیل.get("نام", "عام")}

def سلام(نام, *, سابقہ="سلام"):
    return سابقہ + " " + نام

def شامل_کرو(عدد, اعداد=None):
    if اعداد is None:
        اعداد = []
    اعداد.append(عدد)
    return اعداد

def صرف_دکھاؤ(پیغام):
    print(پیغام)

def عارضی():
    pass

بل_نتیجہ = بل(100, 2, 5, رعایت=10, نام="کتاب")
ڈیفالٹ = بل(100)
پہلی = شامل_کرو(1)
دوسری = شامل_کرو(2)
آؤٹ_پٹ_کا_جواب = صرف_دکھاؤ("کام مکمل")

try:
    بل(قیمت=100)
except TypeError:
    جگہ_کی_غلطی = "TypeError"
else:
    جگہ_کی_غلطی = "missing error"

try:
    سلام("سارہ", "محترمہ")
except TypeError:
    نام_کی_غلطی = "TypeError"
else:
    نام_کی_غلطی = "missing error"

RESULT = {
    "bill": بل_نتیجہ,
    "default": ڈیفالٹ,
    "unpacked": بل(*[50, 2], **{"رعایت": 5}),
    "greeting": سلام("سارہ", سابقہ="خوش آمدید"),
    "fresh_lists": [پہلی, دوسری],
    "output_returns_none": آؤٹ_پٹ_کا_جواب is None,
    "pass_returns_none": عارضی() is None,
    "argument_errors": [جگہ_کی_غلطی, نام_کی_غلطی],
}
print(بل_نتیجہ["amount"], بل_نتیجہ["label"])
print(RESULT["greeting"])
