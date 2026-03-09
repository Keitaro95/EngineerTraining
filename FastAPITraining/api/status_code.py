"""
公式ドキュメント（https://fastapi.tiangolo.com/reference/status/ ）
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from starlette import status
from starlette.status import HTTP_200_OK

app = FastAPI()

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    return item

@app.delete("/items/{item_id}", status_code=status.HTTP_204_CONTENT)
async def delete_item(item_id: int):
    return None

# Exception 
@app.get("/items/{item/_id}")
async def get_item(item_id: int):
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
        )
    return item

@app.put("items/{item_id}")
async def upsert_item(item_id: str, name: str):
    if item_id in items:
        return items[item_id]
    else:
        items[item_id] = {"name": name}
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=items[item_id],
        )



"""
HTTP_422_UNPROCESSABLE_ENTITY を手動で使うのは、スキーマは通るけどビジネスロジックで弾きたいときです。
"""
class Item(BaseModel):
    name: str
    price: float
    quantity: int

@app.post("/items/")
async def create_item(item: Item):
    # 例1: 値の組み合わせチェック
    if item.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="price must be greater than 0"
        )

    # 例2: 文字列の内容チェック
    if len(item.name.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="name cannot be empty or whitespace only"
        )

    # 例3: 複数フィールドの相関チェック
    if item.quantity > 0 and item.price == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="free items cannot have quantity"
        )

    return item

