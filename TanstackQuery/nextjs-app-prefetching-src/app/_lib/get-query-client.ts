import {
    QueryClient,
    defaultShouldDehydrateQuery,
    environmentManager,
} from '@tanstack/react-query'


// QueryClientは棚。同じリクエストなら同じ棚が返る。
// サーバーでデータをフェッチ・キャッシュ
// SSR環境での使用を想定。QueryClient を初期設定付きで生成するファクトリ関数です。
function makeQueryClient() {
    return new QueryClient({
        // 初期設定
        defaultOptions: {
            queries: {
                // cache持続時間=60秒
                staleTime: 60 * 1000,
            },
            // ここで乾燥させる。キャッシュをシリアライズしてクライアントに渡す
            dehydrate: {
                // どのクエリをシリアライズ対象にするか
                shouldDehydrateQuery: (query) =>
                    // デフォルトの success +
                    defaultShouldDehydrateQuery(query) ||
                    // fetching　中のクエリも含める
                query.state.status === 'pending',

            }
        }
    })
}

let browserQueryClient: QueryClient | undefined = undefined

// QueryClient(cacheを置いておく棚)を作る関数
export function getQueryClient() {
    // この関数が使われる場所がサーバーなら
    // 新しいクエリクライアントを使ってね
    //使い回しがあるとユーザー間でキャッシュが混ざるセキュリティリスクがあるから
    if (environmentManager.isServer()) {
        return makeQueryClient()
    } else {
        // この関数が使われる場所がブラウザなら
        // 一度使ったクエリクライアントを使っていいよ。
        // クライアント側がキャッシュを保持し続けるため
        if(!browserQueryClient) browserQueryClient = makeQueryClient()
            return browserQueryClient
    }
}