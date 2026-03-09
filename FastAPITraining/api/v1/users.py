from fastapi import APIRouter, Depends

from auth import require_admin

# ここから router.pyに繋げる routerインスタンスだよ
router = APIRouter(
    prefix="/users",
    tags=["users"], # swaggerに出るよ
    dependencies=[Depends(require_admin)] # この router固有の依存性
)

# エンドポイントは routerから始まるよ
@router.put("{user_id}")
async def update_user(user_id: int):
    pass

@router.get("/")
async def list_users():
    pass


@router.get("/{user_id}")
async def get_user(user_id: int):
    pass