ヘルスチェックエンドポイント設計（liveness vs readiness）
Kubernetesの2種類のプローブは設計思想が根本的に異なる。Livenessプローブは「コンテナを再起動すべきか？」を判断するもので、失敗するとPodが再起動される。Readinessプローブは「トラフィックを受け入れられるか？」を判断し、失敗するとServiceから除外される（再起動はしない）。



FastAPIヘルスチェックエンドポイント
from datetime import datetime, timezone
from fastapi import FastAPI, Response, status
@app.get("/health/live", include_in_schema=False)
async def liveness():
    """Livenessプローブ: 外部依存をチェックしない。高速に200を返す。"""
    return {"status": "alive"}
@app.get("/health/ready", include_in_schema=False)
async def readiness(response: Response):
    """Readinessプローブ: DB、Redis等の外部依存をチェック。"""
    checks = {}
    all_healthy = True
    try:
        await asyncio.wait_for(db.execute(text("SELECT 1")), timeout=5.0)
        checks["database"] = "connected"
    except Exception:
        checks["database"] = "disconnected"
        all_healthy = False
    if not all_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "checks": checks}
    return {"status": "ready", "checks": checks}
Kubernetes YAMLでの設定例
Kubernetes YAMLでの設定例：
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  periodSeconds: 15
  failureThreshold: 3
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  periodSeconds: 10
  failureThreshold: 3
補足:
ドキュメント内でのベストプラクティスに基づき、Livenessプローブ（/health/live）は外部依存をチェックせずにPodの再起動判断に用いられ、Readinessプローブ（/health/ready）はDB接続などの外部依存チェックに用いられています。また、これらのヘルスチェックエンドポイントはinclude_in_schema=Falseが設定されており、OpenAPIドキュメントから除外されています。


ベストプラクティスとして、livenessは外部依存を絶対にチェックしないこと（DBダウンでPod再起動の無限ループを防ぐ）、readinessでは全依存にタイムアウト付きチェックを行うこと、ヘルスチェックはinclude_in_schema=FalseでAPIドキュメントから除外すること、ログミドルウェアからも除外してログノイズを防ぐことが重要だ。

