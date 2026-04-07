// []をつけるとこでダイナミックルーティングになる

// key, valueのレコード
const dummyPosts: Record<string, { title: string; content: string }> = {
        "hello-world": { title: "Hello World", content: "これは初めのコンテンツ"},
        "nextjs-tips": { title: "Next.js Tips", content: "便利なTipsを紹介します"},
        "abc": { title: "ABC", content: "テスト投稿です"},
    }

    

export async function generateStaticParams() {
    // ここで、 dbやapiからくる値をslugにしている
    // const posts = await fetch('/api/posts').then(res => res.json())

    // dummyPosts slugをキーに（"hello-world", "nextjs-tips", "abc"）を配列にして返す
    return Object.keys(dummyPosts).map((slug) => ({ slug: slug }))
}

export async function getPost(slug: string, ) {
    return dummyPosts[slug] ?? null
}

import { notFound } from "next/navigation";
export default async function Page({
     params,
    }: {
        params: Promise<{ slug: string }>
    }) {
    const { slug } = await params
    const post = await getPostBySlug(slug)

    if (!post) {
        notFound()
    }
        return (
        <div>
            <h1>this slug is {slug}</h1>
            <h1>this title is {post.title}</h1>
            <p>this content: {post.content}</p>

            <p>このページは app/boag/[slug]/page.tsxの内容が表示されています</p>
            <p>slugは、urlが /blog/abc なら,h1にslug名 abc が表現されているはずです</p>
        </div>)
    }


import Image from 'next/image'
 
async function PostImage({
  imageFilename,
  alt,
}: {
  imageFilename: string
  alt: string
}) {
    // const { default: image } = await import(
    // `@/content/blog/images/${imageFilename}`
    // )
  const { default: image } = await import(
    `../content/blog/images/${imageFilename}`
  )
  // image contains width, height, and blurDataURL
  return <Image src={image} alt={alt} />
}