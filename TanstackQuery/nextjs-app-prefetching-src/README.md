【サーバー】
  page.tsx
    prefetchQuery → サーバー専用の棚にデータを入れる
    dehydrate     → 棚の中身を JSON に変換
    HydrationBoundary → その JSON を HTML に埋め込む

        ↓ HTML がブラウザに届く

【ブラウザ】
  layout.tsx の Providers
    → クライアント用の「空の棚」を用意

  HydrationBoundary（今度はクライアントとして動く）
    → HTML に埋まってた JSON を発見
    → Providers が用意した棚にデータを流し込む（hydrate）

  PokemonInfo
    → 棚にもうデータがある → API 再リクエストなし
