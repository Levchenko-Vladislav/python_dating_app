"""
Сервис для расчета совместимости между пользователями
"""

from typing import Dict, Tuple
from src.dating_bot.services.test_calculator import calculate_category_scores


class CompatibilityCalculator:
    """Калькулятор совместимости на основе психологического теста"""
    
    @staticmethod
    def calculate_compatibility(
        user1_answers: Dict[int, int],
        user2_answers: Dict[int, int]
    ) -> float:
        """
        Упрощенный расчет совместимости
        
        Returns:
            совместимость в процентах (0-100)
        """
        user1_scores = calculate_category_scores(user1_answers)
        user2_scores = calculate_category_scores(user2_answers)
        
        if not user1_scores or not user2_scores:
            return 0.0
        
        total_difference = 0
        compared_categories = 0
        
        for category in user1_scores:
            if category in user2_scores:
                # Разница в баллах (0-4, где 0 - полное сходство)
                difference = abs(user1_scores[category] - user2_scores[category])
                total_difference += difference
                compared_categories += 1
        
        if compared_categories == 0:
            return 0.0
        
        avg_difference = total_difference / compared_categories
        compatibility = max(0, 100 - (avg_difference * 25))
        
        return round(compatibility, 1)
    
    @staticmethod
    def get_compatibility_description(percentage: float) -> str:
        """Возвращает текстовое описание уровня совместимости"""
        if percentage >= 85:
            return "🎯 Идеальная совместимость!"
        elif percentage >= 70:
            return "💖 Отличная совместимость!"
        elif percentage >= 55:
            return "👍 Хорошая совместимость."
        elif percentage >= 40:
            return "🤔 Средняя совместимость."
        else:
            return "🧐 Низкая совместимость."