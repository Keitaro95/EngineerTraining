


function ChatMessage({ question }: { question: string}) {

    // fetch関数をuseQueryで丸めて状態を取得
    const { erroe, data = [], isFetching } = useQuery(chatQueryOptions(question))
}