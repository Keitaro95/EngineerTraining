import React from 'react'
import { HydrationBoundary, dehydrate } from '@tanstack/react-query'
import { pokemonOptions } from './_lib/pokemon'
import { getQueryClient } from './_lib/get-query-client'
import { PokemonInfo } from './_components/pokemon-info'

export default function Home() {
  const queryClient = getQueryClient() // 棚を用意
  // queryClient（棚） に API データ（pokemonOptions）を prefetch して格納
  void queryClient.prefetchQuery(pokemonOptions) 

  return (
    <main>
      <h1>Pokemon Info</h1>
      {/* dehydrate(queryClient) で「棚の中身」を JSON にシリアライズ 
      HydrationBoundary が その JSON を HTML に埋め込む（<script> タグ等）
      ブラウザ（クライアント）に HTML が届く
        ↓
        providers.tsx(クライアント側)の QueryClient がその JSON を読み取って「復元（hydrate）」
        ↓
        PokemonInfo は API を再リクエストせず、すでにキャッシュにデータがある状態で描画 */}

      {/* サーバーで取ってきたデータを JSON にして HTML に埋め込む */}
      <HydrationBoundary state={dehydrate(queryClient)}>
        <PokemonInfo />
      </HydrationBoundary>
    </main>
  )
}