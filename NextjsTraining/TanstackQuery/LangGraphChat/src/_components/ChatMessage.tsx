import { useQuery } from '@tanstack/react-query'
import { chatQueryOptions } from '../_lib/chat'
import { Message } from '../ui/message'

export default function ChatMessage({ question }: { question: string}) {
    
    // question：userからの文字入力
    // chatQueryOptions：keyとfetch関数の設定

    // experimental_streamedQuery が yield 
    // されるたびに TanStack Query のキャッシュ（data）を更新する。
    // useQuery はキャッシュの変化を監視しているので、data が更新されるたびに
    // 自動でコンポーネントが再レンダリングされる。
    // data.join(' ') が毎回単語を結合して表示するので
    // タイピングアニメーションのように見える、という仕組みです。
    const { error, data = [], isFetching } = useQuery(chatQueryOptions(question))

    if (error)
        return 'エラーが起こりました: ' + error.message

    // チャットの1セット（質問＋回答）を1つのChatMessageコンポーネントで表現
    return (
        <div>
            {/* 1つ目：ユーザーの質問バルーン（右寄せ・青） */}
            <Message message={{ content: question, isQuestion: true }} />
            {/* 2つ目：AIの回答バルーン（左寄せ・グレー） */}
            {/* data.join(' ') が毎回単語を増やして表示 */}
            <Message
                inProgress={isFetching}
                message={{ content: data.join(' '), isQuestion: false }}
            />
        </div>
    )
}