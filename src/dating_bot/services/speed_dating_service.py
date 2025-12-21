import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import random

from src.dating_bot.database.session import AsyncSessionLocal
from src.dating_bot.database.repositories.speed_dating_repository import SpeedDatingRepository
from src.dating_bot.database.repositories.match_repository import MatchRepository
from src.dating_bot.database.repositories.user_repository import UserRepository
from src.dating_bot.data.speed_dating_questions import get_random_questions

logger = logging.getLogger(__name__)


class SpeedDatingService:
    """Сервис для работы со спиддейтингом"""
    
    @staticmethod
    async def start_speed_dating(match_id: int) -> Dict[str, Any]:
        """Начать новую сессию спиддейтинга"""
        async with AsyncSessionLocal() as session:
            match_repo = MatchRepository(session)
            user_repo = UserRepository(session)
            speed_dating_repo = SpeedDatingRepository(session)
            
            # Получаем мэтч
            match = await match_repo.get_match_by_id(match_id)  # ← Теперь этот метод существует
            if not match:
                return {"success": False, "message": "Мэтч не найден"}
            
            # Проверяем, есть ли уже активная сессия
            existing_session = await speed_dating_repo.get_active_session(
                match.user1_id, match.user2_id
            )
            if existing_session:
                return {
                    "success": True,
                    "session": existing_session,
                    "is_new": False
                }
            
            # Получаем случайные вопросы
            questions = get_random_questions(5)

            if match_id % 2 == 0:
                current_responder_id = match.user1_id
            else:
                current_responder_id = match.user2_id
            logger.info(f"Создание сессии Speed Dating: мэтч {match_id}")
            logger.info(f"Пользователи: {match.user1_id} и {match.user2_id}")
            logger.info(f"Первый отвечающий: {current_responder_id}")
            # Создаем сессию
            new_session = await speed_dating_repo.create_session(
                user1_id=match.user1_id,
                user2_id=match.user2_id,
                match_id=match.id,
                questions=questions,
                current_responder_id=current_responder_id
            )
            
            if not new_session:
                return {"success": False, "message": "Не удалось создать сессию"}
            
            # Получаем информацию о пользователях для уведомлений
            user1 = await user_repo.get_user_by_id(match.user1_id)
            user2 = await user_repo.get_user_by_id(match.user2_id)
            
            return {
                "success": True,
                "session": new_session,
                "users": {
                    "user1": {
                        "id": user1.id,
                        "telegram_id": user1.telegram_id,
                        "name": user1.name
                    },
                    "user2": {
                        "id": user2.id,
                        "telegram_id": user2.telegram_id,
                        "name": user2.name
                    }
                },
                "is_new": True,
                "current_responder_id": current_responder_id
            }
    
    @staticmethod
    async def get_current_question(session_id: int) -> Dict[str, Any]:
        """Получить текущий вопрос сессии"""
        async with AsyncSessionLocal() as session:
            speed_dating_repo = SpeedDatingRepository(session)
            
            session_obj = await speed_dating_repo.get_session_by_id(session_id)
            if not session_obj:
                return {"success": False, "message": "Сессия не найдена"}
            
            if session_obj.current_question_index >= len(session_obj.questions):
                return {"success": False, "message": "Все вопросы пройдены"}
            
            question = session_obj.questions[session_obj.current_question_index]
            
            return {
                "success": True,
                "question": question,
                "question_number": session_obj.current_question_index + 1,
                "total_questions": len(session_obj.questions),
                "current_responder_id": session_obj.current_responder_id
            }
    
    @staticmethod
    async def submit_answer(session_id: int, user_id: int, answer: str) -> Dict[str, Any]:
        """Отправить ответ на вопрос"""
        async with AsyncSessionLocal() as session:
            speed_dating_repo = SpeedDatingRepository(session)
            
            # Сохраняем ответ
            saved = await speed_dating_repo.save_answer(session_id, user_id, answer)
            if not saved:
                return {"success": False, "message": "Ошибка сохранения ответа"}
            
            # Получаем обновленную сессию
            session_obj = await speed_dating_repo.get_session_by_id(session_id)
            if session_obj.current_responder_id == session_obj.user1_id:
                next_responder_id = session_obj.user2_id
            else:
                next_responder_id = session_obj.user1_id
                
            # Обновляем current_responder_id в БД
            await speed_dating_repo.update_current_responder(session_id, next_responder_id)
            # Проверяем, завершена ли сессия
            is_completed = session_obj.current_question_index >= len(session_obj.questions)
            
            if is_completed:
                await speed_dating_repo.complete_session(session_id)
            
            return {
                "success": True,
                "is_completed": is_completed,
                "next_responder_id": next_responder_id
            }
    
    @staticmethod
    async def cancel_session(session_id: int) -> Dict[str, Any]:
        """Отменить сессию"""
        async with AsyncSessionLocal() as session:
            speed_dating_repo = SpeedDatingRepository(session)
            
            cancelled = await speed_dating_repo.cancel_session(session_id)
            if not cancelled:
                return {"success": False, "message": "Ошибка отмены сессии"}
            
            return {"success": True, "message": "Сессия отменена"}
    
    @staticmethod
    async def get_session_info(session_id: int) -> Dict[str, Any]:
        """Получить информацию о сессии"""
        async with AsyncSessionLocal() as session:
            speed_dating_repo = SpeedDatingRepository(session)
            user_repo = UserRepository(session)
            
            session_obj = await speed_dating_repo.get_session_by_id(session_id)
            if not session_obj:
                return {"success": False, "message": "Сессия не найдена"}
            
            # Получаем информацию о пользователях
            user1 = await user_repo.get_user_by_id(session_obj.user1_id)
            user2 = await user_repo.get_user_by_id(session_obj.user2_id)
            
            # Получаем прогресс
            completed_answers = 0
            for q_idx in session_obj.answers:
                if len(session_obj.answers[q_idx]) == 2:
                    completed_answers += 1
            
            return {
                "success": True,
                "session": session_obj,
                "users": {
                    "user1": user1,
                    "user2": user2
                },
                "progress": {
                    "completed": completed_answers,
                    "total": len(session_obj.questions),
                    "current_question": session_obj.current_question_index + 1
                }
            }

    @staticmethod
    async def force_responder(session_id: int, user_id: int) -> Dict[str, Any]:
        """Принудительно установить отвечающего"""
        async with AsyncSessionLocal() as session:
            speed_dating_repo = SpeedDatingRepository(session)
            
            session_obj = await speed_dating_repo.get_session_by_id(session_id)
            if not session_obj:
                return {"success": False, "message": "Сессия не найдена"}
            
            # Проверяем, что пользователь участник сессии
            if user_id not in [session_obj.user1_id, session_obj.user2_id]:
                return {"success": False, "message": "Пользователь не участник сессии"}
            
            updated = await speed_dating_repo.update_current_responder(session_id, user_id)
            if not updated:
                return {"success": False, "message": "Ошибка обновления"}
            
            return {"success": True, "message": f"Теперь отвечает пользователь {user_id}"}
    
    @staticmethod
    async def switch_responder(session_id: int) -> Dict[str, Any]:
        """Переключить очередь ответа"""
        async with AsyncSessionLocal() as session:
            speed_dating_repo = SpeedDatingRepository(session)
            
            session_obj = await speed_dating_repo.get_session_by_id(session_id)
            if not session_obj:
                return {"success": False, "message": "Сессия не найдена"}
            
            # Определяем следующего отвечающего
            if session_obj.current_responder_id == session_obj.user1_id:
                next_responder_id = session_obj.user2_id
            else:
                next_responder_id = session_obj.user1_id
            
            updated = await speed_dating_repo.update_current_responder(session_id, next_responder_id)
            if not updated:
                return {"success": False, "message": "Ошибка переключения"}
            
            return {"success": True, "next_responder_id": next_responder_id}