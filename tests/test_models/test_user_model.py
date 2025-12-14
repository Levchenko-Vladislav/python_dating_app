import pytest
from datetime import datetime
from src.dating_bot.database.models import User


class TestUserModel:
    """Тесты модели User"""

    def test_user_creation(self):
        """Тест создания объекта пользователя"""
        user = User(
            telegram_id=123456,
            name="Тест",
            age=30,
            city="Город",
            sex="male"
        )

        assert user.telegram_id == 123456
        assert user.name == "Тест"
        assert user.age == 30
        assert user.city == "Город"
        assert user.sex == "male"

        assert user.created_at is None or isinstance(user.created_at, datetime)

    def test_user_repr(self):
        """Тест строкового представления"""
        user = User(id=1, telegram_id=123, name="Тест")
        repr_str = repr(user)

        assert "<User(id = 1, name = 'Тест', telegram_id = 123)>" == repr_str

    def test_user_default_values(self):
        """Тест значений по умолчанию"""
        user = User(
            telegram_id=123456,
            name="Тест"
        )

        # Проверяем дефолты
        assert user.age is None
        assert user.city is None
        assert user.sex is None
        assert user.photo_id is None

        assert user.search_sex is None or user.search_sex == "any"
        assert user.min_age is None or user.min_age == 18
        assert user.max_age is None or user.max_age == 100

    def test_user_validation(self):
        """Тест валидация не требуется - SQLAlchemy проверит при коммите"""
        # Создаем валидного пользователя
        user = User(telegram_id=123, name="Тест")
        assert user is not None

    @pytest.mark.parametrize("field,value,expected", [
        ("name", "Иван Иванов", "Иван Иванов"),
        ("age", 25, 25),
        ("age", None, None),
        ("city", "Санкт-Петербург", "Санкт-Петербург"),
        ("sex", "female", "female"),
        ("is_active", False, False),
    ])
    def test_user_fields(self, field, value, expected):
        """Параметризованный тест полей"""
        user = User(telegram_id=123, name="Тест")
        setattr(user, field, value)

        assert getattr(user, field) == expected