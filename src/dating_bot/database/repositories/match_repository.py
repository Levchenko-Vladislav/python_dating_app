from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import logging

from src.dating_bot.database.models import Match

logger = logging.getLogger(__name__)


class MatchRepository:
    """Репозиторий для работы с мэтчами (взаимными лайками)"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_match(self, user1_id: int, user2_id: int) -> Optional[Match]:
        """Создать новый мэтч"""
        try:
            # Упорядочиваем ID для избежания дубликатов (меньший ID всегда user1)
            if user1_id > user2_id:
                user1_id, user2_id = user2_id, user1_id

            # Проверяем, существует ли уже мэтч
            existing = await self.get_match(user1_id, user2_id)
            if existing:
                return existing

            # Создаем новый мэтч
            new_match = Match(
                user1_id=user1_id,
                user2_id=user2_id,
                matched_at=datetime.now(timezone.utc),
                status="active"
            )
            self.session.add(new_match)
            await self.session.commit()
            await self.session.refresh(new_match)

            logger.info(f"Создан новый мэтч: {user1_id} ↔ {user2_id}")
            return new_match

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Ошибка создания мэтча: {e}")
            return None
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Неизвестная ошибка: {e}")
            return None

    async def get_match(self, user1_id: int, user2_id: int) -> Optional[Match]:
        """Получить мэтч между двумя пользователями"""
        try:
            # Упорядочиваем ID
            if user1_id > user2_id:
                user1_id, user2_id = user2_id, user1_id

            result = await self.session.execute(
                select(Match).where(
                    and_(
                        Match.user1_id == user1_id,
                        Match.user2_id == user2_id,
                        Match.status == "active"
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Ошибка получения мэтча: {e}")
            return None

    async def get_user_matches(self, user_id: int) -> List[Match]:
        """Получить все активные мэтчи пользователя"""
        try:
            result = await self.session.execute(
                select(Match).where(
                    and_(
                        or_(
                            Match.user1_id == user_id,
                            Match.user2_id == user_id
                        ),
                        Match.status == "active"
                    )
                )
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Ошибка получения мэтчей пользователя: {e}")
            return []

    async def archive_match(self, user1_id: int, user2_id: int) -> bool:
        """Архивировать мэтч"""
        try:
            match = await self.get_match(user1_id, user2_id)
            if not match:
                return False

            match.status = "archived"
            await self.session.commit()
            logger.info(f"Мэтч архивирован: {user1_id} ↔ {user2_id}")
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка архивации мэтча: {e}")
            return False

    async def get_match_by_id(self, match_id: int) -> Optional[Match]:
        """Получить мэтч по ID"""
        try:
            result = await self.session.execute(
                select(Match).where(Match.id == match_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Ошибка получения мэтча по ID: {e}")
            return None

    async def delete_match(self, match_id: int) -> bool:
        match = await self.session.get(Match, match_id)
        if not match:
            return False

        await self.session.delete(match)
        await self.session.commit()
        return True