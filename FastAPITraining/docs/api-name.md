
プレフィックス連結の結果
main.py        v1/router.py     users.py          最終パス
prefix="/api" + prefix="/v1"  + prefix="/users" + get("/")        = GET  /api/v1/users/
                                                + get("/{user_id}") = GET  /api/v1/users/{user_id}
                                                + put("/{user_id}") = PUT  /api/v1/users/{user_id}

本番で使うAPIバージョニング
v2を追加するとき、v1のコードに一切触れずに新バージョンを生やせる。
# app/main.py
from app.api.v1.router import router as v1_router
from app.api.v2.router import router as v2_router

app = FastAPI()

app.include_router(v1_router, prefix="/api")   # /api/v1/...
app.include_router(v2_router, prefix="/api")   # /api/v2/...

同じルーターを2回mountして /api/latest でも公開するパターンもある。
app.include_router(v2_router, prefix="/api")            # /api/v2/...
app.include_router(v2_router, prefix="/api/latest")     # /api/latest/... （v2と同一）

ただしこれはOpenAPIスキーマで operation_id が衝突するため
本番では generate_unique_id_function を設定するか、片方のルーターに別の tags を振る必要がある。安易にやると Swagger UI が壊れるので注意。
dependenciesの伝播
エンドポイント全部に適用できるからおすすめ
GET /api/v1/users/ にリクエストが来ると
verify_api_key → require_admin の順で実行される。
# v1全体に認証を適用
v1_router = APIRouter(prefix="/v1", dependencies=[Depends(verify_api_key)])
# usersルーターにはさらにロール検証を追加
users_router = APIRouter(prefix="/users", dependencies=[Depends(require_admin)])
v1_router.include_router(users_router)

