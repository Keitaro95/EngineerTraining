

開発ドキュメント
Next.js と tanstack queryを組み合わせた開発ドキュメント

# データフェッチ
- pokemonOptionsはキャッシュ対象にするものの定義
- クエリクライアントは棚そのものの定義


## 大元のフェッチ関数　ex: pokemon.ts 
dir: root/_lib/pokemon.ts 
API fetchをする関数。tanstackのqueryOptionsを使ってfetch関数を定義している
pokemonOptionsはサーバーコンポーネント：page.tsx　と
クライアントコンポーネント：データ表現のコンポーネントpokemon-info.tsxに使われている

```tsx
import { queryOptions } from '@tanstack/react-query'
export const pokemonOptions = queryOptions({
    queryKey: ['pokemon'],  //　棚のラベル
    queryFn: async () => {  // 取り方
        const response = await fetch('https://pokeapi.co/api/v2/pokemon/25')
        return response.json()
    }
})
```

## ファクトリー関数で新しいQueryClientを作る　 ex:  get-query-client.ts 
dir: root/_lib/get-query-client.ts 
ファクトリ関数makeQueryClient()
新しいクエリクライアントの振る舞いを定義：キャッシュ持続時間/成功済み (success) のクエリもフェッチ中 (pending) のクエリもクライアントへ送信する

```tsx
function makeQueryClient() {
    return new QueryClient({
        defaultOptions: {
            queries: {
                staleTime: 60 * 1000,
            },
            dehydrate: {
                shouldDehydrateQuery: (query) =>
                    defaultShouldDehydrateQuery(query) || query.state.status === 'pending',
            }
        }
    })
}
let browserQueryClient: QueryClient | undefined = undefined
```
getQueryClient()で
サーバーコンポーネントでの振る舞い
    ＝サーバー：makeQueryClient() を毎回新規作成。使い回しがあるとユーザー間でキャッシュが混ざるセキュリティリスクがあるから
クライアントコンポーネントでの振る舞い
    =ブラウザ：browserQueryClient を使い回す。クライアント側がキャッシュを保持し続けるため
```tsx
export function getQueryClient() {
    // server側での振る舞い
    if (environmentManager.isServer()) {
        return makeQueryClient()
    } else {
        // ブラウザ側での振る舞い
        // クエリクライアントがないならば初回生成
        if(!browserQueryClient) browserQueryClient = makeQueryClient()
            return browserQueryClient
    }
}
```


# データ表現
- layout.tsx（'use client' なしサーバーコンポーネント）
    - <Providers>（'use client' ありクライアントコンポーネント）
        - {children}=page.tsx（サーバーコンポーネント）
            - <PokemonInfo />



## layout.tsx
Next.jsのコンポーネント。Page.tsxを中で使うときに、layout表現となる。
内部で、オリジナルで作成したproviders.tsxを使っている
```tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

## キャッシュの棚を供給する層：providers.tsx：クライアントコンポーネント
クライアントコンポーネント用queryClientを生成。
<QueryClientProvider　client={queryClient}> 
あくまで、棚を置いて、子孫へと渡す、供給するだけの層です。
「この棚を Context に登録する」という宣言です。

でqueryClientがこれ以降の子孫へと渡ります。
このコンポーネントはlayout.tsxに乗るため、
layout配下の全てのcomponentに渡ります。

{children}側、つまりPage.tsx以降の子孫の側ではコンポーネントから
useQuery()が使われている箇所で、client={queryClient}をみます
useQuery()側はContext から受け取ります

```tsx
export default function Providers({ 
    children 
    }: { 
        children: React.ReactNode 
    }) {
    const queryClient = getQueryClient()
    return (
        <QueryClientProvider client={queryClient}>
            {children}
            <ReactQueryDevtools />
        </QueryClientProvider>
    )
}
```

## データを取得しているサーバーコンポーネント：page.tsx　
```tsx
サーバー側の振る舞いをするqueryClient（棚A）

（棚A）はリクエストが終わると消えるため、ハイドレーションして
クライアント（ブラウザ）が持つ（棚B）へ送る（HydrationBoundary にて）
const queryClient = getQueryClient()

// 1. pokemonOptionsを見て棚に ['pokemon'] というラベルのデータはあるか？確認
// 2. ない場合（初回取得）→pokemonOptionsのqueryFnを実行=PokeAPIをfetchして棚に格納
// 3. ある場合（2回目以降）→queryClientで定義しておいた振る舞い通りstaleTime=60秒以内ならfetchしない

// 棚のラベル（pokemonOptionsのqueryKey）を使って、棚(サーバー側の振る舞いで定義されたqueryClient)にデータを先に詰めておく（prefetch）
// つまりここでAPIフェッチしている
void queryClient.prefetchQuery(pokemonOptions) 

// 1. dehydrate(queryClient) プリフェッチしたデータをJSONにシリアライズ → { queries: [{ queryKey: ['pokemon'], data: {...ピカチュウのデータ...} }] }

// <HydrationBoundary state={dehydrate(queryClient)}>でプリフェッチしたJSONをHTMLに埋め込みブラウザ側クエリクライアント（棚Bに送信）

1. ブラウザ側での認識の順番では HydrationBoundary が先にコンポーネントツリーで実行される。つまり、プリフェッチして、JSON化したデータはこの<HydrationBoundary >でhydrateされる（データの復元）こうして、棚（B）にはデータがあることになる

<HydrationBoundary state={dehydrate(queryClient)}>

2. 次に、<PokemonInfo />が動く
const { data } = useSuspenseQuery(pokemonOptions)
ここでは、クライアントコンポーネントのqueryClient(棚)を見る。
つまりproviders.tsxでクライアントの振る舞いをするqueryClient（棚B）を見る。棚Bにはpage.tsxがプリフェッチしてくれたデータがあるため、データを取得できる。
    <PokemonInfo />
<HydrationBoundary />
```


サーバー側                          ブラウザ側
page.tsx の queryClient（棚A）      providers.tsx の queryClient（棚B）
  ↓ prefetch → データ格納             ↓ QueryClientProvider で Context に登録
  ↓ dehydrate → JSON化               ↓
  ↓ HydrationBoundary で送信 ─────→  棚B に復元（hydrate）
                                       ↓
                                      useSuspenseQuery → 棚B からデータ取得



つまり providersが大枠として クライアント用の queryClient（棚B）を生成してあって、

この中childrenで page.tsxはサーバーコンポーネントとしてqueryClient（棚A）を作っているが、HydrationBoundary で棚B にプリフェッチしたデータを流しているとわかった。

<PokemonInfo />そのものは、ReactのcontextからuseSuspenseQuery → 棚B からデータ取得している。


わざわざ棚Aが必要なのは、サーバーコンポーネントは、ブラウザコンポーネント間で共通するContext を読みにいけないから。
JSONを渡すことで、サーバーコンポーネントで取得したデータをクライアントコンポーネントに渡している。サーバーとブラウザの間を渡せるのは JSON だけ、というのが根本の制約で、棚A・dehydrate・HydrationBoundary はその制約を乗り越えるための仕組みです。

queryClient（棚A）　をわざわざ作る必要もないと思うけど、これは、振る舞いを共通にしておくための定義があるから。特に shouldDehydrateQuery は棚Aにしか意味がありません。「どのデータを JSON に含めるか」はサーバー側（棚A）の dehydrate 時にしか使われないからです。

棚Aをわざわざ QueryClient として作るのは：

prefetchQuery を使うために QueryClient のAPIが必要
dehydrate(queryClient) に渡すために QueryClient インスタンスである必要がある
設定（staleTime・shouldDehydrateQuery）を同じ関数で統一できる
ただのオブジェクトではなく QueryClient でないと prefetchQuery も dehydrate も動かない、というのが理由です。