from typing import Any
import numpy as np
from typing_extensions import Annotated
from pydantic import BaseModel, PlainSerializer, PlainValidator


def validateNdarray(x: np.ndarray) -> np.ndarray:
    """numpy.ndarray型かチェックする"""
    if not isinstance(x, np.ndarray):
        raise TypeError("Type numpy.ndarray is required")
    return x

def serializeNdarray(x: np.ndarray) -> list[Any]:
    """np.ndarrayをlistに変換"""
    return x.tolist()

# non-primitveな値を扱うためにAnnotatedでカスタム型を定義
# なお、PlainValidatorを使用するとPydanticデフォルトのvalidationは実行されなくなる
"""Annotated：型ヒントに対して、追加の情報（メタデータ）を付与するための仕組み
『検証時はこれを使って』『出力時はこれを使って』という付箋（メタデータ）を付与
"""
NdArray = Annotated[
    np.ndarray,                       # 1. ベースとなる型
    PlainValidator(validateNdarray),  # 2. 検証ルール（入力時）
    PlainSerializer(serializeNdarray),# 3. 変換ルール（出力時）
]

class Image(BaseModel):
    x: NdArray # こうしてカスタム型が定義できた

if __name__ == "__main__":
    image = Image(x=np.arange(4))
    print(image.model_dump_json(indent=2))
    