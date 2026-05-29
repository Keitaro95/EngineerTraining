
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



a[bcd]*b

'a' そのものにマッチ
[bcd]* bかcかd の0個以上にマッチ
'b' そのものにマッチ

に対して 'abcbd' を考えてみよう
'abcbd'

1. 正規表現'a'が先頭にマッチ→aまで進む
2. [bcd]*→終端まで進む
3. 正規表現'b'は終端以降にない→バックトラック
4. abcbまで戻る。現在１b
5. もう一度正規表現'b'とマッチさせようとする




https://userweb.mnet.ne.jp/nakama/#google_vignette




```
import re
p = re.compile('ab*')
```

\section　をマッチさせたい
↓
\\section と書けばいい
↓
だけどpythonだから "\\\section" と書かないといけない
これが嫌だから "\\section" と書く
↓
r"\\section"




https://docs.python.org/ja/3/howto/regex.html#regex-howto
https://docs.python.org/ja/3/library/re.html




