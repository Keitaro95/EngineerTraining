'use client'

import { useState } from 'react'

export default function LikeButton({ likes }: { likes: number }) {
    const [count, setCount] = useState(likes)

    return (
        <button onClick={() => setCount(count + 1)}>
            Like ({count})
        </button>
    )

}