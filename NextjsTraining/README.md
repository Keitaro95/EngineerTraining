
```bash
npx create-next-app@latest my-app --yes


```

package.jsonでESLint設定
```json
{
  "scripts": {
    "lint": "eslint",
    "lint:fix": "eslint --fix"
  }
}
```

tsconfig.json と jsconfig.jsonで
pathとbaseUrlを決められる
相対インポート
```json
{
    "compilerOptions": {
        "baseUrl": "src/",
        "paths": {
            "@/styles/*": ["styles/*"],
            "@/componets/*": ["components/*"],
        }
    }
}
```


next.config.js：Next.jsの設定
package.json：ライブラリ
instrumentation.ts：テレメトリー
proxy.ts：プロキシ
.env
.env.local
.env.production
.env.development
eslint.config.mjs：ESLint
.gitignore
next-env.d.ts：TSの宣言
tsconfig.json：TS
jsconfig.json：JS

## 予約ファイル：app/
layout		Layout
page		Page
loading		Loading UI
not-found	Not found UI
error		Error UI
global-error		Global error UI
route		API endpoint
template	Re-rendered layout
default		Parallel route fallback page

## routing
app/layout.tsx ：ALL
app/blog/layout.tsx　：/blog 
app/page.tsx　：/のページ
app/blog/page.tsx ：/blogのページ
app/blog/authors/page.tsx ：/blog/authors のページ

## ダイナミックルーティング
app/shop/[slug]/page.tsx ：中にパスは1つだけ
app/shop/[...slug]/page.tsx：パスを何個も入れられる

/shop/shoes/nike → { slug: ["shoes", "nike"] }

## ルートグループ
app/(marketing)/page.tsx ： marketをURLからのぞく
app/(shop)/cart/page.tsx ： /cart からURL
app/blog/_components/Post.tsx ：_をつけてるのでRouting辿り着けない 
app/blog/_lib/data.ts ：_をつけてるのでRouting辿り着けない 

## インターセプト route
