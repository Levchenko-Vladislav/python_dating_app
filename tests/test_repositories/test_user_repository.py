import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.dating_bot.database.repositories.user_repository import UserRepository


class TestUserRepository:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        return UserRepository(mock_session)

    @pytest.mark.asyncio
    async def test_get_all_active_users(self, repository, mock_session):
        mock_user1 = MagicMock()
        mock_user1.id = 1001
        mock_user2 = MagicMock()
        mock_user2.id = 1002

        mock_scalars_result = MagicMock()
        mock_scalars_result.all.return_value = [mock_user1, mock_user2]

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars_result

        mock_session.execute.return_value = mock_result

        result = await repository.get_all_active_users()

        assert len(result) == 2
        user_ids = {user.id for user in result}
        assert 1001 in user_ids
        assert 1002 in user_ids



    @pytest.mark.asyncio
    async def test_create_user_duplicate(self, user_repository):
        user1 = await user_repository.create_user(
            telegram_id=111222333,
            name="Первый",
            age=25
        )

        user2 = await user_repository.create_user(
            telegram_id=111222333,
            name="Другое Имя",
            age=40
        )

        assert user2 is not None
        assert user2.id == user1.id
        assert user2.name == user1.name
        assert user2.age == user1.age

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id_not_found(self, user_repository):
        user = await user_repository.get_user_by_telegram_id(999999999)

        assert user is None

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_repository):
        created_user = await user_repository.create_user(
            telegram_id=111222333,
            name="Исходный",
            age=25,
            city="Москва",
            sex="male",
            photo_id="old_photo"
        )

        updated = await user_repository.update_user(
            telegram_id=111222333,
            age=26,
            city="Новосибирск",
            photo_id="new_photo_123"
        )

        assert updated is not None
        assert updated.age == 26
        assert updated.city == "Новосибирск"
        assert updated.photo_id == "new_photo_123"
        assert updated.name == "Исходный"
        assert updated.sex == "male"

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_repository):
        updated = await user_repository.update_user(
            telegram_id=999999999,
            age=30
        )

        assert updated is None

    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_repository):
        created_user = await user_repository.create_user(
            telegram_id=111222333,
            name="Тестовый",
            age=25
        )

        result = await user_repository.delete_user(111222333)

        assert result is True

        user = await user_repository.get_user_by_telegram_id(111222333)
        assert user is not None
        assert user.is_active is False

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, user_repository):
        result = await user_repository.delete_user(999999999)

        assert result is False

    @pytest.mark.asyncio
    async def test_user_exists_true(self, user_repository):
        await user_repository.create_user(
            telegram_id=111222333,
            name="Тестовый",
            age=25
        )

        exists = await user_repository.user_exists(111222333)

        assert exists is True

    @pytest.mark.asyncio
    async def test_user_exists_false(self, user_repository):
        exists = await user_repository.user_exists(999999999)

        assert exists is False

    @pytest.mark.asyncio
    async def test_count_users(self, user_repository):
        await user_repository.create_user(telegram_id=1001, name="Первый")
        await user_repository.create_user(telegram_id=1002, name="Второй")
        await user_repository.create_user(telegram_id=1003, name="Третий")

        count = await user_repository.count_users()

        assert count == 3

    @pytest.mark.asyncio
    async def test_count_users_empty(self, user_repository):
        count = await user_repository.count_users()

        assert count == 0