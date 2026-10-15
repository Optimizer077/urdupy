# Python کے protocol نام اور decorators اپنی اصل شکل میں
class ٹوکری:
    def __init__(self, اشیا=None):
        self.اشیا = [] if اشیا is None else list(اشیا)

    def __len__(self):
        return len(self.اشیا)

    def __iter__(self):
        return iter(self.اشیا)

    @classmethod
    def بناؤ(cls, *اشیا):
        return cls(اشیا)

    @staticmethod
    def موزوں(عدد):
        return عدد >= 0

    @property
    def تعداد(self):
        return len(self.اشیا)

چیزیں = ٹوکری.بناؤ("کتاب", "قلم")
RESULT = {
    "items": list(چیزیں),
    "length": len(چیزیں),
    "property": چیزیں.تعداد,
    "valid": ٹوکری.موزوں(3),
    "empty_length": len(ٹوکری()),
    "instance": isinstance(چیزیں, ٹوکری),
}
print(RESULT["items"], RESULT["length"])
print(RESULT["valid"], RESULT["instance"])
