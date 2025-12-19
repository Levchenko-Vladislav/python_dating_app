"""
Сервис для расчета совместимости между пользователями
"""

from typing import Dict, Tuple
from src.dating_bot.services.test_calculator import calculate_category_scores


class CompatibilityCalculator:

    @staticmethod
    def calculate_compatibility(
            user1_answers,
            user2_answers
    ) -> float:
        """
        Упрощенный расчет совместимости
        """

        # Преобразуем ключи в int если они строки
        def convert_keys(answers):
            if not answers:
                return {}
            if isinstance(answers, dict):
                result = {}
                for key, value in answers.items():
                    try:
                        result[int(key)] = int(value)
                    except (ValueError, TypeError):
                        print(f"Неверный ключ или значение: {key}={value}")
                        result[key] = value
                return result
            return answers

        user1_answers_converted = convert_keys(user1_answers)
        user2_answers_converted = convert_keys(user2_answers)

        print(f"   User1 ответов: {len(user1_answers_converted)}")
        print(f"   User2 ответов: {len(user2_answers_converted)}")

        # Рассчитываем баллы по категориям
        user1_scores = calculate_category_scores(user1_answers_converted)
        user2_scores = calculate_category_scores(user2_answers_converted)


        print(f"   User1 баллы: {user1_scores}")
        print(f"   User2 баллы: {user2_scores}")

        total_difference = 0
        compared_categories = 0

        # Сравниваем все категории
        for category in user1_scores:
            if category in user2_scores:
                score1 = user1_scores[category]
                score2 = user2_scores[category]
                difference = abs(score1 - score2)
                total_difference += difference
                compared_categories += 1
                print(f"{category}: {score1} vs {score2} = разница {difference}")

        print(f"   Сравнено категорий: {compared_categories}")
        print(f"   Общая разница: {total_difference}")

        if compared_categories == 0:
            print("Нет общих категорий, возвращаем 50%")
            return 50.0

        avg_difference = total_difference / compared_categories
        print(f"Средняя разница: {avg_difference:.2f}")

        # Преобразуем разницу в совместимость
        # 0 разница = 100% совместимости
        # 4 разница = 0% совместимости
        compatibility = 100 - (avg_difference * 25)

        # Ограничиваем 0-100%
        compatibility = max(0, min(100, compatibility))

        print(f"Итоговая совместимость: {compatibility:.1f}%")

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