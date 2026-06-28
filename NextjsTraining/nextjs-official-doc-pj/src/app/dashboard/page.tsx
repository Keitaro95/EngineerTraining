import { getUser } from '../lib/user'

export default async function DashboardPage() {
    // getUserは でラップされているためReact.cache、同じリクエスト内の複数の呼び出しは、サーバー コンポーネントで直接呼び出された場合でも、クライアント コンポーネントでコンテキストを介して解決された場合でも、同じメモ化された結果を返します。
    const user = await getUser()
    return <h1>Dashboard for {user.name}</h1>
}