import 'server-only'
// このファイルはサーバーオンリーだと知らせる

// するとこれがAPI_KEY部分が、エラー検出される

// エラーは発生しない — そのまま実行される
// API_KEY が空文字列になる（Next.jsはクライアントバンドルでNEXT_PUBLIC_なし変数を除去）
// APIコールが失敗するが、原因がわかりにくい

export async function getData() {
    if (!process.env.API_KEY) throw new Error('API_KEY is not set')
    const res = await fetch('https://external-service.com/data', {
        headers: {
            authorization: process.env.API_KEY
        },
    })
    return res.json()
}