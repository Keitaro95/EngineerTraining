# データの流れ


## 大元：pokemon.ts 
ここでAPI fetch
pokemonOptions
これがクエリキャッシュになる。


## ファクトリー関数　クエリクライアントを作って、生成する工場 get-query-client.ts 
まずクエリクライアントの振る舞いを定義。
- キャッシュ時間
サーバー：makeQueryClient() を毎回新規作成
ブラウザ：browserQueryClient を使い回す



ファクトリー関数
サーバーコンポーネント　での振る舞い
クライアントコンポーネント　での振る舞い
↓                   ↓

サーバーコンポーネント　　　クライアントコンポーネント


## サーバーコンポーネント：page.tsx　
```tsx
const queryClient = getQueryClient() // サーバーで使われるファクトリー関数

// pokemonOptionsはフェッチ関数
  // queryClient（棚） に API データ（pokemonOptions）を prefetch して格納
  void queryClient.prefetchQuery(pokemonOptions) 
```
- dehydrate(queryClient) → queryClientを乾燥させる。つまり プリフェッチした棚の中身を JSON にシリアライズ
- HydrationBoundary → JSON を HTML に埋め込む。こうするとHTML生成時に乾燥を元に戻せる

↓ HTML がブラウザに届く

## クライアントコンポーネント：　ステップ1：Providers が「空の棚」を Context に登録
providers.tsx（'use client'）
const queryClient = getQueryClient()  // ブラウザ用の棚を作る
<QueryClientProvider client={queryClient}>  // Contextに棚を登録
  {children}
</QueryClientProvider>
この時点では棚は空。ただ「棚はここにあるよ」とReactのContextに登録しただけ。


## ステップ2：HydrationBoundary が棚にデータを流し込む
page.tsx（{children} として Providers の中で動く）
<HydrationBoundary state={dehydrate(queryClient)}>
state の中にはサーバーが作った JSONが入っている
HydrationBoundary はブラウザ上で動くとき、Contextから上の棚（Providers の queryClient）を探す
見つけたら state の JSON を棚に流し込む（= hydrate）


## pokemon-info.tsx
サーバーと同じpokemonOptionsをフェッチ関数に使っている。
もしここにあらかじめ取得されているデータがあるなら
```tsx
'use client'
const { data } = useSuspenseQuery(pokemonOptions)
```
