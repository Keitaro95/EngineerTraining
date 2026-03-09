from fastapi import APIRouter

from . import order, products, users

router = APIRouter(prefix="v2")

router.include_router(order.router)
router.include_router(users.router)
router.include_router(products.router)