from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import logging

from src.dating_bot.database.models import User, UserTestResult

logger = logging.getLogger(__name__)


class UserRepository:
    """Репозиторий для работы с пользователями"""

    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория

        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        self.session = session

    async def create_user(
            self,
            name: str,
            telegram_id: str,
            username: Optional[str] = None,
            age: Optional[int] = None,
            city: Optional[str] = None,
            sex: Optional[str] = None,
            goal: Optional[str] = None,
            photo_id: Optional[str] = None
    ) -> Optional[User]:
        try:
            # Проверяем, существует ли уже пользователь
            existing_user = await self.get_user_by_telegram_id(telegram_id)
            if existing_user:
                logger.info(f"Пользователь с telegram_id={telegram_id} уже существует")
                return existing_user

            new_user = User(
                telegram_id=telegram_id,
                username=username,
                name=name,
                age=age,
                city=city,
                sex=sex,
                goal=goal,
                photo_id=photo_id,
                created_at=datetime.now(timezone.utc),
                is_active=True
            )

            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)

            logger.info(f"Создан пользователь: {new_user}")
            return new_user

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Ошибка создания пользователя: {e}")
            return None
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Неизвестная ошибка: {e}")
            return None

    async def get_user_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """
        Найти пользователя по Telegram ID
        """
        try:
            result = await self.session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if user:
                logger.debug(f"Найден пользователь: telegram_id={telegram_id}")
            else:
                logger.debug(f"Пользователь не найден: telegram_id={telegram_id}")

            return user

        except Exception as e:
            logger.error(f"Ошибка поиска пользователя: {e}")
            return None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Найти пользователя по username (с @)
        """
        try:
            result = await self.session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()

            if user:
                logger.debug(f"Найден пользователь: username={username}")
            else:
                logger.debug(f"Пользователь не найден: username={username}")

            return user

        except Exception as e:
            logger.error(f"Ошибка поиска пользователя по username: {e}")
            return None

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Найти пользователя по ID в БД
        """
        try:
            result = await self.session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Ошибка поиска пользователя по ID: {e}")
            return None

    async def update_user(
            self,
            telegram_id: str,
            **kwargs
    ) -> Optional[User]:
        """
        Обновить данные пользователя
        """
        try:
            # Проверяем, существует ли пользователь
            user = await self.get_user_by_telegram_id(telegram_id)
            if not user:
                logger.warning(f"Пользователь не найден для обновления: {telegram_id}")
                return None

            allowed_fields = {'name', 'age', 'city', 'sex', 'photo_id',
                              'is_active', 'search_sex', 'min_age', 'max_age','goal',
                              'only_same_city', 'username', 'telegram_id'}

            update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}

            if not update_data:
                logger.warning("Нет полей для обновления")
                return user

            # Выполняем обновление
            await self.session.execute(
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(**update_data)
            )
            await self.session.commit()

            await self.session.refresh(user)

            logger.info(f"Обновлен пользователь {telegram_id}: {update_data}")
            return user

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка обновления пользователя: {e}")
            return None

    async def delete_user(self, telegram_id: str) -> bool:
        """
        Удалить пользователя (мягкое удаление - деактивация)
        """
        try:
            user = await self.get_user_by_telegram_id(telegram_id)
            if not user:
                return False

            # Мягкое удаление - просто деактивируем
            user.is_active = False
            await self.session.commit()

            logger.info(f"Пользователь деактивирован: {telegram_id}")
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка удаления пользователя: {e}")
            return False

    async def get_all_active_users(self) -> List[User]:
        """
        Получить всех активных пользователей
        """
        try:
            result = await self.session.execute(
                select(User).where(User.is_active == True)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Ошибка получения активных пользователей: {e}")
            return []

    async def user_exists(self, telegram_id: str) -> bool:
        """
        Проверить, существует ли пользователь
        """
        user = await self.get_user_by_telegram_id(telegram_id)
        return user is not None

    async def count_users(self) -> int:
        """
        Получить общее количество пользователей
        """
        try:
            from sqlalchemy import func
            result = await self.session.execute(
                select(func.count(User.id))
            )
            return result.scalar()
        except Exception as e:
            logger.error(f"Ошибка подсчета пользователей: {e}")
            return 0

    async def get_user_with_test_results(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить пользователя вместе с результатами теста
        """
        try:
            user = await self.get_user_by_telegram_id(telegram_id)
            if not user:
                return None

            result = await self.session.execute(
                select(UserTestResult).where(UserTestResult.user_id == user.id)
            )
            test_result = result.scalar_one_or_none()

            return {
                "user": user,
                "test_result": test_result,
                "has_test": test_result is not None and test_result.is_completed
            }

        except Exception as e:
            logger.error(f"Ошибка получения пользователя с тестом: {e}")
            return None