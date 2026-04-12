
HTTP HEADメソッドの実践的用途
HEADメソッドはGETと同一だがレスポンスボディを返さない。リソースの存在確認、Content-Lengthによるファイルサイズ事前チェック、ETag/Last-Modifiedによるキャッシュ検証に使う。
2.2 HEADメソッド：メタデータの効率的な取得
HEADメソッドは、レスポンスボディを含まない点を除けばGETメソッドと完全に同一である。このメソッドは、リソースの実体を取得することなく、リソースのメタデータ（HTTPヘッダー）のみを取得するために使用される。
主なユースケース
キャッシュ検証: Last-ModifiedやETagヘッダーを確認し、ローカルキャッシュが有効か判断する。
リソース存在確認: 大容量ファイルのダウンロード前に、ファイルが存在するか（404でないか）を確認する。
帯域幅の節約: Content-Lengthヘッダーを確認し、ダウンロードすべきデータサイズを事前に把握する。
CDNのキャッシュウォームアップ、ファイルダウンロード前のサイズ確認（プログレスバー表示用）、APIの軽量ヘルスチェックなどが実務のユースケースとなる。

```Py
from fastapi import Response

@app.head("/items/{item_id}")
async def get_item_headers(item_id: str, response: Response):
    # 重いデータ取得を行わず、存在確認やメタデータ取得のみを実行
    exists = await db.check_exists(item_id)
    if not exists:
        raise HTTPException(status_code=404)
    response.headers["X-Custom-Meta"] = "meta-value"
    return response # ボディは返さない


```




## メモリ管理
run_in_threadpool ：　AnyIO（asyncio + Trio対応）

BackgroundTasksの内部実装と制約
StarletteのBackgroundTasksはレスポンス送信後にタスクを逐次実行する（並行ではない）。
sync関数はrun_in_threadpool経由でスレッドプールを消費する。

重要な制約: インプロセス実行のためワーカークラッシュでタスク消失、リトライ機構なし、ステータス追跡不可、タスク失敗時に後続タスクは実行されない。
BackgroundTasks vs Celery の使い分け
BackgroundTasksを使う場面: 軽量なfire-and-forget（ログ送信、キャッシュ無効化）、数秒以内に完了、失敗許容可能な場合。Celeryを使う場面: CPU集約処理（画像処理、ML推論）、10秒超のタスク、信頼性/リトライが必要（決済、データパイプライン）、定期実行（Celery Beat）、複数サーバー分散が必要な場合。
メモリ使用量の見積もり方法
Total Memory ≈ N_workers × Memory_per_worker + OS_overhead

各ワーカーは独立したOSプロセスでメモリを共有しない。典型的な目安は、最小FastAPIアプリで30-50MB/worker、ORM付き中規模アプリで50-150MB/worker、MLモデル搭載重量アプリで200MB〜数GB/workerとなる。非同期ワーカーの場合、各ワーカーが既に数千の同時接続を処理できるため、ワーカー数はCPUコア数程度が適切だ（同期の2N+1公式は不要）。

