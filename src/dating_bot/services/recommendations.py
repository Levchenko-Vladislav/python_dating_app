from typing import List, Dict, Optional, Any
from src.dating_bot.services.compatibility import CompatibilityCalculator
from src.dating_bot.database.session import AsyncSessionLocal
from src.dating_bot.database.repositories.user_repository import UserRepository
from src.dating_bot.database.repositories.test_result_repository import TestResultRepository
from src.dating_bot.database.repositories.like_repository import LikeRepository
import random
from src.dating_bot.database.repositories.match_repository import MatchRepository
import logging

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        self.compatibility_calculator = CompatibilityCalculator()

    async def get_recommendations(
        self, 
        user_id: int, 
        limit: int = 10,
        gender_filter: Optional[str] = None,
        goal_filter: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        city_filter: Optional[str] = None
    ) -> List[Dict]:
        async with AsyncSessionLocal() as session:
            user_repo = UserRepository(session)
            test_repo = TestResultRepository(session)
            like_repo = LikeRepository(session)
            match_repo = MatchRepository(session)

            # 1. Получаем текущего пользователя
            current_user = await user_repo.get_user_by_telegram_id(str(user_id))
            if not current_user:
                logger.warning(f"Пользователь {user_id} не найден в БД")
                return []


            # 2. Получаем тест текущего пользователя
            current_test = await test_repo.get_test_result_by_user_id(current_user.id)
            
            # 3. Собираем фильтры
            filters = self._build_filters(
                current_user=current_user,
                gender_filter=gender_filter,
                goal_filter=goal_filter,
                age_min=age_min,
                age_max=age_max,
                city_filter=city_filter
            )
            
            # 4. Получаем всех активных пользователей
            all_users = await user_repo.get_all_active_users()
            
            # 5. Фильтруем пользователей
            filtered_users = []
            for user in all_users:
                # Пропускаем себя
                if user.id == current_user.id:
                    continue
                
                # Проверяем базовую совместимость
                if not self._check_basic_compatibility(current_user, user, filters):
                    continue
                
                # Проверяем, не лайкали ли уже
                existing_like = await like_repo.get_like(current_user.id, user.id)
                if existing_like:
                    continue
                
                # Проверяем, нет ли уже мэтча
                existing_match = await match_repo.get_match(current_user.id, user.id)
                if existing_match:
                    continue
                
                filtered_users.append(user)
            
            
            # 7. Рассчитываем совместимость для отфильтрованных пользователей
            recommendations = []
            for user in filtered_users[:limit * 2]:  # Берем в 2 раза больше для сортировки
                other_test = await test_repo.get_test_result_by_user_id(user.id)
                
                # Рассчитываем совместимость
                compatibility, description = await self._calculate_compatibility(
                    current_test, other_test
                )
                
                # Импортируем маппинг
                try:
                    from src.dating_bot.services.data_mappers import map_gender_to_ui, map_goal_to_ui
                    gender_display = map_gender_to_ui(user.sex)
                    goal_display = map_goal_to_ui(user.goal)
                except ImportError:
                    # Fallback если маппинг не найден
                    gender_display = "Женщина 👩" if user.sex == "female" else "Мужчина 🧑" if user.sex == "male" else "Не указано"
                    goal_display = "💘 Отношения" if user.goal == "relationship" else "🫂 Дружба" if user.goal == "friendship" else "Не указано"
                
                profile = {
                    "id": user.id,
                    "name": user.name,
                    "age": user.age,
                    "city": user.city,
                    "photo_id": user.photo_id,
                    "gender": gender_display,
                    "goal": goal_display,
                    "compatibility": compatibility,
                    "compatibility_description": description,
                    "telegram_id": user.telegram_id,
                    "username": user.username
                }
                recommendations.append(profile)
            
            # 8. Сортируем по совместимости
            recommendations.sort(key=lambda x: x["compatibility"], reverse=True)
            final_recommendations = recommendations[:limit]            
            return final_recommendations


    async def _calculate_compatibility(self, current_test, other_test):
        """Рассчитать совместимость между двумя тестами"""
        if current_test and current_test.is_completed and other_test and other_test.is_completed:
            compatibility = self.compatibility_calculator.calculate_compatibility(
                current_test.answers,
                other_test.answers
            )
            description = self.compatibility_calculator.get_compatibility_description(compatibility)
        else:
            # Если нет тестов, генерируем случайную совместимость
            compatibility = round(random.uniform(50, 95), 1)
            description = "Предварительная оценка"
        
        return compatibility, description

    def _build_filters(
        self,
        current_user,
        gender_filter: Optional[str] = None,
        goal_filter: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        city_filter: Optional[str] = None
        ) -> Dict[str, Any]:
        """Построить словарь фильтров"""
        filters = {}
        
        # Фильтр по полу
        if gender_filter:
            filters['search_sex'] = gender_filter
        elif current_user.search_sex:
            filters['search_sex'] = current_user.search_sex
        else:
            filters['search_sex'] = 'any'
        
        # Фильтр по цели
        if goal_filter:
            filters['goal_filter'] = goal_filter
        elif current_user.goal:
            filters['goal_filter'] = current_user.goal
        else:
            filters['goal_filter'] = None
        
        return filters

    def _check_basic_compatibility(
        self, 
        current_user, 
        other_user, 
        filters: Dict[str, Any]
    ) -> bool:
        """
        Проверить базовую совместимость по фильтрам
        
        Логика:
        1. Текущий пользователь должен подходить под фильтры другого пользователя
        2. Другой пользователь должен подходить под фильтры текущего
        3. Учитываем цель (отношения/дружба)
        """
        
        # 1. Проверяем, что другой пользователь подходит под фильтры текущего
        # Фильтр по полу (кого ищет текущий пользователь)
        search_sex = filters.get('search_sex')
        if search_sex and search_sex != 'any':
            if not other_user.sex or other_user.sex != search_sex:
                return False
        
        # Фильтр по цели (если указан)
        goal_filter = filters.get('goal_filter')
        if goal_filter and goal_filter != 'any':
            if not other_user.goal or other_user.goal != goal_filter:
                # Для дружбы цель может быть любой
                if goal_filter != 'friendship':
                    return False
        
        # 2. Проверяем, что текущий пользователь подходит под фильтры другого
        # Проверка по полу (кого ищет другой пользователь)
        if other_user.search_sex and other_user.search_sex != 'any':
            if not current_user.sex or current_user.sex != other_user.search_sex:
                return False
        
        # Проверка по цели другого пользователя
        if other_user.goal and other_user.goal != 'any':
            if not current_user.goal or current_user.goal != other_user.goal:
                # Для дружбы цель может быть любой
                if other_user.goal != 'friendship':
                    return False
        
        # 3. Специальная логика для разных комбинаций целей
        if current_user.goal and other_user.goal:
            current_goal = current_user.goal
            other_goal = other_user.goal
            
            # Комбинации целей:
            # - отношения + отношения = ✓ (если пол подходит)
            # - дружба + дружба = ✓ (любой пол)
            # - отношения + дружба = ✗ (если отношения требуют взаимности)
            # - дружба + отношения = ✗ (если отношения требуют взаимности)
            
            if current_goal == 'relationship' and other_goal == 'friendship':
                # Текущий ищет отношения, другой - дружбу
                # Это несовместимо, если текущий не согласен на дружбу
                return False
                
            elif current_goal == 'friendship' and other_goal == 'relationship':
                # Текущий ищет дружбу, другой - отношения
                # Это несовместимо, если другой не согласен на дружбу
                return False
        
        
        return True


    async def like_profile(self, user_telegram_id: int, profile_db_id: int) -> Dict:
        print(f"\n=== LIKE_PROFILE ВЫЗВАН ===")
        print(f"   user_telegram_id (кто лайкает): {user_telegram_id}")
        print(f"   profile_db_id (кого лайкают - ID в БД): {profile_db_id}")

        try:
            from src.dating_bot.services.user_service import UserService

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

            user_to_db_id = profile_db_id
            print(f"Кого лайкают: БД ID={user_to_db_id}")

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
        try:
            print(f"DEBUG: dislike_profile вызван: user_id={user_id}, disliked_profile_id={disliked_profile_id}")

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

            disliked_user_profile = await UserService.get_user_profile(str(disliked_profile_id))
            if not disliked_user_profile or not disliked_user_profile.get('user'):
                print(f"DEBUG: Пользователь {disliked_profile_id} не найден в БД")
                return {
                    "success": False,
                    "message": "Анкета не найдена"
                }

            user_to_id = disliked_user_profile['user'].id

            print(f"DEBUG: ID в БД: user_from_id={user_from_id}, user_to_id={user_to_id}")

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