import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.dating_bot.database.session import Base
from src.dating_bot.database.models import User


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine):
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        # Автоматический rollback в конце теста
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def user_repository(test_session):
    from src.dating_bot.database.repositories.user_repository import UserRepository
    return UserRepository(test_session)


@pytest_asyncio.fixture(scope="function")
async def sample_user(test_session):
    user = User(
        telegram_id=1001,
        name="Тестовый Пользователь",
        age=25,
        city="Тестовоград",
        sex="male",  # или sex= если у тебя так
        photo_id="test_photo_001",
        created_at=datetime.utcnow(),
        is_active=True
    )

    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    return user


@pytest_asyncio.fixture(scope="function")
async def sample_users(test_session):
    users = [
        User(
            telegram_id=1001,
            name="Анна",
            age=25,
            city="Москва",
            sex="female",
            is_active=True
        ),
        User(
            telegram_id=1002,
            name="Иван",
            age=30,
            city="Москва",
            sex="male",
            is_active=True
        ),
        User(
            telegram_id=1003,
            name="Мария",
            age=28,
            city="Санкт-Петербург",
            sex="female",
            is_active=False  # Неактивный
        )
    ]

    test_session.add_all(users)
    await test_session.commit()

    for user in users:
        await test_session.refresh(user)

    return users