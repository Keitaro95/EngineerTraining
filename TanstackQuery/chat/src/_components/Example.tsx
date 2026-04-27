import { useState } from 'react'

export function Example() {
    const [ questions, setQuestions ] = useState<Array<string>>([])
    const [ currentQuestionå, setCurrentQuestion ] = useState('')

    const submitMessage = () => {
        setQuestions([...questions, currentQuestion])
        setCurrentQuestion('')
    }

    return (
        <div className="flex flex-col h-screen max-w-3xl mx-auto p-4">

            <h1>
                TanStack Chat Example
            </h1>

            <div>

            </div>

            <div>
                <input 
                    value={currentQuestion} 
                    onChange={(e) => setCurrentQuestion(e.target.value)}
                    onKeyDown{(e) => {
                        if (e.key === 'Enter') {
                            submitMessage()
                        }
                    }}
                    placeholder='メッセージを打ってね'
                />
                <button
                    onClick={submitMessage}
                    disabled={!currentQuestion.trim()}>

                
                </button>

            </div>



        </div>
    )
}