'use client'
 
import { unstable_catchError as catchError, type ErrorInfo } from 'next/error'
 
function ErrorFallback(
  props: { title: string },
  { error, unstable_retry }: ErrorInfo
) {
  return (
    <div>
      <h2>{props.title}</h2>
      <p>{error.message}</p>
      <button onClick={() => unstable_retry()}>Try again</button>
    </div>
  )
}
 
export default catchError(ErrorFallback)