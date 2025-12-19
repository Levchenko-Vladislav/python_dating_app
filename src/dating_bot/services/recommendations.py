from typing import List, Dict, Optional, Any
from src.dating_bot.services.compatibility import CompatibilityCalculator
from src.dating_bot.database.session import AsyncSessionLocal
from src.dating_bot.database.repositories.user_repository import UserRepository
from src.dating_bot.database.repositories.test_result_repository import TestResultRepository
from src.dating_bot.database.repositories.like_repository import LikeRepository
import random


class RecommendationService:
    def __init__(self):
        self.compatibility_calculator = CompatibilityCalculator()

    async def get_recommendations(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Получить рекомендации для пользователя"""

        async with AsyncSessionLocal() as session:
            user_repo = UserRepository(session)
            test_repo = TestResultRepository(session)
            like_repo = LikeRepository(session)

            current_user = await user_repo.get_user_by_telegram_id(str(user_id))
            if not current_user:
                print(f"Пользователь {user_id} не найден в БД")
                return []

            current_test = await test_repo.get_test_result_by_user_id(current_user.id)

            recommendations = []
            for user in await user_repo.get_all_active_users():
                if user.id == current_user.id:
                    continue

                # Пропускаем лайкнутых/дизлайкнутых
                existing_like = await like_repo.get_like(current_user.id, user.id)
                if existing_like:
                    continue

                # Получаем результаты теста другого пользователя
                other_test = await test_repo.get_test_result_by_user_id(user.id)

                # Рассчитываем совместимость
                if current_test and current_test.is_completed and other_test and other_test.is_completed:
                    # Реальный расчет совместимости
                    compatibility = self.compatibility_calculator.calculate_compatibility(
                        current_test.answers,
                        other_test.answers
                    )
                    description = self.compatibility_calculator.get_compatibility_description(compatibility)
                else:
                    # Если у кого-то нет теста - случайная совместимость
                    compatibility = round(random.uniform(50, 95), 1)
                    description = "Предварительная оценка"

                profile = {
                    "id": user.id,
                    "name": user.name,
                    "age": user.age,
                    "city": user.city,
                    "photo_id": user.photo_id,
                    "gender": self._map_gender_to_ui(user.sex),
                    "goal": self._map_goal_to_ui(user.goal),
                    "compatibility": compatibility,
                    "compatibility_description": description
                }

                recommendations.append(profile)

            # Сортируем по совместимости
            recommendations.sort(key=lambda x: x["compatibility"], reverse=True)
            return recommendations[:limit]

    async def _get_random_profiles(self, current_user_id: int, limit: int, session) -> List[Dict]:
        """Получить случайные профили (когда нет теста)"""
        user_repo = UserRepository(session)
        all_users = await user_repo.get_all_active_users()

        random_profiles = []
        for user in all_users:
            if user.id == current_user_id:
                continue

            profile = {
                "id": user.id,
                "name": user.name,
                "age": user.age,
                "city": user.city,
                "photo_id": user.photo_id,
                "gender": self._map_gender_to_ui(user.sex),
                "goal": self._map_goal_to_ui(user.goal),
                "compatibility": round(random.uniform(50, 95), 1),
                "compatibility_description": "Предварительная оценка"
            }
            random_profiles.append(profile)

        random.shuffle(random_profiles)
        return random_profiles[:limit]

    def _check_basic_compatibility(self, user1, user2) -> bool:
        """Проверить базовую совместимость (пол, возраст, цель)"""
        # Проверка пола (если указаны предпочтения)
        if user1.search_sex and user1.search_sex != "any":
            if user1.search_sex != user2.sex:
                return False

        if user2.search_sex and user2.search_sex != "any":
            if user2.search_sex != user1.sex:
                return False

        # Проверка возраста
        if user1.min_age and user2.age and user2.age < user1.min_age:
            return False
        if user1.max_age and user2.age and user2.age > user1.max_age:
            return False

        if user2.min_age and user1.age and user1.age < user2.min_age:
            return False
        if user2.max_age and user1.age and user1.age > user2.max_age:
            return

        # Проверка цели (если оба ищут одно и то же)
        if user1.goal and user2.goal and user1.goal != user2.goal:
            # Можно смягчить эту проверку, если нужно
            pass

        return True

    def _map_gender_to_ui(self, gender_db: str) -> str:
        """Преобразовать пол из БД в UI формат"""
        if gender_db == "female":
            return "Женщина 👩"
        elif gender_db == "male":
            return "Мужчина 🧑"
        return gender_db or "Не указано"

    def _map_goal_to_ui(self, goal_db: str) -> str:
        """Преобразовать цель из БД в UI формат"""
        if goal_db == "relationship":
            return "💘 Отношения"
        elif goal_db == "friendship":
            return "🫂 Дружба"
        return goal_db or "Не указано"

    async def like_profile(self, user_telegram_id: int, profile_db_id: int) -> Dict:
        """Обработать лайк профиля"""
        print(f"\n=== LIKE_PROFILE ВЫЗВАН ===")
        print(f"   user_telegram_id (кто лайкает): {user_telegram_id}")
        print(f"   profile_db_id (кого лайкают - ID в БД): {profile_db_id}")

        try:
            # Получаем реальные ID из БД
            from src.dating_bot.services.user_service import UserService

            # 1. Находим ID в БД того, кто лайкает
            user_from_telegram_str = str(user_telegram_id)
            user_profile = await UserService.get_user_profile(user_from_telegram_str)

            if not user_profile or not user_profile.get('user'):
                print(f"Пользователь {user_telegram_id} не найден в БД")
                return {
                    "is_mutual": False,
                    "match_created": False,
                    "message": "Пользователь не найден"
                }

            user_from_db_id = user_profile['user'].id
            print(f"Кто лайкает: Telegram={user_telegram_id} → БД ID={user_from_db_id}")

            # 2. Находим пользователя, которому поставили лайк
            # profile_db_id - это уже ID в БД из анкеты!
            user_to_db_id = profile_db_id
            print(f"Кого лайкают: БД ID={user_to_db_id}")

            # Для проверки найдем информацию об этом пользователе
            from src.dating_bot.database.session import AsyncSessionLocal
            from src.dating_bot.database.repositories.user_repository import UserRepository

            async with AsyncSessionLocal() as session:
                user_repo = UserRepository(session)
                user_to = await user_repo.get_user_by_id(user_to_db_id)
                if user_to:
                    print(
                        f"Найден пользователь: ID={user_to.id}, Имя='{user_to.name}', Telegram={user_to.telegram_id}")
                else:
                    print(f"Пользователь с ID={user_to_db_id} не найден в БД")
                    return {
                        "is_mutual": False,
                        "match_created": False,
                        "message": "Анкета не найдена"
                    }

            print(f"Отправляем в LikeService: {user_from_db_id} → {user_to_db_id}")

            # Используем LikeService для обработки лайка
            from src.dating_bot.services.like_service import LikeService
            result = await LikeService.like_profile(user_from_db_id, user_to_db_id)

            print(f"Результат от LikeService: {result}")
            return result

        except Exception as e:
            print(f"Ошибка в like_profile: {e}")
            import traceback
            traceback.print_exc()
            return {
                "is_mutual": False,
                "match_created": False,
                "message": f"Ошибка: {str(e)}"
            }

    async def dislike_profile(self, user_id: int, disliked_profile_id: int) -> Dict:
        """Обработать дизлайк профиля"""
        try:
            print(f"DEBUG: dislike_profile вызван: user_id={user_id}, disliked_profile_id={disliked_profile_id}")

            # Получаем реальные ID из БД
            from src.dating_bot.services.user_service import UserService

            telegram_id_str = str(user_id)
            user_profile = await UserService.get_user_profile(telegram_id_str)

            if not user_profile or not user_profile.get('user'):
                print(f"DEBUG: Пользователь {user_id} не найден в БД")
                return {
                    "success": False,
                    "message": "Пользователь не найден"
                }

            user_from_id = user_profile['user'].id

            # Находим пользователя, которому поставили дизлайк
            disliked_user_profile = await UserService.get_user_profile(str(disliked_profile_id))
            if not disliked_user_profile or not disliked_user_profile.get('user'):
                print(f"DEBUG: Пользователь {disliked_profile_id} не найден в БД")
                return {
                    "success": False,
                    "message": "Анкета не найдена"
                }

            user_to_id = disliked_user_profile['user'].id

            print(f"DEBUG: ID в БД: user_from_id={user_from_id}, user_to_id={user_to_id}")

            # Используем LikeService для обработки дизлайка
            from src.dating_bot.services.like_service import LikeService
            result = await LikeService.dislike_profile(user_from_id, user_to_id)

            print(f"DEBUG: Результат dislike_profile: {result}")
            return result

        except Exception as e:
            print(f"ERROR: Ошибка в dislike_profile: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"Ошибка: {str(e)}"
            }