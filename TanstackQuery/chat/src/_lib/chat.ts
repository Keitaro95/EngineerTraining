import {
    queryOptions,
    experimental_streamedQuery as streamedQuery
} from '@tanstack/react-query'

const answers = [
  "I'm just an example chat, I can't really answer any questions :(".split(' '),
  'TanStack is great. Would you like to know more?'.split(' '),
]


function chatAnswer(_question: string) {
  return {
    async *[Symbol.asyncIterator]() {
      
      const answer = answers[Math.floor(Math.random() * answers.length)]
      let index = 0
      // 各単語を100〜400msのランダムな遅延をつけて1単語ずつ yield する
      while (index < answer.length) {
        // setTimeout単体はawaitできない。Promiseで包むとawaitできる
        await new Promise((resolve) =>
          setTimeout(resolve, 100 + Math.random() * 300),
        )
        // index++ は「今の値を使ってから、その後で1増やす」という後置インクリメント。
        yield answer[index++]
      }
    },
  }
}

export const chatQueryOptions = (question: string) => queryOptions({
    queryKey: ['chat', question],
    queryFn: streamedQuery({
      // streamedQuery はその yield のたびに
      //  TanStack Query のキャッシュを配列として更新 する
        streamFn: () => chatAnswer(question),
    }),
    staleTime: Infinity,
})