@tailwindcss/vite は .mjs (ESM専用) で配布されています
デフォルトでは Vite が CJS モードで起動し、require() で設定ファイルを読み込もうとします
CJS の require() は ESM の .mjs ファイルを読み込めないため、エラーが発生しています



githubサンプルから読み下しましょう
https://tanstack.com/query/latest/docs/framework/react/examples/nextjs

useQueryのプロパティには、取得状態を観測できるものがたくさんあるよ。

isErrorはエラーかどうかを見ているよ。
statusそのものをとってきてもいいよ。これを条件判定できる。

const { isPending, status, isError, data, error } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodoList,
  })

if (isPending) {
    return ...
}
または
if (status === 'pending) {

}

if (isError) {
    return ...
}
または
if (status === 'error')

---

## クエリキーと URL の対応例

### 1. 個別リソース `/todos/5`
```tsx
useQuery({
  queryKey: ['todo', 5],
  queryFn: () =>
    fetch('https://jsonplaceholder.typicode.com/todos/5').then(r => r.json()),
})
```

### 2. 個別リソース + オプション `/todos/5?preview=true`
```tsx
useQuery({
  queryKey: ['todo', 5, { preview: true }],
  queryFn: () =>
    fetch('https://jsonplaceholder.typicode.com/todos/5?preview=true').then(r => r.json()),
})
```

### 3. リスト + フィルタ `/todos?completed=true`
```tsx
useQuery({
  queryKey: ['todos', { type: 'done' }],
  queryFn: () =>
    fetch('https://jsonplaceholder.typicode.com/todos?completed=true').then(r => r.json()),
})
```

### 4. オブジェクトはキー順序不問（すべて同一キャッシュ）
```tsx
// この3つはすべて同じキャッシュを参照する
useQuery({ queryKey: ['todos', { status, page }], queryFn: fetchTodos })
useQuery({ queryKey: ['todos', { page, status }], queryFn: fetchTodos })               // 順序違い → 同一
useQuery({ queryKey: ['todos', { page, status, other: undefined }], queryFn: fetchTodos }) // → 同一
```

### 5. 配列の順序は順番に読み込まれる
```tsx
useQuery({ queryKey: ['todos', 'active', 2], queryFn: fetchTodos }) // ← 別キー
useQuery({ queryKey: ['todos', 2, 'active'], queryFn: fetchTodos }) // ← 別キー（順序が違う）
```

ポイント: オブジェクト内のキーは順不同でOK、でも**配列の要素の順番は厳密に一致**させる必要があります。
