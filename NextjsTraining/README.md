
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

### 3/24
データフェッチ

### server component
1. The fetch API
2. An ORM or database


### streamingする方法
- loading.jsで囲む
- <Suspense>で囲む

<Suspense> を使うと、ページのどの部分をストリーミングするかをより細かく制御できます。
例えば、<Suspense> バウンダリの外側にあるページコンテンツはすぐに表示し
バウンダリの内側にあるブログ投稿の一覧はストリーミングで読み込む、といったことが可能です。


最良のユーザー体験のために、アプリが応答していることをユーザーが理解できるような、意味のあるローディング状態を設計することを推奨します。
例えば、スケルトンやスピナーを使用したり、カバー写真やタイトルなど、次の画面の小さくても意味のある一部を表示したりすることができます。
開発中は、React DevToolsを使用してコンポーネントのローディング状態をプレビューおよび検査できます。



### client component
https://nextjs.org/docs/app/getting-started/fetching-data#client-components

``` ts
// app/blog/page.tsx
import Posts from '@/app/ui/posts'
import { Suspense } from 'react'
 
export default function Page() {
  // Don't await the data fetching function
  const posts = getPosts() // ← await なし、Promise のまま
 
  return (
    // use() がサスペンドしている間、<Suspense> の fallback が表示される。Promise が解決されたら <Posts> が描画される。
    <Suspense fallback={<div>Loading...</div>}>
      <Posts posts={posts} />
    </Suspense>
  )
}

// app/ui/posts.tsx
'use client'
import { use } from 'react'
 
export default function Posts({
  posts,
}: {
  posts: Promise<{ id: string; title: string }[]>
}) {
  const allPosts = use(posts) // Promise を受け取ると、解決されるまでコンポーネントの処理を**サスペンド（一時停止）**する。
 
  return (
    <ul>
      {allPosts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}

```

https://nextjs.org/docs/app/getting-started/fetching-data#community-libraries
サードパーティ
例えば tanstack

```tsx
import { useQuery } from '@tanstack/react-query'

function Todos() {
  状態を保持してくれる
  const { data, isPending, error } = useQuery({
    引数1：クエリ
    queryKey: ['todos'],　
    引数2：fetch関数
    queryFn: () => fetch('/api/todos').then(r => r.json()),
  })

  状態を展開できる
  if (isPending) return <span>Loading...</span>
  if (error) return <span>Oops!</span>
  データを展開する
  return <ul>{data.map(t => <li key={t.id}>{t.title}</li>)}</ul>
}

export default Todos
```

https://nextjs.org/docs/app/getting-started/fetching-data#parallel-data-fetching

複数のasyncは並行で起こる
```tsx

import { getArtist, getAlbums } from '@/app/lib/data'

export default function Page({ params }) {

  const { username } = await params
  const artist = await getArtist(username)
  const albums = await getAlbums(username)
  return <div>{artist.name}</div>
}

```

React.cache と context providersを使ってfetched data を
Server and Client Components で共有できる
同じデータを両方で使いたいとき、愚直にやると2回フェッチが走る。それを防ぐのがこのパターン。

リクエスト到着
  └─ layout.tsx: getUser() → Promise生成（fetch開始）
       └─ UserProvider: Promise をコンテキストに保存
            ├─ Profile (Client): use(promise) → Suspense fallback → 解決後レンダリング
            └─ DashboardPage (Server): await getUser() → cache済みなので fetch は走らない


https://nextjs.org/docs/app/getting-started/mutating-data

## Mutating Data
React Server Functionsを使ってデータをmutateする
React Server Functions：サーバーで動く非同期の関数。クライアントサイドからreqで呼び出す。Server Actionとも呼ばれる

StartTransition：POSTメソッド
action を使って formに送られる
formActionを使ってbuttonに送られる

use server を書いている関数で定義される

https://nextjs.org/docs/app/getting-started/mutating-data

クライアントコンポーネントでサーバーファンクションを起こす

```tsx

export default function LikeButton({ initialLikes }: { initialLikes: number }) {
  const [likes, setLikes] = useState(initialLikes)

  return (
    <>
      <p>{likes}</p>
      <button
        onClick={async () => {
          const UpdatedLikes = await incrementLike()
          setLikes(updatedLikes)
          }}
      >
        Like
        </button>
    </>
  )
}

```

https://nextjs.org/docs/app/getting-started/mutating-data#revalidate-data

redirectをつかって、データの変更を即時で伝える

```tsx
'use server'
 
import { auth } from '@/lib/auth'
import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
 
export async function createPost(formData: FormData) {
  const session = await auth()
  if (!session?.user) {
    throw new Error('Unauthorized')
  }
  // Mutate data
  // ...
 
  revalidatePath('/posts')
  redirect('/posts')
}
```

```tsx
'use server'
 
import { cookies } from 'next/headers'
 
export async function exampleAction() {
  const cookieStore = await cookies()
 
  // Get cookie
  cookieStore.get('name')?.value
 
  // Set cookie
  cookieStore.set('name', 'Delba')
 
  // Delete cookie
  cookieStore.delete('name')
}
```

### useEffectで自動的にmutation更新する

```tsx
'use client'

import { incrementViews } from './actions'
import { useState, useEffect, useTransition } from 'react'

export default function ViewCount({ initialViews }: { initialViews: number }) {
  // 初期表示値（Server Componentなどから受け取る）
  const [views, setViews] = useState(initialViews)

  // 非同期更新を「遷移」として扱う（UIをブロックしにくくする）
  const [isPending, startTransition] = useTransition()

  // 初回マウント時に1回だけ実行（[]）
  useEffect(() => {
    startTransition(async () => {
      // Server Actionを呼んでDB側の閲覧数を更新（mutation）
      const updatedViews = await incrementViews()
      // 返ってきた最新値でクライアントUIを更新
      setViews(updatedViews)
    })
  }, [])

  // isPending を使うと更新中表示もできる
  return <p>Total Views: {isPending ? '...' : views}</p>
}
```




### cache

https://nextjs.org/docs/app/getting-started/caching

```tsx
import { cacheLife } from 'next/cache'
 
export async function getUsers() {
  'use cache'
  cacheLife('hours')
  return db.query('SELECT * FROM users')
}
```

```tsx
import { cookies } from 'next/headers'
import { Suspense } from 'react'
 
async function UserGreeting() {
  const cookieStore = await cookies()
  const theme = cookieStore.get('theme')?.value || 'light'
  return <p>Your theme: {theme}</p>
}
 
export default function Page() {
  return (
    <>
      <h1>Dashboard</h1>
      <Suspense fallback={<p>Loading...</p>}>
        <UserGreeting />
      </Suspense>
    </>
  )
}
```


リクエストごとにユニークなUUIDなどを生成する

```tsx
import { connection } from 'next/server'
import { Suspense } from 'react'

async function UniqueContent() {
  await connection()
  const uuid = crypto.randomUUID()
  return <p>Request ID: {uuid}</p>
}

export default function Page() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <UniqueContent />
    </Suspense>
  )
}

// 代わりに　use cacheでもいい
export default function Page() {
  'use cache'
  const buildId = crypto.randomUUID()
  return <p>Build ID: {buildID}</p>
}

```

### 決定論的な動作はプレレンダリング中に
このページはjsonを使う場合

```tsx
import fs from 'node:fs'

export default async function Page() {
  const content = fs.readFileSync('./config.json', 'utf-8')
  const constants = await import('./constants.json')
  const processed = JSON.parse(content).items.map((item) = item.value * 2)

  return (
    <div>
      <h1>{constants.appName}</h1>
      <ul>
        {processed.map((value, i) => (
          <li key={i}>{value}</li>
        ))}
      </ul>
    </div>
  )
}

```


静的なシェルに保存される処理（クライアントに保存される）
- use cache
- <Suspense>
- 決定論的操作
html, rscからなる静的なシェルが生成される=部分プリレンダリング（PPR)
PPRはNext.jsの機能で、1つのページを静的な部分と動的な部分に分けてレンダリングする仕組みです。
流れ
ビルド時: HTML + RSC Payloadからなる静的シェルを生成
リクエスト時: 静的シェルを即座に返す（高速）
ストリーミング: 動的部分が完了次第、Suspense fallbackを実際のコンテンツに差し替え
つまり、従来の「ページ全体が静的 or 動的」という二択ではなく、1つのページ内で静的・動的を共存させることがPPRの本質です。

reactのSuspenseを使うと、Suspenseの中は、取得されるまで待機されることになる。
メインのPage.tsxが以下の場合この中が待機状態のため
子供のcomponentは ページ全体のレンダリングが完了するまで何も表示されない。従来のSSR（非Streaming）と同じ挙動になる。
```tsx
// app/layout.tsx
import { Suspense } from 'react'

export default function RootLayout({ children }) {
  return (
    <html>
      <Suspense fallback={null}>  {/* ← fallbackが空 = 送れるものがない */}
        <body>{children}</body>
      </Suspense>
    </html>
  )
}
```
なのでディレクトリに個別にlayout.tsxをおいておく方がいい


https://nextjs.org/docs/app/getting-started/caching#putting-it-all-together


