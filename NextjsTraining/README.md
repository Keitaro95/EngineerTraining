
https://nextjs.org/docs/app/getting-started/project-structure


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
@slotではめ込む

@modal

### かいそうこうぞう

```js
[img](NextjsTraining/nestedlayout.png)

<Layout>
  <Template>
    <ErrorBoundary fallback={<Error />}>
      <Suspense fallback={<Loading />}>
        <ErrorBoundary fallback={<NotFound />}>
          <Page />
        </ErrorBoundary>
      </Suspense>
  </Template>
</Layout>


```

even though route structure is defined through folders, a route is not publicly accessible until a page.js or route.js file is added to a route segment.

page.jsが前提でroutingが起きる
nextjsのシステム的にpage.jsありきでURLが決まる

だから、UIコンポーネント置いてるだけのディレクトリにはpage.jsおかないでいい
そうやって、制御できる



app/
  dashboard/ → /dashboard
    page.js
    settings/ → /dashboard/settings
      page.js
  api/
    route.js → /api

/Users/keitarosasaki/Documents/エンジニアトレーニング/NextjsTraining/routing.png


_をつけたファイルは not routableになるよ

/dashboard/_lib/page.js　→ not routable
でもあんまこうしないで private　フォルダに置くのがいいよ



app/
  (admin)/
    dashboard/
        page.js → /dashboard


## Nextjs大体こう

pj/
  src/
    app/
      layout.js
      page.js
  package.json
  next.config.js


### ルート戦略
https://nextjs.org/docs/app/getting-started/project-structure#store-project-files-in-top-level-folders-inside-of-app

app/ を pure routingのためのフォルダにする

pj/
  components/
    ...
  lib/
    ...
  app/
    dashboard/
      page.js
    page.js


### feature別
pj/
  app/
    components/
      ...
    lib/
      ...
    dashboard/
      components/
      lib/
      page.js
    page.js

### route別
app/
  layout.js 子供の中に置くなら消す
  (marketing)
    layout.js このdirの中のlayout
    about/
      page.js
    blog/
      page.js
  (shop)
    layout.js このdirの中のlayout
    loading.js このdirの中のloading
    account/
      page.js


3/20
https://nextjs.org/docs/app/getting-started/layouts-and-pages


3/21
https://nextjs.org/docs/app/getting-started/layouts-and-pages#creating-a-dynamic-segment