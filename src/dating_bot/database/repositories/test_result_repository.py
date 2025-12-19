from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import logging

from src.dating_bot.database.models import UserTestResult

logger = logging.getLogger(__name__)


class TestResultRepository:
    """Репозиторий для работы с результатами тестов"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_test_result_by_user_id(self, user_id: int) -> Optional[UserTestResult]:
        """Получить результаты теста пользователя"""
        try:
            result = await self.session.execute(
                select(UserTestResult).where(UserTestResult.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Ошибка получения результатов теста: {e}")
            return None

    async def save_test_result(
            self,
            user_id: int,
            answers: Dict[int, int],
            category_scores: Dict[str, float],
            is_completed: bool = True
    ) -> Optional[UserTestResult]:
        """Сохранить или обновить результаты теста"""
        try:
            # Проверяем, существует ли уже запись
            existing = await self.get_test_result_by_user_id(user_id)

            if existing:
                # Обновляем существующую запись
                existing.answers = answers
                existing.category_scores = category_scores
                existing.answered_count = len(answers)
                existing.is_completed = is_completed
                existing.completed_at = datetime.now(timezone.utc) if is_completed else None
            else:
                # Создаем новую запись
                new_result = UserTestResult(
                    user_id=user_id,
                    answers=answers,
                    category_scores=category_scores,
                    answered_count=len(answers),
                    is_completed=is_completed,
                    completed_at=datetime.now(timezone.utc) if is_completed else None
                )
                self.session.add(new_result)
                existing = new_result

            await self.session.commit()
            await self.session.refresh(existing)

            logger.info(f"Сохранены результаты теста для user_id={user_id}, ответов: {len(answers)}")
            return existing

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Ошибка сохранения результатов теста: {e}")
            return None
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Неизвестная ошибка: {e}")
            return None

    async def delete_test_result(self, user_id: int) -> bool:
        """Удалить результаты теста пользователя"""
        try:
            result = await self.get_test_result_by_user_id(user_id)
            if not result:
                return False

            await self.session.delete(result)
            await self.session.commit()
            logger.info(f"Удалены результаты теста для user_id={user_id}")
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка удаления результатов теста: {e}")
            return False

    async def is_test_completed(self, user_id: int) -> bool:
        """Проверить, прошел ли пользователь тест"""
        result = await self.get_test_result_by_user_id(user_id)
        return result is not None and result.is_completed