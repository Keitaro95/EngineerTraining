{/* <Playlists> can only fetch data after <Artist> completes because it needs the artistID: */}


export default async function Page({
    params,
}: {
    params: Promise<{ username: string }>
}) {
    const { username } = await params

    const artist = await getArtist(username)


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