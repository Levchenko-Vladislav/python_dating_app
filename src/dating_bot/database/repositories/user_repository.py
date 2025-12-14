from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from typing import Optional, List
import logging

from src.dating_bot.database.models import User

# Настройка логгера
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
            telegram_id: int,
            name: str,
            age: Optional[int] = None,
            city: Optional[str] = None,
            sex: Optional[str] = None,
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
                name=name,
                age=age,
                city=city,
                sex=sex,
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

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
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
            telegram_id: int,
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
                              'is_active', 'search_sex', 'min_age', 'max_age',
                              'only_same_city'}

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

    async def delete_user(self, telegram_id: int) -> bool:
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

    async def user_exists(self, telegram_id: int) -> bool:
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