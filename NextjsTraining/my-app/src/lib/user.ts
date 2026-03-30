import { cache } from 'react'

// 同一リクエスト内で何度 getUser() を呼んでも、実際の fetch は 1回だけ
// リクエストをまたいでキャッシュしない（ユーザーAのデータがユーザーBに漏れるのを防ぐ）

export const getUser = cache(async () => {
    const res = await fetch('https://api.example/com/user')
    return res.json()
})

