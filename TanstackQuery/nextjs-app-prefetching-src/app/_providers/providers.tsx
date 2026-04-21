'use client'
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
// @/エイリアスはNext.jsのルートにtsconfig.jsonがある場合に使えますが、このディレクトリには存在しないため相対パスを使います
import { getQueryClient } from '../_lib/get-query-client'
import type * as React from 'react'


// このprovidersがサーバーとクライアントの境界となる


export default function Providers({ children }: { children: React.ReactNode }) {
    // クライアント側getQueryClientは同じインスタンスを使い回すため
    // HydrationBoundary が復元したデータがそのまま残ります。
    const queryClient = getQueryClient()

    return (
        // providers.tsx(クライアント側)の QueryClient がその JSON を読み取って「復元（hydrate）」
        <QueryClientProvider client={queryClient}>
            {children}
            <ReactQueryDevtools />
        </QueryClientProvider>
    )
}