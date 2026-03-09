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