'use client'

import { use, useContext } from 'react'
import { UserContext } from '../user-provider'

export function Profile() {
    const userPromise = useContext(UserContext)
    if (!userPromise) {
        throw new Error ('useContext must be used within a UserProvider')
    }
    // Promise が未解決の間は最も近い <Suspense> の fallback を表示
    // 解決したら自動的に再レンダリング
    const user = use(userPromise)
    return <p>Welcome, {user.name}</p>
}