from datetime import date
from typing import Any
from pydantic import BaseModel, field_serializer, model_serializer

class Task(BaseModel):
    name: str
    dueDate: date

    # 特定のフィールドだけに対して適用
    @field_serializer("dueDate")
    def serializeDate(self, d: date) -> str:
        return d.strftime("%Y %m %d")
    """
    strftimeは日付や時刻のオブジェクトを文字列に変換する関数で、引数にフォーマット文字列を指定します
    %Y: 西暦（例: 2025）
    %m: 月（01～12）
    %d: 日（01～31）
    %B: 月名（例: December）
    %H: 時（00～23）
    %M: 分（00～59）
    %S: 秒（00～59）
    """

    """
    from typing：型ヒントで使うライブラリー
    Pythonで型ヒントを書くときに使う。
    Any：どんな型でもOK
    List[int]：int型のリスト
    Dict[str, int]：キーがstr、値がintの辞書
    Optional[str]：strまたはNone
    Union[int, str]：intまたはstr
    """
    @model_serializer
    def seriarizeDateToJson(self) -> dict[str, Any]:
        return {
            "name": self.name, # クラス名自身
            "year": self.dueDate.year,
            "month": self.dueDate.month,
            "day": self.dueDate.day,
        }

class User(BaseModel):
    name: str
    tasks: list[Task]

if __name__ == "__main__":
    # try:
    #     user = User(
    #         name="John",
    #         tasks=[
    #             Task(name="task1", dueDate=date(2025, 12, 25)),
    #             Task(name="task2", dueDate=date(2025, 12, 31)),
    #         ],
    #     )
    #     # json文字列に変換
    #     print(user.model_dump_json(indent=2))
    # except ValueError as e:
    #     print(e)

    try:
        task = Task(
            name="task1",
            dueDate=date(2025, 12, 25)
        )
        print(task.model_dump_json(indent=2))
    except ValueError as e:
        print(e)
        