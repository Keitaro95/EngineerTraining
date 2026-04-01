import Carousel from './carousel'
import { Suspense } from 'react'

import { Profile } from './ui/profile'
// import { createPost } from '@/lib/actions'とせずコンポーネントの中に書く

export default async function Page({
  params, // /blog/[slug] → { slug: "hello" }
  searchParams, // /blog/hello?filters=active → { filters: "active" }
}: {
  params: Promise<{ slug:string }>
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}) {

  async function createPost(formData: FormData) {
    'use server'
    //...
  }
  const { slug } = await params
  const filters = (await searchParams).filters
  return (
          <Suspense fallback={<div>Loading profile...</div>}>
            <Profile />
            <div>
              <h1>Hello Next.js!</h1>
              <p>this query is {filters}</p>
              <p>this page slug is {slug}</p>
              <Carousel />
            </div>
          </Suspense>
          
        )
}