export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    // must contain html and body tags.
    <html lang="en">
      <body>
        {children}
        <p>this sentence is deisplayed by app/layout.tsx</p>
      </body>
    </html>
  )
}