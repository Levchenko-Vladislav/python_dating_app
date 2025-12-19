# test_test_calculator.py
import pytest
from src.dating_bot.services.test_calculator import (
    get_total_questions,
    get_question_by_id,
    get_questions_by_category,
    calculate_category_scores,
    format_results_for_display,
    calculate_test_completion_percentage,
    get_min_required_answers,
    is_test_complete
)
from unittest.mock import patch


class TestTestCalculator:
    """Тесты для функций калькулятора тестов"""

    def test_get_total_questions(self):
        """Тест получения общего количества вопросов"""
        # Это зависит от реальных данных в PSYCHOLOGICAL_TEST_QUESTIONS
        total = get_total_questions()
        assert isinstance(total, int)
        assert total >= 0

    def test_get_question_by_id_found(self):
        """Тест получения вопроса по ID (если существует)"""
        # Мок данных для теста
        with patch('src.dating_bot.services.test_calculator.PSYCHOLOGICAL_TEST_QUESTIONS',
                   [{"id": 1, "text": "Test question", "category": "test"}]):
            result = get_question_by_id(1)
            assert result is not None
            assert result["id"] == 1
            assert result["text"] == "Test question"

    def test_get_question_by_id_not_found(self):
        """Тест получения вопроса по несуществующему ID"""
        with patch('src.dating_bot.services.test_calculator.PSYCHOLOGICAL_TEST_QUESTIONS', []):
            result = get_question_by_id(999)
            assert result is None

    def test_get_questions_by_category(self):
        """Тест получения вопросов по категории"""
        # Мок данных для теста
        with patch('src.dating_bot.services.test_calculator.PSYCHOLOGICAL_TEST_QUESTIONS',
                   [{"id": 1, "category": "test"},
                    {"id": 2, "category": "test"},
                    {"id": 3, "category": "other"}]):
            result = get_questions_by_category("test")
            assert len(result) == 2
            assert all(q["category"] == "test" for q in result)

    def test_calculate_category_scores(self):
        """Тест расчета баллов по категориям"""
        # Мок данных для теста
        with patch('src.dating_bot.services.test_calculator.get_question_by_id') as mock_get_question:
            mock_get_question.side_effect = [
                {"id": 1, "category": "extraversion", "reverse_scored": False},
                {"id": 2, "category": "extraversion", "reverse_scored": True},
                {"id": 3, "category": "neuroticism", "reverse_scored": False}
            ]

            answers = {1: 5, 2: 4, 3: 3}  # Для reverse_scored: 4 -> 2 (6-4)
            result = calculate_category_scores(answers)

            # extraversion: (5 + (6-4)) / 2 = (5 + 2) / 2 = 3.5
            # neuroticism: 3 / 1 = 3
            assert "extraversion" in result
            assert "neuroticism" in result
            assert result["extraversion"] == pytest.approx(3.5, 0.01)
            assert result["neuroticism"] == pytest.approx(3.0, 0.01)

    def test_calculate_category_scores_empty(self):
        """Тест расчета баллов по категориям с пустыми ответами"""
        result = calculate_category_scores({})
        assert result == {}

    def test_format_results_for_display(self):
        """Тест форматирования результатов для отображения"""
        category_scores = {
            "extraversion": 4.5,
            "neuroticism": 2.0
        }

        with patch('src.dating_bot.services.test_calculator.QUESTION_CATEGORIES',
                   {"extraversion": "Экстраверсия", "neuroticism": "Невротизм"}):
            result = format_results_for_display(category_scores)

            assert "Экстраверсия" in result
            assert "Невротизм" in result
            assert "4.5/5" in result
            assert "2.0/5" in result
            assert "⭐" in result

    def test_format_results_for_display_empty(self):
        """Тест форматирования пустых результатов"""
        result = format_results_for_display({})
        assert "не найдены" in result

    def test_calculate_test_completion_percentage(self):
        """Тест расчета процента завершения теста"""
        with patch('src.dating_bot.services.test_calculator.get_total_questions', return_value=50):
            result = calculate_test_completion_percentage(25)
            assert result == 50.0  # 25/50 = 50%

    def test_get_min_required_answers(self):
        """Тест получения минимального количества ответов"""
        result = get_min_required_answers()
        assert result == 20

    def test_is_test_complete_true(self):
        """Тест проверки завершенности теста (True)"""
        assert is_test_complete(20) is True
        assert is_test_complete(25) is True

    def test_is_test_complete_false(self):
        """Тест проверки завершенности теста (False)"""
        assert is_test_complete(19) is False
        assert is_test_complete(0) is False