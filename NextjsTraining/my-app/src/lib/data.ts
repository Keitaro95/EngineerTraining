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