// このtailwind表現そのまま使える

import { useState } from 'react'
import ChatMessage from './ChatMessage'

export function Example() {
    const [ questions, setQuestions ] = useState<Array<string>>([])
    const [ currentQuestion, setCurrentQuestion ] = useState('')

    // 送信
    const submitMessage = () => {
        // setQuestionを介して
        // 「今まである質問リスト
        // の末尾に、今入力中の質問を1つ追加した新しい配列をセットする」 
        setQuestions([...questions, currentQuestion])
        // setCurrentQuestionを介してcurrentQuestionを空にする
        setCurrentQuestion('')
    }

    return (
        // flex：並べる
        // flex-col：縦に
        <div className="flex flex-col h-screen max-w-3xl mx-auto p-4">

            <h1 className="text-3xl font-bold text-gray-800">
                TanStack Chat Example
            </h1>

            {/* overflow-y-auto：縦にscrollbarを自動表示
            メッセージが増えてもこのdivの外には出さない
            mb-4：下の余白
            space-y-4：子要素  */}
            <div className="overflow-y-auto mb-4 space-y-4">
                {questions.map((question) => (
                    <ChatMessage key={question} question={question} />
                ))}
            </div>
            {/* flex：横に並べる
            items-center：縦方向を中央揃え */}
            <div className='flex items-center space-x-2'>
                {/* value={currentQuestion} と onChange がセット */}
                <input
                    /*
                    flex: 1
                    → 横幅の余りをすべてこのinputが使う
                    → ボタンの幅だけ残して、あとは全部inputの幅になる
                    */
                    className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-100"
                    value={currentQuestion} 
                    onChange={(e) => setCurrentQuestion(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                            submitMessage()
                        }
                    }}
                    placeholder='メッセージを打ってね'
                />
                <button
                    onClick={submitMessage}
                    disabled={!currentQuestion.trim()}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded-2xl shadow-md transition"
                >
                    <span>Send</span>
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    >
                        <path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z" />
                        <path d="m21.854 2.147-10.94 10.939" />
                    </svg>
                </button>
            </div>
        </div>
    )
}