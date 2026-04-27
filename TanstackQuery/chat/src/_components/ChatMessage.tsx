import { useQuery } from '@tanstack/react-query'
import { chatQueryOptions } from '../_lib/chat'
import { Message } from './message'

export default function ChatMessage({ question }: { question: string}) {
    // fetch関数をuseQueryで丸めて状態を取得
    const { error, data = [], isFetching } = useQuery(chatQueryOptions(question))

    if (error)
        return 'エラーが起こりました: ' + error.message

    return (
        <div>
            <Message message={{ content: question, isQuestion: true }} />
            <Message
                inProgress={isFetching}
                message={{ content: data.join(' '), isQuestion: false }}
            />
        </div>
    )
}