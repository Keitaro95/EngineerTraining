import Link from 'next/link'
import ThemeProvider from './theme-provider'
import UserProvider from './user-provider'
import { getUser } from './lib/user'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // awaitせずPromise のまま渡すことでストリーミングが維持され、UI が段階的に表示される
  const userPromise = getUser()

  return (
    // must contain html and body tags.
    <html lang="en">
      <body>
        <nav>
          {/* Linkの働き：リンクにホバーされた時、またはビューポートに入った時prefetchする*/}
          {/* ↓ Layoutにより、{children}以外は再レンダリングしない */}
          <Link href="/blog">Blog</Link>
        </nav>
        <p>this sentence is deisplayed by app/layout.tsx</p>
        {/* ↓ ここだけページごとに差し替わる */}
        <ThemeProvider>{children}</ThemeProvider>
        <UserProvider userPromise={userPromise}>{children}</UserProvider>
      </body>
    </html>
  )
}