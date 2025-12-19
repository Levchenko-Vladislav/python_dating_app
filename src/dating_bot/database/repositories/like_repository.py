from sqlalchemy import select, and_, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Any
import logging

from src.dating_bot.database.models import Like, Match

logger = logging.getLogger(__name__)


class LikeRepository:
    """Репозиторий для работы с лайками и дизлайками"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_like(self, user_from_id: int, user_to_id: int, is_like: bool = True) -> Optional[Like]:
        """Создать или обновить лайк/дизлайк"""
        try:
            print(f"DEBUG: create_like: {user_from_id} → {user_to_id}, is_like={is_like}")

            existing = await self.get_like(user_from_id, user_to_id)

            if existing:
                print(f"DEBUG: Обновляем существующую реакцию: was_like={existing.is_like}, new_like={is_like}")
                existing.is_like = is_like
                existing.created_at = datetime.now(timezone.utc)
            else:
                print(f"DEBUG: Создаем новую реакцию")
                new_like = Like(
                    user_from_id=user_from_id,
                    user_to_id=user_to_id,
                    is_like=is_like
                )
                self.session.add(new_like)
                existing = new_like

            await self.session.commit()
            await self.session.refresh(existing)

            action = "лайк" if is_like else "дизлайк"
            print(f"DEBUG: Создан {action}: {user_from_id} → {user_to_id}")
            return existing

        except IntegrityError as e:
            await self.session.rollback()
            print(f"ERROR: Ошибка создания лайка: {e}")
            return None
        except Exception as e:
            await self.session.rollback()
            print(f"ERROR: Неизвестная ошибка: {e}")
            return None

    async def get_like(self, user_from_id: int, user_to_id: int) -> Optional[Like]:
        """Получить реакцию одного пользователя на другого"""
        try:
            result = await self.session.execute(
                select(Like).where(
                    and_(
                        Like.user_from_id == user_from_id,
                        Like.user_to_id == user_to_id
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Ошибка получения лайка: {e}")
            return None

    async def check_mutual_like(self, user1_id: int, user2_id: int) -> bool:
        """Проверить наличие взаимного лайка"""
        try:
            like1 = await self.get_like(user1_id, user2_id)
            like2 = await self.get_like(user2_id, user1_id)

            return (
                    like1 is not None and like1.is_like and
                    like2 is not None and like2.is_like
            )
        except Exception as e:
            logger.error(f"Ошибка проверки взаимного лайка: {e}")
            return False

    async def get_likes_received(self, user_id: int, only_likes: bool = True) -> List[Like]:
        """Получить все лайки, полученные пользователем"""
        try:
            query = select(Like).where(Like.user_to_id == user_id)
            if only_likes:
                query = query.where(Like.is_like == True)

            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Ошибка получения полученных лайков: {e}")
            return []

    async def get_likes_given(self, user_id: int, only_likes: bool = True) -> List[Like]:
        """Получить все лайки, поставленные пользователем"""
        try:
            query = select(Like).where(Like.user_from_id == user_id)
            if only_likes:
                query = query.where(Like.is_like == True)

            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Ошибка получения поставленных лайков: {e}")
            return []

    async def delete_like(self, user_from_id: int, user_to_id: int) -> bool:
        """Удалить реакцию"""
        try:
            like = await self.get_like(user_from_id, user_to_id)
            if not like:
                return False

            await self.session.delete(like)
            await self.session.commit()
            logger.info(f"Удален лайк: {user_from_id} → {user_to_id}")
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка удаления лайка: {e}")
            return False

    async def get_mutual_likes_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить список взаимных лайков для пользователя"""
        try:
            likes_given = await self.get_likes_given(user_id, only_likes=True)

            mutual_likes = []
            for like in likes_given:
                reverse_like = await self.get_like(like.user_to_id, user_id)
                if reverse_like and reverse_like.is_like:
                    mutual_likes.append({
                        'user_id': like.user_to_id,
                        'liked_at': like.created_at,
                        'mutual_at': reverse_like.created_at
                    })

            return mutual_likes

        except Exception as e:
            logger.error(f"Ошибка получения взаимных лайков: {e}")
            return []