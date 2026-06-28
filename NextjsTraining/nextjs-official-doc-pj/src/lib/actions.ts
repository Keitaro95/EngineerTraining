'use server' // ここに書いてもいい


import { auth } from '@/lib/auth'
import { refresh } from 'next/cache'

export async function createPost(formData: FormData) {
    'use server'
    const session = await auth()
    if (!session?.user) {
        throw new Error('Unauthorized')
    }

    const title = formData.get('title')
    const content = formData.get('content')

    refresh()
}

export async function deletePost(formData: FormData) {
  'use server'
  const session = await auth()
  if (!session?.user) {
    throw new Error('Unauthorized')
  }
 
  const id = formData.get('id')
 
  // Verify the user owns this resource before deleting
  // Mutate data
  // Revalidate cache
}

// revalidateTag；サーっバーアクションとルートハンドラー
// バックグラウンドでリフレッシュが起こる
// キャッシュデータをタグ単位で無効化
// app/lib/actions.ts (Server Action)
'use server'
import { revalidateTag } from 'next/cache'

export async function updateProduct(id: string) {
  // DBを更新
  await db.update('products', id, { ... })

  // 'products' タグが付いたキャッシュをすべて無効化
  revalidateTag('products')
}

// updateTag：サーバーアクションのみ
// 直ちにキャッシュを消す
import { updateTag } from 'next/cache'
import { redirect } from 'next/navigation'

export async function createPost(formData: FormData) {
  const post = await db.post.create({
    data: {
      title: formData.get('title'),
      content: formData.get('content'),
    },
  })

  updateTag('posts')
  redirect(`/posts/${post.id}`)
}


// タグにキャッシュされたデータを無効化
import { revalidatePath } from 'next/cache'

export async function updateUser(id: string) {
  revalidatePath('/profile')
}