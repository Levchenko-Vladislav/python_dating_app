from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

DATABASE_URL = "sqlite+aiosqlite:///./dating_app.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db_session():
    """
       Получить сессию для работы с БД
       Использовать в async функциях:
       async with get_db_session() as session:
           # работа с БД
       """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
