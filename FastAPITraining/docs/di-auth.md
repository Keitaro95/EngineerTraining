4. サーバーサイドの実装：FastAPIによる受信と処理
FastAPI側では、前述のPydanticモデルを用いてリクエストボディを受け取り、同時にヘッダー情報も検証する。
4.1 依存性注入（Dependency Injection）によるヘッダー処理
FastAPIの強力な機能の一つである依存性注入システムを利用して、認証ヘッダーとカスタムヘッダーを処理する。ヘッダー取得には Header() を、認証には HTTPBearer を使用するのが標準的である 7。

Python


from typing import Annotated
from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 前述のモデル定義ファイルからインポート
# from models import OrderDetail

app = FastAPI()

# Bearerトークンの抽出用スキーム
security = HTTPBearer()

async def verify_token(credentials: Annotated):
    """
    AuthorizationヘッダーのBearerトークンを検証する依存関係関数。
    実際の実装ではJWTのデコードやDB照合を行う。
    """
    token = credentials.credentials
    if token!= "valid_secret_token_123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効な認証トークンです",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@app.post("/v1/orders")
async def create_order_endpoint(
    order: OrderDetail,
    token: Annotated,
    x_correlation_id: Annotated[str | None, Header()] = None,
    x_client_version: Annotated[str | None, Header()] = None
):
    """
    5階層のJSONボディとヘッダーを受け取るエンドポイント
    """
    print(f"Processing Order: {order.order_id}")
    print(f"Client Version: {x_client_version}")
    print(f"Correlation ID: {x_correlation_id}")

    # ここでビジネスロジックを呼び出す
    # process_order(order)

    return {"message": "Order received", "order_id": order.order_id}