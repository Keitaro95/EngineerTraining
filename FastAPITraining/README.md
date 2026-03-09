

uvicorn --workers 4 

osの中に 箱が4つできます


1つの箱　Worker Process
1. event loop (main thread)
   async def 担当
   i/oが終わるのを待たずに次の処理を進めていく、ような
   ⚠️ time.sleepなどの大きい処理は❌
   event loopを止めるので
2. thread pool (sub thread)
   def 担当
   デフォルトで40個のスレッド=task担当ボックスがあります
   def エンドポイント

