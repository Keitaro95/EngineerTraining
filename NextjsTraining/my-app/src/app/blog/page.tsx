// import { getPosts } from '@/lib/posts'
// import { Post } from '@/ui/post'
import { Suspense } from 'react'
import { db, posts } from '@/lib/db'
import BlogList from '@/components/BlogList'
import BlogListSkeleton '@/components/BlogListSkeleton'


// credentialとqueryはclientでやらない
// Server Component
// pagesはserver componentsだよ：デフォルトはサーバーサイド
export default async function BlogPage() {
    const allPosts = await db.select().from(posts)

    return (<div>
                <header>
                    <h1>Blog</h1>
                    <p>this page route is /blog </p>
                    <p>file is app/blog/page.tsx</p>
                </header>
                <main>
                    <Suspense fallback={<BlogSkeleton />}>
                        <BlogList />
                        // <ul>
                        //     {allPosts.map((post) => (
                        //         <li key={post.id}>{post.title}</li>
                        //     ))}
                        // </ul>
                    </Suspense>
                </main>
            </div>
        )
}