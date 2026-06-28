// https://nextjs.org/docs/app/getting-started/linking-and-navigating#streaming#slow-networks
// 遅延ネットワークの時 useLinkStatusを置くのがいい

'use client'

import { useLinkStatus } from 'next/link'

export default function LoadingIndicator() {
    const { pending } = useLinkStatus()
    return (
        // pending状態がtrueならcssでpendingクラス
        <span aria-hidden className={`link-hint ${pending ? 'is-pending' : ''}`} />
    )
}