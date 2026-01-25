import pytest
from unittest.mock import patch
from src.dating_bot.services.compatibility import CompatibilityCalculator


class TestCompatibilityCalculator:
    @pytest.fixture
    def calculator(self):
        return CompatibilityCalculator()

    def test_calculate_compatibility_same_answers(self, calculator):
        with patch('src.dating_bot.services.compatibility.calculate_category_scores') as mock_calc:
            mock_calc.side_effect = [
                {"extraversion": 4.0, "neuroticism": 3.0},
                {"extraversion": 4.0, "neuroticism": 3.0}
            ]

            user1_answers = {1: 5, 2: 4}
            user2_answers = {1: 5, 2: 4}

            result = calculator.calculate_compatibility(user1_answers, user2_answers)

            assert result == pytest.approx(100.0, 0.1)

    def test_calculate_compatibility_different_answers(self, calculator):
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
        with patch('src.dating_bot.services.compatibility.calculate_category_scores') as mock_calc:
            mock_calc.side_effect = [
                {"extraversion": 3.0},
                {"neuroticism": 3.0}  # Разные категории
            ]

            result = calculator.calculate_compatibility({1: 5}, {2: 5})

            assert result == 50.0

    def test_calculate_compatibility_edge_cases(self, calculator):
        result = calculator.calculate_compatibility({}, {})
        assert result == 50.0

        result = calculator.calculate_compatibility(None, None)
        assert result == 50.0

