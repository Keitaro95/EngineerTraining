

// isQuestion が true（質問・送信側）
// justify-end → 右寄せ
// bg-blue-500 text-white → 青背景・白文字

// isQuestion が false（回答・受信側）
// justify-start → 左寄せ
// bg-gray text-gray-800 → グレー背景・濃い文字

export function Message({
    inProgress,
    message,
}: {
    inProgress?: boolean
    message: { content: string; isQuestion: boolean }
}) {
    return (
        <div
            className={`flex ${message.isQuestion ? 'justify-end' : 'justify-start'}`}>
                <div
                    className={`max-w-[80%] rounded-lg p-3 ${message.isQuestion
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray text-gray-800'
                    }`}
                >
                    {message.content}
                    {inProgress ? '...' : null}
                </div>
        </div>
    )
}