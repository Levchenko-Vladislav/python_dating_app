import pytest
from unittest.mock import patch
from src.dating_bot.services.compatibility import CompatibilityCalculator


class TestCompatibilityCalculator:
    """Тесты для CompatibilityCalculator"""

    @pytest.fixture
    def calculator(self):
        return CompatibilityCalculator()

    def test_calculate_compatibility_same_answers(self, calculator):
        """Тест расчета совместимости с одинаковыми ответами"""
        with patch('src.dating_bot.services.compatibility.calculate_category_scores') as mock_calc:
            mock_calc.side_effect = [
                {"extraversion": 4.0, "neuroticism": 3.0},
                {"extraversion": 4.0, "neuroticism": 3.0}
            ]

            user1_answers = {1: 5, 2: 4}
            user2_answers = {1: 5, 2: 4}

            result = calculator.calculate_compatibility(user1_answers, user2_answers)

            # Нулевая разница = 100% совместимость
            assert result == pytest.approx(100.0, 0.1)

    def test_calculate_compatibility_different_answers(self, calculator):
        """Тест расчета совместимости с разными ответами"""
        with patch('src.dating_bot.services.compatibility.calculate_category_scores') as mock_calc:
            mock_calc.side_effect = [
                {"extraversion": 5.0, "neuroticism": 1.0},
                {"extraversion": 1.0, "neuroticism": 5.0}
            ]

            user1_answers = {1: 5}
            user2_answers = {1: 1}

            result = calculator.calculate_compatibility(user1_answers, user2_answers)

            assert result == pytest.approx(0.0, 0.1)


    def test_calculate_compatibility_no_common_categories(self, calculator):
        """Тест расчета совместимости без общих категорий"""
        with patch('src.dating_bot.services.compatibility.calculate_category_scores') as mock_calc:
            mock_calc.side_effect = [
                {"extraversion": 3.0},
                {"neuroticism": 3.0}  # Разные категории
            ]

            result = calculator.calculate_compatibility({1: 5}, {2: 5})

            # Нет общих категорий = 50% по умолчанию
            assert result == 50.0

    def test_calculate_compatibility_edge_cases(self, calculator):
        """Тест граничных случаев расчета совместимости"""
        # Пустые ответы
        result = calculator.calculate_compatibility({}, {})
        assert result == 50.0

        # None вместо ответов
        result = calculator.calculate_compatibility(None, None)
        assert result == 50.0

    def test_get_compatibility_description_high(self, calculator):
        """Тест получения описания высокой совместимости"""
        descriptions = []
        for percentage in [85, 90, 95, 100]:
            desc = calculator.get_compatibility_description(percentage)
            descriptions.append(desc)

        assert any("Идеальная" in desc for desc in descriptions)

    def test_get_compatibility_description_good(self, calculator):
        """Тест получения описания хорошей совместимости"""
        desc = calculator.get_compatibility_description(75)
        assert "Отличная" in desc

    def test_get_compatibility_description_medium(self, calculator):
        """Тест получения описания средней совместимости"""
        desc = calculator.get_compatibility_description(60)
        assert "Хорошая" in desc

        desc = calculator.get_compatibility_description(45)
        assert "Средняя" in desc

    def test_get_compatibility_description_low(self, calculator):
        """Тест получения описания низкой совместимости"""
        desc = calculator.get_compatibility_description(30)
        assert "Низкая" in desc