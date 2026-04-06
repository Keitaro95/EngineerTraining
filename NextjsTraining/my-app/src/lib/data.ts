import { cacheLife, cacheTag } from 'next/cache'

type Post = {
    id: string
    title: string
    likes: number
}

const posts: Post[] = [
    { id: '1', title: 'First Post', likes: 10 },
    { id: '2', title: 'Second Post', likes: 5 },
]

export async function getPost(id: string): Promise<Post> {
    const post = posts.find((p) => p.id === id)
    if (!post) throw new Error(`Post not found: ${id}`)
    return post
}

// cacheLife('hours')と
// cacheTag('products')
export async function getProducts() {
    'use cache'
    // cacheLife('hours')
    cacheTag('products')
    cacheLife({
        stale: 3600, // 1hourキャッシュ提供
        revalidate: 7200, // 2h再検証
        expire: 86400, // 1日で期限切れ
    })

    return db.query('SELECT * FROM products')
}

