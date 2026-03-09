このコードを日本語で解説します。

## やっていること

`job_groups` というリストを、**各グループ内の `llm_score` の最大値**を基準に**降順（大きい順）**に並び替えています。

---

## 分解して理解する

### 全体構造
```python
job_groups = sorted(job_groups, key=..., reverse=True)
```
- `sorted()` でリストを並び替えて、結果を `job_groups` に再代入
- `reverse=True` → 降順（大きい順）

---

### `key=lambda jg: ...` の部分

```python
key=lambda jg: max(
    (float(c.get('llm_score', 0) or 0) for c in jg.get('candidates', [])),
    default=0.0
)
```

`key` は「何を基準に並び替えるか」を決める関数。  
各 `jg`（job_group）に対して、**その中の candidates の llm_score の最大値**を返す。

---

### 内側のジェネレータ式

```python
float(c.get('llm_score', 0) or 0) for c in jg.get('candidates', [])
```

| コード | 意味 |
|---|---|
| `jg.get('candidates', [])` | candidates キーがなければ空リスト `[]` を使う |
| `c.get('llm_score', 0)` | llm_score キーがなければ `0` を使う |
| `or 0` | `None` や `""` など falsy な値も `0` に変換 |
| `float(...)` | 文字列など数値以外の型も浮動小数点数に変換 |

---

### `max(..., default=0.0)`

```python
max(..., default=0.0)
```
candidates が空リストの場合、`max()` はエラーになる。  
→ `default=0.0` で、空のときは `0.0` を返すように保険をかけている。

---

## まとめ図

```
job_groups = [
  { candidates: [{llm_score: 0.9}, {llm_score: 0.5}] },  # max → 0.9
  { candidates: [{llm_score: 0.3}] },                      # max → 0.3
  { candidates: [] },                                       # max → 0.0 (default)
]

並び替え後 → [0.9のグループ, 0.3のグループ, 0.0のグループ]
```