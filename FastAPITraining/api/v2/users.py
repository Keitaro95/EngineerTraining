from fastapi import APIRouter, Depends

from auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"], # swaggerに出るよ
    dependencies=[Depends(get_current_user)]
)


@router.put("{user_id}")
async def update_user(user_id: int):
    pass

@router.get("/")
async def list_users():
    pass


@router.get("/{user_id}")
async def get_user(user_id: int):
    pass