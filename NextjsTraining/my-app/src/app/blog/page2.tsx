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

https://nextjs.org/docs/app/getting-started/caching#putting-it-all-together