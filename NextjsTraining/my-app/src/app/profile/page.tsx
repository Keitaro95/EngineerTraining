import { cookies } from 'next/headers'
import { Suspense } from 'react'

export default function Page() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <ProfileContent />
        </Suspense>
    )
}

// ランタイムデータを読む
async function ProfileContent() {
    const session = (await cookies()).get('session')?.value
    return <CachedContent sessionId={session} />
}

async function CachedContent({ sessionId }: { sessionId: string }) {
    'use cache'
    // sessionIdをキャッシュキーに取る
    const data = await fetchUserData(sessionId)
    return <div>{data}</div>
}