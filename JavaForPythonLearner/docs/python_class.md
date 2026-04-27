文字列・表示系

__repr__    # repr(a), print(a)  ← Fraction で実装済み
__str__     # str(a)  (__repr__ と分けたいとき)
__format__  # f"{a:.2f}" のフォーマット指定
比較演算子

__lt__   # a < b   ← Fraction で実装済み
__le__   # a <= b
__eq__   # a == b
__ne__   # a != b
__gt__   # a > b
__ge__   # a >= b
算術演算子

__add__   # a + b  ← Fraction で実装済み
__radd__  # 2 + a  ← Fraction で実装済み
__sub__   # a - b
__mul__   # a * b
__truediv__ # a / b
__mod__   # a % b
組み込み関数に反応

__len__   # len(a)
__bool__  # bool(a), if a:
__abs__   # abs(a)
__int__   # int(a)
__float__ # float(a)
コレクション的な振る舞い

__getitem__  # a[0], a["key"]
__setitem__  # a[0] = 1
__contains__ # x in a
__iter__     # for x in a:
__next__     # イテレータの次の値
オブジェクトのライフサイクル

__init__   # Fraction(1, 3) ← Fraction で実装済み
__del__    # オブジェクトが削除されるとき
__new__    # インスタンス生成の前処理
with 文

__enter__  # with a as x:  の入り口
__exit__   # with ブロックを抜けるとき（例外処理も含む）
ファイル操作の with open(...) as f: はこの仕組みで動いています。



from fraction import Fraction

a = Fraction(1, 3)   # 1/3
b = Fraction(1, 2)   # 1/2
c = Fraction(7, 3)   # 7/3 = 2と1/3

# __repr__  ← print() が自動で呼ぶ
print(a)        # → "1/3"
print(c)        # → "2 1/3"  (仮分数 → 帯分数)
repr(a)         # → "1/3"

# __add__  ← + の左側が Fraction のとき
a + b           # → Fraction.__add__(a, b)  → 5/6

# __radd__  ← + の左側が int/float のとき
2 + a           # → int.__add__ 失敗 → Fraction.__radd__(a, 2)
sum([a, b])     # → 0 + a → __radd__ が呼ばれる ← これが主な用途

# __lt__  ← < 演算子
a < b           # → Fraction.__lt__(a, b)  → True (1/3 < 1/2)
b < a           # → False

# sorted や min/max も __lt__ を使う
sorted([c, a, b])   # → [a, b, c]  (1/3, 1/2, 7/3)
min(a, b)           # → a (1/3)
呼び出しの流れを図にすると:


書いたコード         Pythonが内部でやること
─────────────────────────────────────────
print(a)      →  a.__repr__()
a + b         →  a.__add__(b)
2 + a         →  (int失敗) → a.__radd__(2)
a < b         →  a.__lt__(b)
sorted([...]) →  要素間で __lt__ を繰り返し呼ぶ
sum([a, b])   →  0.__add__(a) 失敗 → a.__radd__(0) → ...
sum() と sorted() が dunder 経由で動くのが特に実用的なポイントです