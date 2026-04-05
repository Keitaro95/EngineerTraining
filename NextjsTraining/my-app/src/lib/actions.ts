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