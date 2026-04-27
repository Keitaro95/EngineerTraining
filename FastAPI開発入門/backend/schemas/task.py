# routerのレスポンス型を定義する
import datetime
from pydantic import BaseModel, Field

class TaskBase(BaseModel):
    title: str | None = Field(None, example="クリーニングを取りにいく")
    due_date: datetime.date | None = Field(None, example="2024-12-01")

class TaskCreate(TaskBase):
    pass

class TaskCreateResponse(TaskCreate):
    id: int

    class Config:
        orm_mode = True

class Task(TaskBase):
    id: int
    done: bool = Field(None, description="完了フラグ")

    class Config:
        # ormからdbオブジェクトを受け取り、responseスキーマに変換する
        orm_mode = True


