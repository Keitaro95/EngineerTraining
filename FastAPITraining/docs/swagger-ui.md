Swagger UI / ReDoc の本番環境での制御
公式ドキュメント（https://fastapi.tiangolo.com/how-to/conditional-openapi/ ）に示されるパターンで環境に応じて切り替える。


from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    environment: str = "development"
    openapi_url: str = "/openapi.json"
settings = Settings()
app = FastAPI(
    openapi_url="" if settings.environment == "production" else settings.openapi_url,
    docs_url=None if settings.environment == "production" else "/docs",
    redoc_url=None if settings.environment == "production" else "/redoc",
)
補足情報：本番環境でのドキュメント制御

この設定により、settings.environmentが"production"の場合、FastAPIの動作は以下のようになります。
openapi_urlが空文字列""に設定され、OpenAPIスキーマのエンドポイントが無効化されます。
docs_urlとredoc_urlがNoneに設定され、Swagger UIとReDocのドキュメントUIが無効化されます。
ただし、ドキュメントでは、この制御に関する重要な注意点として、ドキュメントUIの非表示はAPIのセキュリティを向上させないと指摘されています。これは「隠蔽によるセキュリティ（Security through obscurity）」にすぎず、適切な認証・認可・入力バリデーションが本質的な対策であるとしています。


openapi_urlを空文字列""またはNoneに設定すると、OpenAPIスキーマエンドポイントが無効化される。Swagger UIとReDocはこのスキーマに依存するため、同時に機能停止する。本番ではOPENAPI_URL="" uvicorn main:appで起動すればよい。

ただし公式ドキュメントは重要な注意を記している。ドキュメントUIの非表示はAPIのセキュリティを向上させない。パスオペレーションは引き続き同じURLで機能する。これは「Security through obscurity（隠蔽によるセキュリティ）」にすぎず、適切な認証・認可・入力バリデーションが本質的な対策である。
include_in_schema=False でエンドポイントを非表示にする
# 個別エンドポイントを非表示
@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}
# ルーター全体を非表示
app.include_router(internal_router, include_in_schema=False)
# クエリパラメータを非表示
@app.get("/items/")
async def read_items(
    internal_key: str | None = Query(default=None, include_in_schema=False),
):
    ...
補足情報：include_in_schema=Falseについて

このパラメータは、OpenAPIスキーマ（Swagger UIやReDocの元データ）からエンドポイントやパラメータを除外するために使用されます。
個別エンドポイント、ルーター全体、クエリパラメータのいずれにも適用可能です。
重要な点として、この設定でエンドポイントがOpenAPIドキュメントから消えるだけで、API自体は引き続きリクエストに応答します。このため、「隠蔽によるセキュリティ（Security through obscurity）」に頼るのではなく、適切な認証・認可が本質的なセキュリティ対策であるとドキュメントでは指摘されています。


エンドポイントはOpenAPIから消えるだけで、引き続きリクエストに応答する。 完全な無効化フラグは存在しない。