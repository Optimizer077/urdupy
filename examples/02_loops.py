# 3 چھوڑ دیں، 4 کے بعد لوپ روک دیں
رکھے = []
for عدد in range(1, 7):
    if عدد == 3:
        continue
    if عدد > 4:
        break
    رکھے.append(عدد)

مربع = [عدد * عدد for عدد in range(1, 4)]
باقی = 3
الٹی_گنتی = []
while باقی > 0:
    الٹی_گنتی.append(باقی)
    باقی -= 1

RESULT = {"kept": رکھے, "sum": sum(رکھے), "squares": مربع, "countdown": الٹی_گنتی}
print(رکھے, sum(رکھے))
print(مربع, الٹی_گنتی)
