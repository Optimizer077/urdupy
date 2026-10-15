# بیرونی API کے اصل نام برقرار رہتے ہیں
import math as ریاضی
from statistics import mean as اوسط
from collections import Counter

اعداد = [2, 4, 6]
حروف = Counter("aba")
RESULT = {
    "root": ریاضی.sqrt(81),
    "mean": اوسط(اعداد),
    "counts": dict(حروف),
    "length": len(اعداد),
}
print(RESULT["root"], RESULT["mean"])
print(RESULT["counts"], RESULT["length"])
