import { useState } from 'react'

export function Example() {
    const [ questions, setQuestions ] = useState<Array<string>>([])
    const [ currentQuestions, setCurrentQuestion ] = useState('')

    const submitMessage = () => {
        setQuestions([...questions, currentQuestion])
        setCurrentQuestion('')
    }

    return (
        <div className="flex flex-col h-screen max-w-3xl mx-auto p-4">

            <h1>

            </h1>

            <div>

            </div>

            <div>
                <input 
                    value={currentQuestion} />

            </div>



        </div>
    )
}