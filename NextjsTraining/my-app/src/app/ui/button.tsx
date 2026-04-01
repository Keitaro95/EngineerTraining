'use client'

import { createPost } from "@/lib/actions"

export function Button() {
    return <button formAction={createPost}>Create</button>
}