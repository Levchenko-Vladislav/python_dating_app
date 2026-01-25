from typing import Dict, Tuple
from src.dating_bot.services.test_calculator import calculate_category_scores

class CompatibilityCalculator:
    @staticmethod
    def calculate_compatibility(
            user1_answers,
            user2_answers
    ) -> float:
        def convert_keys(answers):
            if not answers:
                return {}
            if isinstance(answers, dict):
                result = {}
                for key, value in answers.items():
                    try:
                        result[int(key)] = int(value)
                    except (ValueError, TypeError):
                        result[key] = value
                return result
            return answers

        user1_answers_converted = convert_keys(user1_answers)
        user2_answers_converted = convert_keys(user2_answers)

        user1_scores = calculate_category_scores(user1_answers_converted)
        user2_scores = calculate_category_scores(user2_answers_converted)

        total_difference = 0
        compared_categories = 0

        for category in user1_scores:
            if category in user2_scores:
                score1 = user1_scores[category]
                score2 = user2_scores[category]
                difference = abs(score1 - score2)
                total_difference += difference
                compared_categories += 1

        if compared_categories == 0:
            return 50.0

        avg_difference = total_difference / compared_categories
        compatibility = 100 - (avg_difference * 25)
        compatibility = max(0, min(100, compatibility))

        return round(compatibility, 1)
    