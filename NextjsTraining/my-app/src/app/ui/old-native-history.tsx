'use client'

import { useSearchParams } from "next/navigation"

//初期URL: /products
// ↓ Sort Ascending をクリック
// URL: /products?sort=asc  ← 履歴に追加
// pushState → 新しい履歴エントリを追加する（戻るボタンで前のページに戻れる）
export default function SortProducts() {
    const searchParams = useSearchParams()

    function updateSorting(sortOrder: string) {
        const params = new URLSearchParams(searchParams.toString())
        // 現在のクエリ
        // 例: "category=shoes&sort=asc"

        params.set('sort', sortOrder)
        // sort だけ上書き → "category=shoes&sort=desc"

        // ここでURLだけが書き換わる
        window.history.pushState(null, '', `?${params.toString()}`)
        // window.history.pushState(state, unused, url)
        // URLバーを ?category=shoes&sort=desc に変更
        // → useSearchParams が変化を検知して再レンダリング
    }

    return (
        <>
            <button onClick={() => updateSorting('asc')}>Sort Ascending</button>
            <button onClick={() => updateSorting('desc')}>Sort Descending</button>
        </>
    )
}