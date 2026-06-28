https://github.com/TanStack/query/blob/main/examples/react/chat/src/index.tsx

https://tanstack.com/query/v5/docs/reference/streamedQuery


# chat

図解で説明しますね。図のポイントを補足します。

**縦方向の `flex-col`**（青の点線矢印）：外側コンテナが「タイトル → メッセージ一覧 → 入力行」を上から下に積んでいます。`h-screen` で画面いっぱい、`max-w-3xl mx-auto` で中央に配置です。

**真ん中だけスクロール**（紫の領域）：`overflow-y-auto` がついているのはメッセージ一覧だけ。だからメッセージが増えてもこの枠の中だけがスクロールし、上のタイトルや下の入力欄は画面に固定されたように見えます。`space-y-4` で吹き出し同士の間隔も自動的に空きます。

**横方向の `flex`**（緑の矢印）：入力行は左右並び。`flex-1` がついた入力欄が残りの幅を全部もらって、ボタンは中身に合わせた最小サイズで右に置かれます。`space-x-2` で2つの間に小さな隙間ができます。

**形の対比**：入力欄は `rounded-lg`（控えめな角丸）、送信ボタンは `rounded-2xl`（はっきりしたピル形）。同じ高さに並んでいても、形でちゃんと役割が違って見えるように作られています。