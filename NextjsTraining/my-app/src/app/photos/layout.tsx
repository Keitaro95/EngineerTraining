export default function PhotosRayout({
    children,
    modal, // @modal が追加
}: {
    children: React.ReactNode;
    modal: React.ReactNode;
}) {
    return (
        <html>
            <body>
                {children}
                {modal}
            </body>
        </html>
    )
}