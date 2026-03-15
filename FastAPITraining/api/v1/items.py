from fastapi import APIRouter, Depends, HTTPException

from schemas.items import ResponseItem
from models.items import Item
from db import DBSessionDep


# ここから router.pyに繋げる routerインスタンスだよ
router = APIRouter(
    prefix="/items",
    tags=["items"], # swaggerに出るよ
    dependencies=[Depends(require_admin)] # この router固有の依存性
)

# エンドポイントは routerから始まるよ
@router.patch("/items/{item_id}", response_model=ResponseItem)
async def update_item(item_id: int, item: Item, item_update: ItemUpdate, db: DBSessionDep):
    result = await db.execute(select(Item).where(Item.id == item_id))
    db_item = result.scalars().first()
    if not db_item:
        raise HTTPException(status_code=404)
    """
    明示的に値が更新されたフィールドのみを抽出します。
    """
    update_data = item_update.model_dump(exclude_unset=True)

    # 既存データにマージ
    for field, value in update_data.items():
        setattr(db_item, field, value)
        
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

    
    """
    こんなのもあるよ
    既存のデータモデルのコピーに対して、ステップ2で抽出した部分的な更新データをマージ（上書き）します。

    updated_item = stored_item_model.model_copy(update=update_data)
    # jsonable_encoder()はPydanticモデルをJSON互換のPythonデータ構造に変換する
    items[item_id] = jsonable_encoder(updated_item)
    return updated_item
    """
    
