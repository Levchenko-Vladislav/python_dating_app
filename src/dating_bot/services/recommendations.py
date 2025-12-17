from typing import List, Dict, Optional
from src.dating_bot.services.compatibility import CompatibilityCalculator
import random


class RecommendationService:
    def __init__(self, db_session=None):
        self.db = db_session  # Пока заглушка, потом подключишь БД
    
    async def get_recommendations(self, user_id: int, limit: int = 10) -> List[Dict]:
        # TODO: Заменить на реальные данные из БД
        # Сейчас - заглушка с тестовыми анкетами
        
        test_profiles = [
            {
                "id": 1,
                "name": "Анна",
                "age": 25,
                "city": "Москва",
                "photo_id": "BQACAgIAAxkBAAEGb-hpQwvLq922LFtSo_3ujXq9B6xe8QAC6o4AAnx-GUoJqZZtQjl3XzYE",
                "gender": "Женщина 👩",
                "goal": "💘 Отношения",
                "test_answers": {1: 4, 2: 3, 3: 5, 4: 2, 5: 4, 6: 3, 7: 5, 8: 2, 9: 4, 10: 3},
                "compatibility": 78.5
            },
            {
                "id": 2, 
                "name": "Максим",
                "age": 28,
                "city": "Санкт-Петербург",
                "photo_id": "AgACAgIAAxkBAAEGb-RpQwujskicI0JFlTvbt_e1Lvyz6QACaBBrG3x-GUoxxMjCq-2hWwEAAwIAA20AAzYE",
                "gender": "Мужчина 🧑",
                "goal": "🫂 Дружба",
                "test_answers": {1: 2, 2: 4, 3: 3, 4: 5, 5: 1, 6: 4, 7: 2, 8: 5, 9: 3, 10: 2},
                "compatibility": 65.2
            },
        ]
        
        for profile in test_profiles[:limit]:
            if "compatibility" not in profile:
                # TODO: Реальный расчет совместимости с текущим пользователем
                profile["compatibility"] = round(random.uniform(50, 95), 1)
        
        return sorted(test_profiles, key=lambda x: x["compatibility"], reverse=True)
    
    async def like_profile(self, user_id: int, liked_profile_id: int) -> Dict:
        # TODO: Проверка на взаимный лайк в БД
        # Сейчас - случайный результат для демо
        
        is_mutual = random.choice([True, False])
        
        if is_mutual:
            return {
                "is_mutual": True,
                "matched_profile": {"name": "Тестовый пользователь", "id": liked_profile_id},
                "message": "🎉 У вас взаимная симпатия! Начнем Speed Dating?"
            }
        else:
            return {
                "is_mutual": False,
                "matched_profile": None,
                "message": "👍 Лайк отправлен! Ждем ответа..."
            }
    
    async def dislike_profile(self, user_id: int, disliked_profile_id: int):
        # TODO: Сохранение в БД что пользователь не хочет видеть эту анкету
        return {"status": "disliked", "profile_id": disliked_profile_id}