'use client'

import React from 'react'
import { useSuspenseQuery } from '@tanstack/react-query'
import { pokemonOptions } from '../_lib/pokemon'

export function PokemonInfo() {
    // 内部で QueryClient のキャッシュを見に行きます。すでに hydrate 済みのデータがあれば API を叩かず、そのままデータを返します
    const { data } = useSuspenseQuery(pokemonOptions)

    return (
        <div>
            <figure>
                <img src={data.sprites.front_shiny} height={200} alt={data.name} />
                <h2>I'm {data.name}</h2>
            </figure>
        </div>
    )
}