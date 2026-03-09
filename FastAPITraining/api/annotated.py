"""
https://fastapi.tiangolo.com/tutorial/query-param-models/

Annotated[型, メタデータ] は「この型に追加情報を付与する」

という Python 標準の仕組み。

FastAPI はこのメタデータを見てFilterParamsが Query()型だと判断する。

"""


from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import FastAPI, Query

app = FastAPI()

class FilterParams(BaseModel):
    """
    gt（より大きい）
    ge（以上）
    lt（より小さい）
    le（以下）
    multiple_of（倍数）
    allow_inf_nan（inf/NaN許可）
    max_digits/decimal_places（Decimal用）
    """
    limit: int = Field(100, gt=0, le=100)# デフォルト100、(0,100]の範囲
    offset: int = Field(0, ge=0)
    order_by: str = "created_at"

    # GET /items/?limit=20&unknown=foo → 422 Validation Error になる。
    model_config = ConfigDict(extra="forbid")

@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, QUery()]):
    """
    GET 
    /items/?limit=20&offset=5&order_by=name 
    """
    return filter_query


"""
FastAPI内部の処理フロー
1. リクエスト GET /items/?limit=20&offset=5 受け取る
2. FastAPIが Annotated  Query() を発見し「クエリ文字列」と決定する
3. FilterParams のフィールド定義（limit, offset, order_by）を走査し、それぞれに対応するクエリパラメータを抽出する
4. 抽出した値を FilterParams(limit=20, offset=5, order_by="created_at") のようにPydanticに渡してバリデーションを実行する
バリデーション通過後、 filter_query に注入される

⚠️Query()なしでPydanticモデルを型ヒントすると、FastAPIはJSONリクエストボディとして解釈する。
"""