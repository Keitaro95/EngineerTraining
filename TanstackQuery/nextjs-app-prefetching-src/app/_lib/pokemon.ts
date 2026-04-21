import { queryOptions } from '@tanstack/react-query'

// サーバーもクライアントも、ここの定義を使い回す。queryKeyとqueryFnを一元管理
export const pokemonOptions = queryOptions({
    queryKey: ['pokemon'],  //　棚のラベル
    queryFn: async () => {  // 取り方
        const response = await fetch('https://pokeapi.co/api/v2/pokemon/25')
        return response.json()
    }
})