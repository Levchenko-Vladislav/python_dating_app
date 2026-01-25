from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import logging
from sqlalchemy.orm.attributes import flag_modified
from src.dating_bot.database.models import SpeedDatingSession, Match
from src.dating_bot.database.repositories.match_repository import MatchRepository


logger = logging.getLogger(__name__)


class SpeedDatingRepository:

    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_session(self, user1_id: int, user2_id: int, match_id: int, questions: List[str], current_responder_id: int = None) -> Optional[SpeedDatingSession]:
        """Создать новую сессию спиддейтинга"""
        try:
            if current_responder_id is None:
                current_responder_id = user1_id

            new_session = SpeedDatingSession(
                user1_id=user1_id,
                user2_id=user2_id,
                match_id=match_id,
                questions=questions,
                status='active',
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )

            self.session.add(new_session)
            await self.session.commit()
            await self.session.refresh(new_session)
            
            logger.info(f"Создана сессия спиддейтинга: {user1_id} ↔ {user2_id}")
            return new_session
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка создания сессии: {e}")
            return None

    async def get_active_session(self, user1_id: int, user2_id: int) -> Optional[SpeedDatingSession]:
        """Получить активную сессию между двумя пользователями"""
        try:
            result = await self.session.execute(
                select(SpeedDatingSession).where(
                    and_(
                        or_(
                            and_(
                                SpeedDatingSession.user1_id == user1_id,
                                SpeedDatingSession.user2_id == user2_id
                            ),
                            and_(
                                SpeedDatingSession.user1_id == user2_id,
                                SpeedDatingSession.user2_id == user1_id
                            )
                        ),
                        SpeedDatingSession.status == "active"
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Ошибка получения сессии: {e}")
            return None
    
    async def get_session_by_id(self, session_id: int) -> Optional[SpeedDatingSession]:
        """Получить сессию по ID"""
        try:
            result = await self.session.execute(
                select(SpeedDatingSession).where(SpeedDatingSession.id == session_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Ошибка получения сессии по ID: {e}")
            return None
    
    async def get_user_sessions(self, user_id: int) -> List[SpeedDatingSession]:
        """Получить все сессии пользователя"""
        try:
            result = await self.session.execute(
                select(SpeedDatingSession).where(
                    and_(
                        or_(
                            SpeedDatingSession.user1_id == user_id,
                            SpeedDatingSession.user2_id == user_id
                        ),
                        SpeedDatingSession.status == "active"
                    )
                )
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Ошибка получения сессий пользователя: {e}")
            return []

    async def save_answer(self, session_id: int, user_id: int, answer: str) -> Dict[str, Any]:
        try:
            session = await self.get_session_by_id(session_id)
            if not session:
                return {"success": False, "message": "Сессия не найдена"}

            q_idx = session.current_question_index

            if not session.answers:
                session.answers = {}
            if str(q_idx) not in session.answers:
                session.answers[str(q_idx)] = {}

            session.answers[str(q_idx)][str(user_id)] = answer
            flag_modified(session, "answers")
            question_completed = (len(session.answers[str(q_idx)]) == 2)
            if question_completed:
                session.current_question_index += 1

            session.updated_at = datetime.now(timezone.utc)
            await self.session.commit()

            return {
                "success": True,
                "question_completed": question_completed,
                "completed_question_index": q_idx
            }

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка сохранения ответа: {e}")
            return {"success": False, "message": "Ошибка сохранения ответа"}

    async def cancel_session(self, session_id: int) -> bool:
        """Отменить сессию спиддейтинга"""
        try:
            session = await self.get_session_by_id(session_id)
            if not session:
                return False
            
            session.status = "cancelled"
            session.updated_at = datetime.now(timezone.utc)
            

            match_repo = MatchRepository(self.session)
            await match_repo.archive_match(session.user1_id, session.user2_id)
            
            await self.session.commit()
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка отмены сессии: {e}")
            return False
    
    async def complete_session(self, session_id: int) -> bool:
        """Завершить сессию успешно"""
        try:
            session = await self.get_session_by_id(session_id)
            if not session:
                return False
            
            session.status = "completed"
            session.updated_at = datetime.now(timezone.utc)
            await self.session.commit()
            
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка завершения сессии: {e}")
            return False

    async def get_active_session_by_user_id(self, user_id: int):
        stmt = select(SpeedDatingSession).where(
            SpeedDatingSession.status == "active",
            or_(
                SpeedDatingSession.user1_id == user_id,
                SpeedDatingSession.user2_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()