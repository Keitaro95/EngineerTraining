// 静的コンテンツ、ダイナミックコンテント、ストリーミングを合算
import { Suspense } from 'react'
import { cookies } from 'next/headers'
import { cacheLife, cacheTag, updateTag } from 'next/cache'
import Link from 'next/link'

export default function BlogPage() {
    return (
        <>
        {/* Static content 自動プレレンダリング*/}
        <header>
            <h1>Our Blog</h1>
            <nav>
                <Link href="/">Home</Link> | <Link href="/about">About</Link>
            </nav>
        </header>

        {/* Static Shell含んだキャッシュされたコンテント */}
        <BlogPosts />

        {/* リクエストしてストリームするダイナミックコンテンツ */}
        <Suspense fallback={<p>Loading your prefernces...</p>}>
            <UserPreferences />
        </Suspense>

        {/* Mutation - キャッシュを再更新するサーバーアクション。 */}
        <Suspense fallback={<p>Loading...</p>}>
            <CreatePost />
        </Suspense>
        </>
    )
}

// 1時間ごとにキャッシュされる
async function BlogPosts() {
    'use cache'
    cacheLife('hours')
    // // 呼び出しによってupdateTagブログ記事のキャッシュが即座に期限切れとなり、次の訪問者が新しい記事を見ることができます。
    cacheTag('posts')

    const res = await fetch('https://api.vercel.app/blog')
    const posts = await res.json()

    return (
        <section>
            <h2>Latest Posts</h2>
            <ul>
                {posts.slice(0, 5).map((post: any) => (
                    <li key={post.id}>
                        <h3>{post.title}</h3>
                        <p>
                            By {post.author} on {post.date}
                        </p>
                    </li>
                ))}
            </ul>
        </section>
    )
}

//管理者専用画面でキャッシュを再評価する
async function CreatePost() {
    // 管理者かどうか
    const isAdmin = (await cookies()).get('role')?.value === 'admin'
    if (!isAdmin) return null

    async function createPost(formData: FormData) {
        'use server'
        await db.post.create({ data: {title: formData.get('title')} })
        // キャッシュ更新に使うタグ
        updateTag('posts')
    }
    return (
        <form action="{createPost}">
            <input type="title" placeholder="Post title" required/>
            <button type="submit">Publish</button>
        </form>
    )
}
