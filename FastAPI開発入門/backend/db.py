from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


ASYNC_DB_URL = "mysql+pymysql://root@db:3306/demo?charset=utf8"

async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
async_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    class_=async_engine,
    )


Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session