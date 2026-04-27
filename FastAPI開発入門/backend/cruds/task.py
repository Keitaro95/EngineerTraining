from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

import backend.models.task as task_model #dbのmodel
import backend.schemas.task as task_schema #dbのschema

## create動作をする関数を定義しています
## 引数として　schema を受け取る。これをDBモデルに変換する
async def create_task(
        db: AsyncSession, 
        task_create: task_schema.TaskCreate
        ) -> task_model.Task:
    task = task_model.Task(**task_create.dict())
    db.add(task)
    # 待ち時間が発生するような処理ですよ、と伝えている
    # 
    await db.commit()
    await db.refresh(task) # taskインスタンスを更新する処理
    return task

# Read
# Task テーブルと Doneテーブルをjoinして結果を返す
async def get_tasks_with_done(db: AsyncSession) -> list[tuple[int, str, bool]]:
    result: Result = await db.execute(
        select(
            task_model.Task.id,
            task_model.Task.title,
            task_model.Done.id.isnot(None).label("done"),
        ).outerjoin(task_model.Done)
    )
    return result.all()

# Update
async def get_task(db: AsyncSession, task_id: int) -> task_model.Task | None:
    result: Result = await db.execute(
        select(task_model.Task).filter(task_model.Task.id == task_id)
    )
    # tupleで返されるResultを、値に変換
    return result.scalars().first()

async def update_task(
        db: AsyncSession,
        task_create: task_schema.TaskCreate,
        original: task_model.Task
    ) -> task_model.Task:
    original.title = task_create.title
    db.add(original)
    await db.commit()
    await db.refresh(original)
    return original


## delete
async def delete_task(db: AsyncSession, original: task_model.Task) -> None:
    await db.delete(original)
    await db.commit()