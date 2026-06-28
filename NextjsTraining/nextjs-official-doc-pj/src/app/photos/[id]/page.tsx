export default async function PhotoPage({ params }: { params: Promise<{id: string}>}) {
    const { id } = await params
    return (
        <p>これはphotosページ {id}のメインぺ〜じ</p>
    )
}