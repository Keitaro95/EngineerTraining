from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, StrictInt

class Event(BaseModel):
    id: UUID
    dt: datetime

class StrictEvent(BaseModel):
    # 型変換を厳格にしたい時strict modeにする
    model_config = ConfigDict(strict=True)

    id: UUID
    dt: datetime

# 型変換を厳格にしたい時
class User(BaseModel):
    name: str = Field(..., strict=True)
    age: StrictInt


if __name__ == "__main__":
    # pythonは暗黙的に型変換を行う
    # try:
    #     event = Event(
    #         id="19a63218-cca8-489e-89c6-b283a9ac4118",  # UUID形式の文字列
    #         dt="2021-08-01T00:00:00+09:00",  # datetime形式の文字列
    #     )
    #     print(event)
    # except ValueError as e:
    #     print(e)


    try:
        strictEvent = StrictEvent(
            id="19a63218-cca8-489e-89c6-b283a9ac4118",  # UUID形式の文字列
            dt="2021-08-01T00:00:00+09:00",  # datetime形式の文字列
        )
    except ValueError as e:
        print(e)  