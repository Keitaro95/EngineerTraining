import re

text = "お問い合わせは 03-134-578 までご連絡ください。"

# 数字0~9で2~4桁-数字0~9で2~4桁-数字0~9で3~4桁
pattern = r"\d{2,4}-\d{2,4}-\d{3,4}"

# 全ての一致をリストで返す
result = re.findall(pattern, text)
print(result)



text1 = "担当者一覧: suzuki@example.com tanaka@abc.co.jp"


# [a-zA-Z0-9._%+-]+ 
# [...]	文字クラス（いずれか1文字）
# a-zA-Z0-9	英数字
# ._%+-	使用可能な記号
# +	1文字以上
# [a-zA-Z0-9.-]：英数字・ドット・ハイフン
# .ドットそのもの
# a~zなどから2文字
pattern1 = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"


emails = re.findall(pattern1, text1)
print(emails)