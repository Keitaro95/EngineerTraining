"""
全体のルーターを統制する。api/v1
main.pyで吐き出してます。
"""

from fastapi import APIRouter, Depends

from . import order, products, users
from auth import verify_api_key


# v1　routerこれだよ
router = APIRouter(
    prefix="/v1",
    tags=["items"], # OpenAPI表示名
    # dependenciesはルーター内の全ルートで事前実行される戻り値はパスオペレーション関数に渡されない。
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}}, # swagger UI 表示用
    redirect_slashes=True, # v1/users/は v1/usersへ
    deprecated=None,
    include_in_schema=True, # swaggerに表示するかどうか
    )

# routerの中にはこれがあるよ
router.include_router(order.router)
router.include_router(users.router)
router.include_router(products.router)
