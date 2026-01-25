from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

DATABASE_URL = "sqlite+aiosqlite:///./dating_app.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    connect_args={"check_same_thread": False}
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


async def init_database():
    """
    Инициализация базы данных - создание таблиц
    """
    print("Инициализация базы данных...")

    from .models import User, UserTestResult, Like, Match, SpeedDatingSession

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Таблицы созданы успешно!")

    async with AsyncSessionLocal() as session:
        from sqlalchemy import text
        result = await session.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'"))
        table_count = result.scalar()
        print(f"Таблиц в БД: {table_count}")

        tables = ['users', 'user_test_results', 'likes', 'matches', 'speed_dating_sessions']
        for table in tables:
            result = await session.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
            if result.fetchone():
                print(f"Таблица '{table}' существует")
            else:
                print(f"Таблица '{table}' не найдена")