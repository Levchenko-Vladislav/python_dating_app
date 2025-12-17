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
    print("🔧 Инициализация базы данных...")

    from .models import User

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Таблицы созданы успешно!")

    # Проверяем что все работает
    async with AsyncSessionLocal() as session:
        from sqlalchemy import text
        result = await session.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'"))
        table_count = result.scalar()
        print(f"📊 Таблиц в БД: {table_count}")

        # Проверяем таблицу users
        result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'"))
        if result.fetchone():
            print("✅ Таблица 'users' существует")
        else:
            print("❌ Таблица 'users' не найдена")