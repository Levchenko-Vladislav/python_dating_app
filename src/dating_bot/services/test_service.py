from typing import Optional, Dict, Any
from src.dating_bot.database.session import AsyncSessionLocal
from src.dating_bot.database.repositories.test_result_repository import TestResultRepository
from src.dating_bot.services.test_calculator import calculate_category_scores

class TestService:
    @staticmethod
    async def save_test_results(
            user_id: int,
            answers: Dict[int, int],
            is_completed: bool = True
    ) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            repo = TestResultRepository(session)
            category_scores = calculate_category_scores(answers)
            test_result = await repo.save_test_result(
                user_id=user_id,
                answers=answers,
                category_scores=category_scores,
                is_completed=is_completed
            )

            if test_result:
                return {
                    "success": True,
                    "test_result": test_result,
                    "category_scores": category_scores,
                    "message": "Результаты теста сохранены!"
                }
            else:
                return {
                    "success": False,
                    "test_result": None,
                    "message": "Ошибка сохранения результатов теста"
                }

    @staticmethod
    async def get_user_test_results(user_id: int) -> Optional[Dict[str, Any]]:
        async with AsyncSessionLocal() as session:
            repo = TestResultRepository(session)
            test_result = await repo.get_test_result_by_user_id(user_id)

            if test_result:
                return {
                    "answers": test_result.answers,
                    "category_scores": test_result.category_scores,
                    "answered_count": test_result.answered_count,
                    "is_completed": test_result.is_completed,
                    "completed_at": test_result.completed_at
                }
            return None

    @staticmethod
    async def delete_test_results(user_id: int) -> bool:
        async with AsyncSessionLocal() as session:
            repo = TestResultRepository(session)
            return await repo.delete_test_result(user_id)

    @staticmethod
    async def has_completed_test(user_id: int) -> bool:
        async with AsyncSessionLocal() as session:
            repo = TestResultRepository(session)
            return await repo.is_test_completed(user_id)