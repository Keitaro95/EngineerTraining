'use client'

import { createPost } from "@/lib/actions"

import { useActionState, startTransition } from 'react'
import { createPost } from '@app/actions'
import { LoadingSpinner } from '@/app/ui/loading-spinner'

export function Button() {
    const [state, action, pending] = useActionState(createPost, false)

    // return <button formAction={createPost}>Create</button>
    return (
        <button onClick={() => startTransition(action)}>
            {pending ? <LoadingSpinner />: 'Create Post'}
        </button>
    )
}