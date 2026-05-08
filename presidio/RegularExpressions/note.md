
# 正規表現

a,b,またはcのどの文字にもマッチ
[abc]
[a-c]

a-zの小文字アルファベットにマッチ
[a-z]

'5'以外の文字にマッチ
[^5]

任意の英数字文字
\w は [a-zA-Z0-9_] と同じ意味
↓大文字にするとそれ以外
\W　は [^a-zA-Z0-9_]

\d　は　[0-9] と同じ意味

\D　は [^0-9] と同じ意味


## greedy パターン

ca*t は
'ct'
'cat'
'caaat'にマッチ
https://docs.python.org/ja/3/howto/regex.html#regex-howto
https://docs.python.org/ja/3/library/re.html




