from typing import Dict, Any
from src.dating_bot.database.session import AsyncSessionLocal
from src.dating_bot.database.repositories.speed_dating_repository import SpeedDatingRepository
from src.dating_bot.database.repositories.match_repository import MatchRepository
from src.dating_bot.database.repositories.user_repository import UserRepository
from src.dating_bot.data.speed_dating_questions import get_random_questions

class SpeedDatingService:
    
    @staticmethod
    async def start_speed_dating(match_id: int) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            match_repo = MatchRepository(session)
            user_repo = UserRepository(session)
            speed_dating_repo = SpeedDatingRepository(session)


            match = await match_repo.get_match_by_id(match_id)  # ← Теперь этот метод существует
            if not match:
                return {"success": False, "message": "Мэтч не найден"}

            existing_session = await speed_dating_repo.get_active_session(match.user1_id, match.user2_id)
            if existing_session:
                user1 = await user_repo.get_user_by_id(match.user1_id)
                user2 = await user_repo.get_user_by_id(match.user2_id)

                return {
                    "success": True,
                    "session": existing_session,
                    "users": {
                        "user1": {
                            "id": user1.id,
                            "telegram_id": user1.telegram_id,
                            "name": user1.name,
                            "username": user1.username,
                        },
                        "user2": {
                            "id": user2.id,
                            "telegram_id": user2.telegram_id,
                            "name": user2.name,
                            "username": user2.username,
                        },
                    },
                    "is_new": False,
                }

            questions = get_random_questions(5)

            new_session = await speed_dating_repo.create_session(
                user1_id=match.user1_id,
                user2_id=match.user2_id,
                match_id=match.id,
                questions=questions
            )
            if not new_session:
                return {"success": False, "message": "Не удалось создать сессию"}

            user1 = await user_repo.get_user_by_id(match.user1_id)
            user2 = await user_repo.get_user_by_id(match.user2_id)

            return {
                "success": True,
                "session": new_session,
                "users": {
                    "user1": {
                        "id": user1.id,
                        "telegram_id": user1.telegram_id,
                        "name": user1.name,
                        "username": user1.username,
                    },
                    "user2": {
                        "id": user2.id,
                        "telegram_id": user2.telegram_id,
                        "name": user2.name,
                        "username": user2.username,
                    },
                },
                "is_new": True,
            }

    @staticmethod
    async def get_current_question(session_id: int) -> Dict[str, Any]:

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
            }
    
    @staticmethod
    async def submit_answer(session_id: int, user_id: int, answer: str) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            speed_dating_repo = SpeedDatingRepository(session)

            save_res = await speed_dating_repo.save_answer(session_id, user_id, answer)
            if not save_res.get("success"):
                return {"success": False, "message": save_res.get("message", "Ошибка сохранения ответа")}

            session_obj = await speed_dating_repo.get_session_by_id(session_id)
            if not session_obj:
                return {"success": False, "message": "Сессия не найдена"}

            is_completed = session_obj.current_question_index >= len(session_obj.questions)
            if is_completed:
                await speed_dating_repo.complete_session(session_id)

            return {
                "success": True,
                "is_completed": is_completed,
                "current_question_index": session_obj.current_question_index,
                "question_completed": save_res["question_completed"],
                "completed_question_index": save_res["completed_question_index"]
            }

    @staticmethod
    async def cancel_session(session_id: int) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            speed_dating_repo = SpeedDatingRepository(session)
            
            cancelled = await speed_dating_repo.cancel_session(session_id)
            if not cancelled:
                return {"success": False, "message": "Ошибка отмены сессии"}
            
            return {"success": True, "message": "Сессия отменена"}
    
    @staticmethod
    async def get_session_info(session_id: int) -> Dict[str, Any]:
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
    async def join_active_session(user_db_id: int) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            speed_dating_repo = SpeedDatingRepository(session)
            match_repo = MatchRepository(session)
            user_repo = UserRepository(session)

            session_obj = await speed_dating_repo.get_active_session_by_user_id(user_db_id)
            if not session_obj:
                return {
                    "success": False,
                    "message": "Активная сессия не найдена"
                }

            match = await match_repo.get_match_by_id(session_obj.match_id)
            if not match:
                return {
                    "success": False,
                    "message": "Мэтч не найден"
                }

            user1 = await user_repo.get_user_by_id(match.user1_id)
            user2 = await user_repo.get_user_by_id(match.user2_id)
            return {
                "success": True,
                "session": {
                    "id": session_obj.id,
                    "match_id": session_obj.match_id,
                    "user1_id": session_obj.user1_id,
                    "user2_id": session_obj.user2_id,
                },
                "users": {
                    "user1": {"id": user1.id, "telegram_id": user1.telegram_id, "name": user1.name,
                              "username": user1.username},
                    "user2": {"id": user2.id, "telegram_id": user2.telegram_id, "name": user2.name,
                              "username": user2.username},
                },
            }

    @staticmethod
    async def cancel_session_and_remove_match(session_id: int) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            speed_dating_repo = SpeedDatingRepository(session)

            session_obj = await speed_dating_repo.get_session_by_id(session_id)
            if not session_obj:
                return {"success": False, "message": "Сессия не найдена"}

            ok = await speed_dating_repo.cancel_session(session_id)
            if not ok:
                return {"success": False, "message": "Не удалось отменить сессию"}
            return {"success": True}

