
https://docs.google.com/document/d/1ISMQLgQfnC7Z0XhsqW5j6YWB7-9nnrO5wtPWM0wiQsw/edit?tab=t.0


async def はFastAPIのメインスレッドで常にIO待ちをしながら起こせる
だから他の処理を待って、他にも処理させたいことに使う
I/O待ちイベント
非同期イベント
リクエスト

def 
計算処理
部屋の中で単に起こしたいこと



uvicorn --workers 4 

osの中に 箱が4つできます


1つの箱　Worker Process
1. event loop (main thread)
   async def 担当
   i/oが終わるのを待たずに次の処理を進めていく、ような
   ⚠️ time.sleepなどの大きい処理は❌
   event loopを止めるので
   イメージ：1人の料理人が、コンロを何個も同時に監視する（I/O待ちを有効活用）。
2. thread pool (sub thread)
   def 担当
   デフォルトで40個のスレッド=task担当ボックスがあります
   def エンドポイントが呼ばれる
   →run_in_threadpoll
   → このボックスの1つ占有
   イメージ：注文ごとに別の料理人を呼んで、1つの鍋を専有させる。


依存関係の実行は「ルーターの依存関係が最初に実行され、次にデコレータ内の依存関係、そして通常のパラメータ依存関係が実行され」ます。