
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

slugってのは最終/以下で
?でつながるのがparams
/blog/hello?page=2
        ↑       ↑
     params  searchParams
  { slug: "hello" }  { page: "2" }

Page.tsx：デフォルトで用意されてるPagePropsを使う
```js
export default async function Page(props: PageProps<'/blog/[slug]'>) {
  const { slug } = await props.params
  return <h1>Blog post: {slug}</h1>
}
```
layout.tsx：デフォルトで用意されてるPagePropsを使う
```js
export default function Layout(props: LayoutProps<'/dashboard'>) {
  return (
    <section>
      {props.children}
      {/* If you have app/dashboard/@analytics, it appears as a typed slot: */}
      {/* {props.analytics} */}
    </section>
  )
}
```

### 3/22
https://nextjs.org/docs/app/getting-started/linking-and-navigating

デフォルトではサーバーからレンダリングされる
server rendering
prefetch
streaming
client-side transition
でfast and responsiveにできるよ

LayoutとPageは デフォルトでReact Server Component=つまりサーバーレンダリング
サーバーレンダリングには2種類ある
Prerendering（事前レンダリング）:
ビルド時 or 再検証時	
結果がキャッシュされる。静的コンテンツ向き

Dynamic Rendering（動的レンダリング）：
リクエスト時
クライアントのリクエストに応じてその場で生成。動的コンテンツ向き

Next.js の対策：

### Prefetching（プリフェッチ） — ユーザーが訪問しそうなルートを事前に取得しておく
Client-side transitions（クライアントサイド遷移） — ページ遷移をブラウザ側で処理することで体感速度を向上させる

Dynamic Route でプリフェッチをスキップする
ユーザーが /dashboard にホバーしただけで
→ サーバーでDBクエリ実行 → 無駄なコスト発生
訪問するかどうかわからないページのために、サーバーで余分な処理をしないための最適化です。
なのでloading.tsx を追加
Dynamic Route → 部分プリフェッチ → loading UIを即表示 → 体験改善


https://nextjs.org/docs/app/getting-started/linking-and-navigating#streaming

クライアントサイドトランジション
例えば

```js
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        
        <nav>
          <Link href="/">Home</Link>
          <Link href="/dashboard">Dashboard</Link>
          {/* ↓ 必要ないリソースはprefetchしない */}
          <Link prefetch={false}  href="/blog">Dashboard</Link>
        </nav>

        {/* ↓ ここだけページごとに差し替わる */}
        <main>{children}</main>
      </body>
    </html>
  );
}
```


### 3/23
Server and Client Components
https://nextjs.org/docs/app/getting-started/server-and-client-components






### client Componentを使うとき
Client Componentsを使うと機能的にinteractive, browserAPIができるよ
- State and event handlers / onClick, onChange
- ライフサイクルロジック / useEffect
- ブラウザでしか使えないAPI / localStorage, window, Navigator
- reactのカスタムフック

### Server Component
layoutとpagesはserver componentsだよ：デフォルトはサーバーサイド
- serverからデータやAPI取得
- API keyやtoken, secretを使う
- ブラウザに送るjsを減らしたい
- Improve the First Contentful Paint (FCP), and stream content progressively to the client.


サードパーティ
Nextjsは<Carousel /> 
ライブラリ：acme-carousel　
が client onlyだと知らない


API_KEYはサーバーの秘密情報ですが、クライアントで実行すると空文字列になるだけでエラーにならず、気づきにくいバグになります。



### 3/23
https://nextjs.org/docs/app/getting-started/fetching-data




