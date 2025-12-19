# test_test_service.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.dating_bot.services.test_service import TestService


class TestTestService:
    """Тесты для TestService"""

    @pytest.mark.asyncio
    async def test_save_test_results_success(self):
        """Тест успешного сохранения результатов теста"""
        with patch('src.dating_bot.services.test_service.AsyncSessionLocal') as mock_session:
            mock_repo = AsyncMock()
            mock_result = MagicMock()
            mock_repo.save_test_result.return_value = mock_result

            with patch('src.dating_bot.services.test_service.TestResultRepository', return_value=mock_repo):
                with patch('src.dating_bot.services.test_service.calculate_category_scores') as mock_calc:
                    mock_calc.return_value = {"extraversion": 4.5}

                    answers = {1: 5, 2: 4}
                    result = await TestService.save_test_results(1, answers)

                    assert result["success"] is True
                    assert result["test_result"] == mock_result
                    assert "сохранены" in result["message"]

    @pytest.mark.asyncio
    async def test_save_test_results_failure(self):
        """Тест неудачного сохранения результатов теста"""
        with patch('src.dating_bot.services.test_service.AsyncSessionLocal') as mock_session:
            mock_repo = AsyncMock()
            mock_repo.save_test_result.return_value = None

            with patch('src.dating_bot.services.test_service.TestResultRepository', return_value=mock_repo):
                with patch('src.dating_bot.services.test_service.calculate_category_scores'):
                    answers = {1: 5, 2: 4}
                    result = await TestService.save_test_results(1, answers)

                    assert result["success"] is False
                    assert result["test_result"] is None
                    assert "Ошибка" in result["message"]

    @pytest.mark.asyncio
    async def test_get_user_test_results_success(self):
        """Тест успешного получения результатов теста"""
        with patch('src.dating_bot.services.test_service.AsyncSessionLocal') as mock_session:
            mock_repo = AsyncMock()
            mock_result = MagicMock()
            mock_result.answers = {1: 5}
            mock_result.category_scores = {"extraversion": 4.5}
            mock_result.answered_count = 10
            mock_result.is_completed = True
            mock_result.completed_at = "2024-01-01"
            mock_repo.get_test_result_by_user_id.return_value = mock_result

            with patch('src.dating_bot.services.test_service.TestResultRepository', return_value=mock_repo):
                result = await TestService.get_user_test_results(1)

                assert result is not None
                assert result["answers"] == {1: 5}
                assert result["category_scores"] == {"extraversion": 4.5}
                assert result["answered_count"] == 10

    @pytest.mark.asyncio
    async def test_get_user_test_results_not_found(self):
        """Тест получения результатов теста, которых нет"""
        with patch('src.dating_bot.services.test_service.AsyncSessionLocal') as mock_session:
            mock_repo = AsyncMock()
            mock_repo.get_test_result_by_user_id.return_value = None

            with patch('src.dating_bot.services.test_service.TestResultRepository', return_value=mock_repo):
                result = await TestService.get_user_test_results(1)

                assert result is None

    @pytest.mark.asyncio
    async def test_delete_test_results_success(self):
        """Тест успешного удаления результатов теста"""
        with patch('src.dating_bot.services.test_service.AsyncSessionLocal') as mock_session:
            mock_repo = AsyncMock()
            mock_repo.delete_test_result.return_value = True

            with patch('src.dating_bot.services.test_service.TestResultRepository', return_value=mock_repo):
                result = await TestService.delete_test_results(1)

                assert result is True

    @pytest.mark.asyncio
    async def test_has_completed_test_true(self):
        """Тест проверки завершенности теста (True)"""
        with patch('src.dating_bot.services.test_service.AsyncSessionLocal') as mock_session:
            mock_repo = AsyncMock()
            mock_repo.is_test_completed.return_value = True

            with patch('src.dating_bot.services.test_service.TestResultRepository', return_value=mock_repo):
                result = await TestService.has_completed_test(1)

                assert result is True

    @pytest.mark.asyncio
    async def test_has_completed_test_false(self):
        """Тест проверки завершенности теста (False)"""
        with patch('src.dating_bot.services.test_service.AsyncSessionLocal') as mock_session:
            mock_repo = AsyncMock()
            mock_repo.is_test_completed.return_value = False

            with patch('src.dating_bot.services.test_service.TestResultRepository', return_value=mock_repo):
                result = await TestService.has_completed_test(1)

                assert result is False