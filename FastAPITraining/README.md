
https://docs.google.com/document/d/1ISMQLgQfnC7Z0XhsqW5j6YWB7-9nnrO5wtPWM0wiQsw/edit?tab=t.0


### async def = event loop (main thread)
i/oまたない
1人の料理人が、コンロを何個も同時に監視する（I/O待ちを有効活用）。
だから他の処理を待って、他にも処理させたいことに使う
I/O待ちイベント
非同期イベント
リクエスト

### def 
計算処理
部屋の中で単に起こしたいこと
thread pool (sub thread)
デフォルトで40個のスレッド=task担当ボックスがあります
イメージ：注文ごとに別の料理人を呼んで、1つの鍋を専有させる。


### リクエスト処理フロー

Socket Accept 
→ HTTP Parse (httptools/h11) 
→ ASGI App Dispatch
→ Starlette Middleware Chain 
→ FastAPI Routing 
→ 依存関係解決
→ エンドポイント実行（async def: イベントループ直接 / def: スレッドプール）
→ レスポンスシリアライズ → Socket送信



ワーカープロセスモデルは2種類ある。
Uvicorn単体（uvicorn --workers N）はspawnでワーカーを作成する。

Gunicorn + Uvicorn（gunicorn -k uvicorn.workers.UvicornWorker）
はpre-forkモデルで、max-requestsによるワーカー再起動やローリングアップグレードなど成熟したプロセス管理を提供する。
