/* <Playlists> can only fetch data after <Artist> completes because it needs the artistID: */

async function getArtist(username: string) {
    const res = await fetch(`https://api.example.com/artist/${username}`)
    return res.json()
}

async function getAlbums(username: string) {
    const res = await fetch(`https://api.example.com/artist/${username}/albums`)
    return res.json()
}

export default async function Page({
    params,
}: {
    params: Promise<{ username: string }>
}) {
    // ここはsequential
    const { username } = await params
    const artist = await getArtist(username)
    const albums = await getAlbums(username)

    // 複数リクエストを起こし、Promise.allでまつ
    // ただし、どちらかのfetchが失敗したらどちらも失敗する
    // 代替措置：Promise.allSelected
    const [artist, albums] = await Promise.all([artistData, albumsData])

    return (
        <>
            <h1>{artist.name}</h1>
            {/* <Suspense> があることで、Playlists のフェッチ中に フォールバックUI（Loading...）を表示 できます。ただし、Page 自体の getArtist が完了するまでは何も表示されません。 */}
            <Suspense fallback={<div>Loading...</div>}>
                <Playlists artistID={artist.id} />
            </Suspense>
        </>
    )
}

async function Playlists({ artistID }: { artistID: string }) {
//     Playlists が getArtistPlaylists(artistID) を await
//   ↓ 完了
// プレイリスト一覧がストリームで流れ込む
    const playlists = await getArtistPlaylists(artistID)

    return (
        <ul>
            {playlists.map((playlist) => (
                <li key={playlist.id}>{playlist.name}</li>
            ))}
        </ul>
    )
}