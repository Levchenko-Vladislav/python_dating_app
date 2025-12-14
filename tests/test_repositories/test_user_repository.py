import pytest


class TestUserRepository:
    """Тесты UserRepository"""

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_repository):
        """Успешное создание пользователя"""
        user = await user_repository.create_user(
            telegram_id=999888777,
            name="Новый Пользователь",
            age=30,
            city="Казань",
            sex="male",
            photo_id="photo_999"
        )

        assert user is not None
        assert user.id is not None
        assert user.telegram_id == 999888777
        assert user.name == "Новый Пользователь"
        assert user.age == 30
        assert user.city == "Казань"
        assert user.sex == "male"
        assert user.photo_id == "photo_999"
        assert user.is_active is True
        assert user.created_at is not None

    @pytest.mark.asyncio
    async def test_create_user_duplicate(self, user_repository):
        """Создание дубликата пользователя"""
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
    async def test_get_user_by_telegram_id_found(self, user_repository):
        """Поиск существующего пользователя"""
        created_user = await user_repository.create_user(
            telegram_id=111222333,
            name="Тестовый",
            age=25
        )

        found_user = await user_repository.get_user_by_telegram_id(111222333)

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.telegram_id == 111222333
        assert found_user.name == "Тестовый"

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id_not_found(self, user_repository):
        """Поиск несуществующего пользователя"""
        user = await user_repository.get_user_by_telegram_id(999999999)

        assert user is None

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_repository):
        """Успешное обновление пользователя"""
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
        """Обновление несуществующего пользователя"""
        updated = await user_repository.update_user(
            telegram_id=999999999,
            age=30
        )

        assert updated is None

    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_repository):
        """Успешное удаление (деактивация)"""
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
        """Удаление несуществующего пользователя"""
        result = await user_repository.delete_user(999999999)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_all_active_users(self, user_repository):
        """Получение всех активных пользователей"""
        user1 = await user_repository.create_user(
            telegram_id=1001,
            name="Анна",
            age=25,
            city="Москва",
            sex="female"
        )

        user2 = await user_repository.create_user(
            telegram_id=1002,
            name="Иван",
            age=30,
            city="Москва",
            sex="male"
        )

        user3 = await user_repository.create_user(
            telegram_id=1003,
            name="Мария",
            age=28,
            city="СПб",
            sex="female"
        )
        await user_repository.update_user(
            telegram_id=1003,
            is_active=False
        )

        active_users = await user_repository.get_all_active_users()

        assert len(active_users) == 2

        for user in active_users:
            assert user.is_active is True

        telegram_ids = {u.telegram_id for u in active_users}
        assert 1001 in telegram_ids
        assert 1002 in telegram_ids
        assert 1003 not in telegram_ids

    @pytest.mark.asyncio
    async def test_user_exists_true(self, user_repository):
        """Проверка существования пользователя"""
        await user_repository.create_user(
            telegram_id=111222333,
            name="Тестовый",
            age=25
        )

        exists = await user_repository.user_exists(111222333)

        assert exists is True

    @pytest.mark.asyncio
    async def test_user_exists_false(self, user_repository):
        """Проверка несуществующего пользователя"""
        exists = await user_repository.user_exists(999999999)

        assert exists is False

    @pytest.mark.asyncio
    async def test_count_users(self, user_repository):
        """Подсчет пользователей"""
        # Создаем несколько пользователей
        await user_repository.create_user(telegram_id=1001, name="Первый")
        await user_repository.create_user(telegram_id=1002, name="Второй")
        await user_repository.create_user(telegram_id=1003, name="Третий")

        count = await user_repository.count_users()

        assert count == 3

    @pytest.mark.asyncio
    async def test_count_users_empty(self, user_repository):
        """Подсчет в пустой БД"""
        count = await user_repository.count_users()

        assert count == 0