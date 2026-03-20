// []をつけるとこでダイナミックルーティングになる

// ここで、 dbやapiからくる値をslugにしている
export async function generateStaticParams() {
    // const posts = await fetch('/api/posts').then(res => res.json())

    const DummyPosts = [
        { slug: "hello-world" },
        { slug: "nextjs-tips" },
        { slug: "abc" },
    ]

    // 本当は postsをmapするけどここではdammyを使っている
    return DummyPosts.map((DummyPosts) => ({
        slug: DummyPosts.slug
    }))
}

// 
export default async function Page({ params }: { params: Promise<{ slug: string }>}) {
    const { slug } = await params
    return (<div>
                <h1>{slug}</h1>
                <p>このページは app/boag/[slug]/page.tsxの内容が表示されています</p>
                <p>slugは、urlが "/blog/abc" なら,h1にslug名 abc が表現されているはずです</p>
            </div>)
}