import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


class TestUserService:
    @pytest.mark.asyncio
    async def test_register_user_new(self):
        from src.dating_bot.services import UserService

        with patch('src.dating_bot.services.user_service.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            mock_repo = AsyncMock()
            mock_repo.get_user_by_telegram_id.return_value = None  # Пользователь не существует

            # Создаем реальный mock пользователя
            mock_user = MagicMock()
            mock_user.telegram_id = 111222333
            mock_user.name = "Новый Тестовый"
            mock_user.age = 28
            mock_user.city = "Екатеринбург"
            mock_user.sex = "female"
            mock_repo.create_user.return_value = mock_user

            with patch('src.dating_bot.services.user_service.UserRepository', return_value=mock_repo):
                result = await UserService.register_user(
                    telegram_id=111222333,
                    name="Новый Тестовый",
                    age=28,
                    city="Екатеринбург",
                    sex="female"
                )

        assert result["success"] is True
        assert "Регистрация успешна" in result["message"]
        assert result["is_new"] is True
        assert result["user"] is not None
        assert result["user"].telegram_id == 111222333

    @pytest.mark.asyncio
    async def test_register_user_existing(self):
        from src.dating_bot.services import UserService

        with patch('src.dating_bot.services.user_service.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            mock_repo = AsyncMock()
            # Возвращаем существующего пользователя
            mock_existing_user = MagicMock()
            mock_existing_user.id = 1
            mock_existing_user.telegram_id = 123456
            mock_existing_user.name = "Существующий Пользователь"
            mock_existing_user.age = 25
            mock_repo.get_user_by_telegram_id.return_value = mock_existing_user

            with patch('src.dating_bot.services.user_service.UserRepository', return_value=mock_repo):
                result = await UserService.register_user(
                    telegram_id=123456,
                    name="Новое Имя",
                    age=99
                )

        assert result["success"] is True
        assert "Вы уже зарегистрированы" in result["message"]
        assert result["is_new"] is False
        assert result["user"] is not None
        assert result["user"].id == 1
        assert result["user"].name == "Существующий Пользователь"

    @pytest.mark.asyncio
    async def test_get_user_profile_success(self):
        from src.dating_bot.services import UserService

        with patch('src.dating_bot.services.user_service.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            mock_repo = AsyncMock()
            mock_user = MagicMock()
            mock_user.id = 1
            mock_user.telegram_id = 123456
            mock_user.name = "Тестовый Пользователь"
            mock_user.age = 25
            mock_user.city = "Тестовоград"
            mock_user.sex = "male"
            mock_user.photo_id = "test_photo_001"
            mock_user.is_active = True
            mock_user.created_at = datetime(2023, 1, 1)

            mock_repo.get_user_by_telegram_id.return_value = mock_user

            with patch('src.dating_bot.services.user_service.UserRepository', return_value=mock_repo):
                profile = await UserService.get_user_profile(123456)

        assert profile is not None
        assert profile["user"].id == 1
        assert "Имя: Тестовый Пользователь" in profile["text"]
        assert "Возраст: 25" in profile["text"]
        assert "Город: Тестовоград" in profile["text"]
        assert "Пол: male" in profile["text"]
        assert profile["has_photo"] is True
        assert profile["photo_id"] == "test_photo_001"
        assert profile["is_active"] is True

    @pytest.mark.asyncio
    async def test_update_user_profile_success(self):
        from src.dating_bot.services import UserService

        with patch('src.dating_bot.services.user_service.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            mock_repo = AsyncMock()
            mock_repo.get_user_by_telegram_id.return_value = MagicMock()  # Пользователь существует

            mock_updated_user = MagicMock()
            mock_updated_user.name = "Обновленное Имя"
            mock_updated_user.age = 26
            mock_updated_user.city = "Обновленный Город"
            mock_updated_user.photo_id = "new_photo_456"
            mock_repo.update_user.return_value = mock_updated_user

            with patch('src.dating_bot.services.user_service.UserRepository', return_value=mock_repo):
                result = await UserService.update_user_profile(
                    telegram_id=123456,
                    name="Обновленное Имя",
                    age=26,
                    city="Обновленный Город",
                    photo_id="new_photo_456"
                )

        assert result["success"] is True
        assert "Профиль обновлен" in result["message"]
        assert result["user"] is not None
        assert result["user"] is mock_updated_user
        assert result["user"].name == "Обновленное Имя"


    @pytest.mark.asyncio
    async def test_delete_user_profile_not_found(self):
        from src.dating_bot.services.user_service import delete_user_completely 

        with patch('src.dating_bot.services.user_service.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            mock_repo = AsyncMock()
            mock_repo.delete_user_completely.return_value = False  

            with patch('src.dating_bot.services.user_service.UserRepository', return_value=mock_repo):
                result = await delete_user_completely("999999999")  

        assert result is False

    @pytest.mark.asyncio
    async def test_check_user_exists_true(self):
        from src.dating_bot.services import UserService

        with patch('src.dating_bot.services.user_service.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            mock_repo = AsyncMock()
            mock_repo.user_exists.return_value = True

            with patch('src.dating_bot.services.user_service.UserRepository', return_value=mock_repo):
                exists = await UserService.check_user_exists(123456)

        assert exists is True

    @pytest.mark.asyncio
    async def test_check_user_exists_false(self):
        from src.dating_bot.services import UserService

        with patch('src.dating_bot.services.user_service.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            mock_repo = AsyncMock()
            mock_repo.user_exists.return_value = False

            with patch('src.dating_bot.services.user_service.UserRepository', return_value=mock_repo):
                exists = await UserService.check_user_exists(999999999)

        assert exists is False

    @pytest.mark.asyncio
    async def test_get_user_stats(self):
        from src.dating_bot.services import UserService
        from unittest.mock import AsyncMock, patch

        with patch('src.dating_bot.services.user_service.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            mock_repo = AsyncMock()
            mock_repo.count_users.return_value = 10
            mock_repo.get_all_active_users.return_value = [
                MagicMock(age=25, city="Москва"),
                MagicMock(age=30, city="Москва"),
                MagicMock(age=35, city="СПб"),
                MagicMock(age=None, city=None),
            ]

            with patch('src.dating_bot.services.user_service.UserRepository', return_value=mock_repo):
                stats = await UserService.get_user_stats()

        assert stats["total_users"] == 10
        assert stats["active_users"] == 4
        assert stats["inactive_users"] == 6
        assert isinstance(stats["average_age"], float)
        assert isinstance(stats["top_cities"], list)

    @pytest.mark.asyncio
    async def test_get_user_stats_empty(self):
        from src.dating_bot.services import UserService

        with patch('src.dating_bot.services.user_service.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            mock_repo = AsyncMock()
            mock_repo.count_users.return_value = 0
            mock_repo.get_all_active_users.return_value = []

            with patch('src.dating_bot.services.user_service.UserRepository', return_value=mock_repo):
                stats = await UserService.get_user_stats()

        assert stats["total_users"] == 0
        assert stats["active_users"] == 0
        assert stats["inactive_users"] == 0
        assert stats["average_age"] == 0
        assert stats["top_cities"] == []