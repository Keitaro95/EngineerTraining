"""
全体のルーターを統制する。api/v1
main.pyで吐き出してます。
"""

from fastapi import APIRouter, Depends

from . import order, products, users
from auth import verify_api_key


# v1　routerこれだよ
router = APIRouter(prefix="/v1", dependencies=[Depends(verify_api_key)])

# routerの中にはこれがあるよ
router.include_router(order.router)
router.include_router(users.router)
router.include_router(products.router)
