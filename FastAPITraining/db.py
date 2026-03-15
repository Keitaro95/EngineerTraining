from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator, Annotated

DATABASE_URL = "mysql+asyncmy://user:password@localhost:3306/dbname"

engine = create_async_engine(
    DATABASE_URL,
    echo=True, # SQL出力（開発用）
    pool_size=5,
    max_overflow=10, # 接続上限
    pool_pre_ping=True, # ping確認
    poolrecycle=3600, # 接続リサイクル秒数
)
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False, # asyncでは必須
)
"""
非同期接続している
そのため
コミット後もexpireさせないためにfalseにします
https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
"""

# db セッション管理
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

"""
db接続に使うdepends注入を
他のrouterで使うとき
これ使えばいい

async def create_item(session: DBSessionDep):
"""
DBSessionDep = Annotated[AsyncSession, Depends(get_db)]



