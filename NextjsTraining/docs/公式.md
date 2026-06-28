
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



### 再検証
https://nextjs.org/docs/app/getting-started/revalidating

- 時間ベースの再検証
- オンデマンド再検証


## エラー処理
モデルは errorを　valueとして返して欲しいと期待してる
なので try catch使わないで

```tsx
// app/actions.ts
'use server'
 
export async function createPost(prevState: any, formData: FormData) {
  const title = formData.get('title')
  const content = formData.get('content')
 
  const res = await fetch('https://api.vercel.app/posts', {
    method: 'POST',
    body: { title, content },
  })
  const json = await res.json()
 
  if (!res.ok) {
    return { message: 'Failed to create post' }
  }
}
```


```tsx
//app/ui/form.tsx
'use client'

import { useActionState } from 'react'
import { createPost } from '@/app/actions'

const initialState = {
  message: '',
}

export function Form() {
  const [state, formAction, pending] = useActionState(createPost, initialState)

  return (
    <form action={formAction}>
      <label htmlFor="title">Title</label>
      <input type="text" id="title" name="title" required />
      <label htmlFor="content">Content</label>
      <textarea id="content" name="content" required />
      {/* ここでstateの中のmessageでエラー検出 */}
      {state?.message && <p aria-live="polite">{state.message}</p>}
      <button disabled={pending}>Create Post</button>
    </form>
  )
}

```

https://nextjs.org/docs/app/getting-started/error-handling#server-components

```tsx
export default async function Page() {
  const res = await fetch(`https://...`)
  const data = await res.json()
  
  // この中で 条件分岐
  if (!res.ok) {
    return 'There was an error.'
  }
 
  return '...'
}
```

### エラー境界
捕捉されない例外
発生するはずのないバグや問題を示す予期せぬエラーは
エラー境界で捕捉する必要があります。

app/dashboard/error.tsx：関数機能
app/custom-error-boundary.tsx：境界
app/some-component.tsx：この中で使う

レンダリング中のエラーを捕捉するように設計されています。アプリ全体をクラッシュさせる代わりに、代替のUIを表示する。

useState, useReducerでエラーをシステム処理する
```tsx
'use client'
 
import { useState } from 'react'
 
export function Button() {
  const [error, setError] = useState(null)
 
  const handleClick = () => {
    try {
      // do some work that might fail
      throw new Error('Exception')
    } catch (reason) {
      setError(reason)
    }
  }
 
  if (error) {
    /* render fallback UI */
  }
 
  return (
    <button type="button" onClick={handleClick}>
      Click me
    </button>
  )
}
```


useTransitionでキャッチ
```tsx
'use client'
 
import { useTransition } from 'react'
 
export function Button() {
  const [pending, startTransition] = useTransition()
 
  const handleClick = () =>
    startTransition(() => {
      throw new Error('Exception')
    })
 
  return (
    <button type="button" onClick={handleClick}>
      Click me
    </button>
  )
}
```

https://nextjs.org/docs/app/getting-started/error-handling#global-errors


## CSS

tailwind
npm install -D tailwindcss @tailwindcss/postcss

postcss.config.mjs
```mjs
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

app/globals.css
```css
@import 'tailwindcss'
```

app/layout.tsx
```tsx
import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>  
    </html>
  )
}
```
app/Page.tsx

```tsx
export default function Page() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1 className="text-4xl font-bold">Welcome to Next.js!</h1>
    </main>
  )
}
```

css module：名前衝突を気にせずに 

app/blog/blog.module.css
```css
.blog {
  padding: 24px;
}
```

app/blog/page.tsx　のなかで .blogをアタッチする
```tsx
import styles from './blog/module.css'

export default function Page() {
  return <main className={styles.blog}></main>
}

```


Global CSS
app/global.css

```css
body {
  padding: 20px 20px 60px;
  max-width: 680px;
  margin: 0 auto;
}
```

app/layout.tsx
```tsx
import './global.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

```
We recommend using global styles for truly global CSS (like Tailwind's base styles), Tailwind CSS for component styling, and CSS Modules for custom scoped CSS when needed.


外部スタイルシート
import 'bootstrap/dist/css/bootstrap.css'
 
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="container">{children}</body>
    </html>
  )
}

### CSSのインポート順
To keep CSS ordering predictable:

CSSのインポートはできる限り単一のJavaScriptまたはTypeScriptエントリファイルにまとめる
グローバルスタイルとTailwindのスタイルシートはアプリケーションのルートでインポートする
一般的なデザインパターンをユーティリティクラスでカバーできるため、ほとんどのスタイリングにはTailwind CSSを使用する
Tailwindのユーティリティだけでは不十分な場合は、コンポーネント固有のスタイルにCSS Modulesを使用する
CSS Modulesのファイル名には一貫した命名規則を使用する（例：`<name>.tsx` よりも `<name>.module.css`）
重複インポートを避けるために、共通スタイルは共有コンポーネントに切り出す
ESLintの `sort-imports` のように、インポートを自動ソートするリンターやフォーマッターは無効にする
`next.config.js` の `cssChunking` オプションを使うと、CSSのチャンク分割方法を制御できる



Development vs Production
開発環境（`next dev`）では、CSSの変更はFast Refreshによって即座に反映される。
本番環境（`next build`）では、すべてのCSSファイルが自動的に結合・ミニファイされ、コード分割された `.css` ファイルとして出力される。これにより、各ルートで読み込まれるCSSは最小限に抑えられる。
本番環境ではJavaScriptが無効でもCSSは読み込まれるが、開発環境のFast RefreshにはJavaScriptが必要である。
CSSの順序は開発環境と本番環境で異なる場合があるため、最終的なCSS順序はビルド（`next build`）で必ず確認すること。



### Image Optimization

Next.jsの `<Image>` コンポーネントはHTMLの `<img>` 要素を拡張し、以下の機能を提供する：

- **サイズ最適化**：WebPなどの最新画像フォーマットを使用し、各デバイスに適したサイズの画像を自動的に配信する。
- **視覚的安定性**：画像の読み込み中にレイアウトシフトが発生しないよう自動的に防ぐ。
- **高速なページ読み込み**：ネイティブブラウザの遅延読み込みを使用し、ビューポートに入ったときのみ画像を読み込む。オプションでぼかしプレースホルダーも利用可能。
- **アセットの柔軟性**：リモートサーバーに保存された画像を含め、オンデマンドで画像をリサイズできる。

画像を静的インポートした場合、Next.jsは自動的に固有の `width` と `height` を判定する。これらの値は画像のアスペクト比の算出に使用され、読み込み中のCumulative Layout Shift（累積レイアウトシフト）を防ぐ。

```tsx
import Image from 'next/image'
 
export default function Page() {
  return <Image src="" alt="" />
}
```

app
public

publicに入れたやつは 自動的に '/' 扱いになる
app/page.tsx
```tsx
import Image from 'next/image'
 
export default function Page() {
  return (
    <Image
      src="/profile.png"
      alt="Picture of the author"
      width={500}
      height={500}
    />
  )
}

import Image from 'next/image'
import ProfileImage from './profile.png'
 
export default function Page() {
  return (
    <Image
      src={ProfileImage}
      alt="Picture of the author"
      // width={500} automatically provided
      // height={500} automatically provided
      // blurDataURL="data:..." automatically provided
      // placeholder="blur" // Optional blur-up while loading
    />
  )
}
```

```tsx
import Image from 'next/image'
 
export default function Page() {
  return (
    <Image
      src="https://s3.amazonaws.com/my-bucket/profile.png"
      alt="Picture of the author"
      width={500}
      height={500}
    />
  )
}
```


Next.jsはビルド時にリモートファイルにアクセスできないため、リモート画像の場合は `width`・`height`・任意の `blurDataURL` プロパティを手動で指定する必要がある。`width` と `height` は正しいアスペクト比の推定と、画像読み込み時のレイアウトシフト防止に使用される。なお、`fill` プロパティを使用すると、親要素のサイズに合わせて画像を拡大表示することもできる。

リモートサーバーの画像を安全に使用するには、`next.config.js` でサポートするURLパターンのリストを定義する必要がある。悪意ある使用を防ぐため、できる限り具体的に指定すること。例えば、以下の設定では特定のAWS S3バケットからの画像のみを許可する：

```tsx
import type { NextConfig } from 'next'
 
const config: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 's3.amazonaws.com',
        port: '',
        pathname: '/my-bucket/**',
        search: '',
      },
    ],
  },
}
 
export default config
```


### font
https://nextjs.org/docs/app/getting-started/fonts

app/layout.tsx
```tsx
import { Geist } from 'next/font/google'
 
const geist = Geist({
  subsets: ['latin'],
})
 
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={geist.className}>
      <body>{children}</body>
    </html>
  )
}

import { Geist } from 'next/font/google'
 
const geist = Geist({
  subsets: ['latin'],
})
 
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={geist.className}>
      <body>{children}</body>
    </html>
  )
}

import { Roboto } from 'next/font/google'
 
const roboto = Roboto({
  weight: '400',
  subsets: ['latin'],
})
 
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={roboto.className}>
      <body>{children}</body>
    </html>
  )
}

```

## メタデータ
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />

app/blog/layout.tsx
```tsx
import type { Metadata } from 'next'
 
export const metadata: Metadata = {
  title: 'My Blog',
  description: '...',
}
 
export default function Layout() {}
```

app/blog/[slug]/page.tsx
```tsx
import type { Metadata, ResolvingMetadata } from 'next'
 
type Props = {
  params: Promise<{ slug: string }>
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}
 
export async function generateMetadata(
  { params, searchParams }: Props,
  parent: ResolvingMetadata
): Promise<Metadata> {
  const slug = (await params).slug
 
  // fetch post information
  const post = await fetch(`https://api.vercel.app/blog/${slug}`).then((res) =>
    res.json()
  )
 
  return {
    title: post.title,
    description: post.description,
  }
}
 
export default function Page({ params, searchParams }: Props) {}

```


bot対策
動的にレンダリングされるページでは、Next.js はメタデータを別途ストリーミングし、generateMetadata が解決された後に HTML へ注入します。これにより UI のレンダリングをブロックしません。

ストリーミングメタデータは、視覚的なコンテンツを先にストリーミングできるため、体感パフォーマンスを向上させます。

ストリーミングメタデータは、<head> タグにメタデータがあることを期待するボットやクローラー（例：Twitterbot、Slackbot、Bingbot）に対しては無効化されます。これらは受信リクエストの User Agent ヘッダーを使用して検出されます。

Next.jsはリクエストの User-Agent ヘッダーを確認し、既知のボット・クローラーからのリクエストにはストリーミングを無効化して、完全なHTMLを同期的に返す

Next.js の設定ファイルで htmlLimitedBots オプションを使用することで、ストリーミングメタデータをカスタマイズしたり、完全に無効化したりすることができます。

プリレンダリングされたページは、メタデータがビルド時に解決されるため、ストリーミングを使用しません。

ストリーミングメタデータについて詳しく学ぶ。

import { ImageResponse } from 'next/og'

export default function OGImage() {
  return new ImageResponse(
    <div style={{ display: 'flex', fontSize: 60 }}>
      Hello World
    </div>,
    { width: 1200, height: 630 }
  )
}


### route handler
appディレクトリ内で
APIエンドポイントを作成する
Web標準のRequest/Response APIを使います。

app/api/route.ts
```tsx
export async function GET(request: Request) {
  return Response.json({ message: "Hello!" })
}

export async function GET(_req: NextRequest, ctx: RouteContext<'/users/[id]'>) {
  const { id } = await ctx.params
  return Response.json({ id })
}
```

https://nextjs.org/docs/app/getting-started/route-handlers



### proxy

https://nextjs.org/docs/app/getting-started/proxy

req → proxy でmodify　→ req



`redirects`の設定を next.config.tsで書いて
ここでreqに複雑な設定をする
proxyはauthみたいなfull sessionでは使われない
許可性のredirectで使われる

root/proxy.ts
root/src/proxy.ts
```tsx
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
 
// This function can be marked `async` if using `await` inside
export function proxy(request: NextRequest) {
  return NextResponse.redirect(new URL('/home', request.url))
}
 
// Alternatively, you can use a default export:
// export default function proxy(request: NextRequest) { ... }
 
ここでプロキシしたいpathを書く
export const config = {
  matcher: '/about/:path*',
}
```


## deploy
**Node.js**
full機能
package.jsonに buildとstartがある状態で

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

npm run build
npm run start


**Docker**
k8s運用もできる
https://nextjs.org/docs/app/getting-started/deploying#templates-1


**Static**
静的サイト / Single-Page-Applicationなど
static exportをサポートしています


**Adapters**
いろんなInfraに可用性あり
アダプターAPI
https://nextjs.org/docs/app/api-reference/config/next-config-js/adapterPath

Next.js公式が検証してる　認証済みAdapterもあります
https://nextjs.org/docs/app/getting-started/deploying#verified-adapters

CloudflareとかNetlifyは彼らオリジナルのインテグレーションを持っています



## upgrade

```sh
npm next upgrade
npx @next/codemod@canary upgrade latest
npm i next@latest react@latest react-dom@latest eslint-config-next@latest
```


## メトリクス
https://nextjs.org/docs/app/guides/analytics#client-instrumentation

root/instrumentation-client.js
```js
// Initialize analytics before the app starts
console.log('Analytics initialized')
 
// Set up global error tracking
window.addEventListener('error', (event) => {
  // Send to your error tracking service
  reportError(event.error)
})
```

## Authentification
認可：username, password
Session Maganement：Auth stateを管理して全てのreqで送る
認証：userが受け取れるdataやrouteを決める


https://nextjs.org/docs/app/guides/authentication#sign-up-and-login-functionality

