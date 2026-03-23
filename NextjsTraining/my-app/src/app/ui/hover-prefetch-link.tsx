// Linkを使いたくない場合


'use client'

import Link from 'next/link'
import { useState } from 'react'

export function HoverPrefetchLink({
    href,
    children,
}: {
    href: string
    children: React.ReactNode
}) {
    const [active, setActive] = useState(false)

    return (
        // onMouseEnter でマウスが乗った瞬間に active = true になり、prefetch が null（= Next.js のデフォルト動作）に切り替わります。
        <Link
            href={href}
            prefetch={active ? null : false}
            onMouseEnter={() => setActive(true)}
        >
            {children}
        </Link>
    )
}