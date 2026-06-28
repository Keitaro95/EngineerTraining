'use client'

import { usePathname } from 'next/navigation'

// replaceState → 現在のエントリを上書きする（戻るボタンで前のページに戻れない）
export function LocaleSwitcher() {
    // usePathname() で現在のパス（例: /about）を取得
    const pathname = usePathname()

    function switchLocale(locale: string) {
        // /${locale}${pathname} でロケールを先頭に付けたパスを生成
        const newPath = `/${locale}${pathname}`
        // replaceState でURLだけを変更 → ページのリロードなし・ナビゲーションなし
        window.history.replaceState(null, '', newPath)
    }

    return (
        <>
            <button onClick={() => switchLocale('en')}>English</button>
            <button onClick={() => switchLocale('fr')}>French</button>
        </>
    )
}