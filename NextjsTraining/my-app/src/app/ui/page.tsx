import Link from "next/link"

const dummyPosts = [
        { slug: "hello-world", title: "Hello World" },
        { slug: "nextjs-tips", title: "Next.js Tips" },
        { slug: "abc", title: "ABC"},
    ]

export async function getPosts() {
    return dummyPosts
}

export default async function Post() {
    const posts = await getPosts()
    return (
        <div>
            <p>このページはNextjsのLinkでURL表示されています</p>
            <ul>
                {posts.map((post) => (
                    <li key={post.slug}>
                        <Link href={`/blog/${post.slug}`}>{post.title}</Link>
                    </li>
                ))}
            </ul>
        </div>
    )
}