import {
    queryOptions,
    experimental_streamedQuery as streamedQuery
} from '@tanstack/react-query'

type Chunk =
  | { type: 'token'; content: string }
  | { type: 'tool'; name: string; args?: unknown }
  | { type: 'done' }


// async function* = 非同期ジェネレーター関数。
// 通常の async 関数は値を1回だけ return して終わるが、
// ジェネレーターは yield を使って値を少しずつ複数回送り出せる。
// これにより、サーバーからの応答を受け取るたびに呼び出し元へ逐次データを渡せる。
async function* chatAnswer(question: string, signal: AbortSignal) {
  // fetch でサーバーにリクエストを送信。
  // signal は AbortController のシグナルで、キャンセルが発生したら
  // fetch も自動的に中断される。
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
    signal,
  })
  // レスポンスがエラーか、ストリームボディが無い場合は例外を投げて終了。
  if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`)

  // res.body は ReadableStream<Uint8Array>（バイナリ）のため、
  // TextDecoderStream でパイプして文字列ストリームに変換してから Reader を取得する。
  const reader = res.body.pipeThrough(new TextDecoderStream()).getReader()
  let buffer = ''
  while (true) {
    // reader.read() はストリームから1チャンクを非同期で読み取る。
    // done が true になるとストリーム終端（サーバーが接続を閉じた）を意味する。
    const { done, value } = await reader.read()
    if (done) break
    // ネットワークのチャンク境界は行の区切りと一致しないことがあるため、
    // 受信データをバッファに蓄積してから改行で分割する。
    buffer += value
    const lines = buffer.split('\n')
    // pop() で最後の要素（まだ改行が届いていない可能性のある不完全な行）を取り出し、
    // 次の read() の結果と結合するためにバッファへ戻す。
    buffer = lines.pop() ?? ''
    for (const line of lines) {
      if (!line.trim()) continue // 空行はスキップ
      // サーバーは1行ごとに JSON を送ってくる（NDJSON 形式）。
      // 各行をパースして Chunk 型として扱う。
      const chunk = JSON.parse(line) as Chunk
      // type が 'token' のときだけテキスト断片を yield する。
      // yield するたびに streamedQuery がキャッシュを更新し、
      // UI 側でリアルタイムに文字が追加されていくように見える。
      if (chunk.type === 'token') yield chunk.content
      // tool呼び出しを別マーカーで出したい場合はここで yield を分ける
    }
  }
}

export const chatQueryOptions = (question: string) => 
  queryOptions({
    queryKey: ['chat', question],
    //通常の queryFn は Promise を1回解決して終わりですが、streamedQuery は
    // yield のたびにキャッシュを配列として追記更新 します。
    // ChatMessage.tsx の data.join(' ') がタイピングアニメーションに見えるのはこの仕組みのためです。
    queryFn: streamedQuery({
      // streamedQuery はその yield のたびに
      //  TanStack Query のキャッシュを配列として更新 する
        streamFn: ({ signal }) => chatAnswer(question, signal),
    }),
    staleTime: Infinity,
})