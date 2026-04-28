# Vite + Tailwind CSS 設定メモ

## vite.config.ts — `chat/` をルートとして認識させる

```ts
// vite.config.ts
export default defineConfig({
  root: 'chat',
})
```

Vite はデフォルトでプロジェクトルート（`vite.config.ts` と同じ階層）に `index.html` があることを想定する。  
`root: 'chat'` を指定すると、Vite は `chat/` ディレクトリをルートとして扱い、`chat/index.html` をエントリーポイントとして読み込む。  
そのため `index.html` は `chat/` 直下に置く必要がある。

---

## postcss.config.js — Vite に Tailwind を処理させる

```js
// postcss.config.js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

Tailwind CSS v3 は PostCSS プラグインとして動作する。  
Vite は CSS ファイルを処理するとき、プロジェクトルートの `postcss.config.js` を自動的に読み込み、そこに書かれたプラグインを適用する。  
この設定がないと `@tailwind base` などのディレクティブが変換されず、スタイルが一切当たらない。

---

## tailwind.config.js — どのファイルを対象にするか

```js
// tailwind.config.js
export default {
  content: ['./chat/**/*.{ts,tsx}'],
  theme: { extend: {} },
  plugins: [],
}
```

Tailwind は本番ビルド時に `content` に指定したファイルを走査し、実際に使われているクラスだけを出力する（未使用クラスは除去される）。  
`content` の指定が漏れていると、そのファイルで使った Tailwind クラスがビルド後に消えてスタイルが当たらなくなる。

---

## chat/src/style.css — Tailwind の読み込み

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

| ディレクティブ | 内容 |
|---|---|
| `@tailwind base` | ブラウザのデフォルトスタイルをリセット／正規化する |
| `@tailwind components` | プラグインや `@layer components` で定義したクラスを出力する |
| `@tailwind utilities` | `flex`, `text-center` などのユーティリティクラスを出力する |

このファイルを `index.tsx` で import することで、アプリ全体に Tailwind が適用される。

```ts
// index.tsx
import './style.css'
```
