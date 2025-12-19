import logging
from typing import Optional, Dict, Any, Tuple, List

from src.dating_bot.database.session import AsyncSessionLocal
from src.dating_bot.database.repositories.like_repository import LikeRepository
from src.dating_bot.database.repositories.match_repository import MatchRepository
from src.dating_bot.database.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class LikeService:
    """Сервис для работы с лайками и мэтчами"""

    @staticmethod
    async def like_profile(user_from_db_id: int, user_to_db_id: int) -> Dict[str, Any]:


        async with AsyncSessionLocal() as session:
            like_repo = LikeRepository(session)
            match_repo = MatchRepository(session)
            user_repo = UserRepository(session)

            # Проверяем существование пользователей
            user_from = await user_repo.get_user_by_id(user_from_db_id)
            user_to = await user_repo.get_user_by_id(user_to_db_id)

            if not user_from or not user_to:
                return {
                    "is_mutual": False,
                    "match_created": False,
                    "message": "Пользователь не найден"
                }

            # Сохраняем лайк
            like = await like_repo.create_like(user_from_db_id, user_to_db_id, is_like=True)

            if not like:
                return {
                    "is_mutual": False,
                    "match_created": False,
                    "message": "Ошибка при сохранении лайка"
                }

            # Проверяем на взаимность
            is_mutual = await like_repo.check_mutual_like(user_from_db_id, user_to_db_id)
            match_created = False

            if is_mutual:
                # Создаем мэтч
                match = await match_repo.create_match(user_from_db_id, user_to_db_id)
                match_created = match is not None

                # Получаем информацию о другом пользователе
                other_user = user_to if user_from_db_id == user_from.id else user_from

                return {
                    "is_mutual": True,
                    "match_created": match_created,
                    "matched_with": {
                        "id": other_user.id,
                        "name": other_user.name,
                        "username": other_user.username,
                        "telegram_id": other_user.telegram_id  # Добавляем для уведомления
                    },
                    "message": f"🎉 У вас взаимная симпатия с {other_user.name}! Начнем Speed Dating?"
                }
            else:
                return {
                    "is_mutual": False,
                    "match_created": False,
                    "message": "❤️ Лайк отправлен! Ждем ответа..."
                }

    @staticmethod
    async def dislike_profile(user_from_db_id: int, user_to_db_id: int) -> Dict[str, Any]:
        """
        Поставить дизлайк профилю
        user_from_db_id: ID в БД того, кто ставит дизлайк
        user_to_db_id: ID в БД того, кому ставят дизлайк
        """
        print(f"DEBUG: LikeService.dislike_profile: {user_from_db_id} → {user_to_db_id}")

        async with AsyncSessionLocal() as session:
            like_repo = LikeRepository(session)
            user_repo = UserRepository(session)

            # Проверяем существование пользователей
            user_from = await user_repo.get_user_by_id(user_from_db_id)
            user_to = await user_repo.get_user_by_id(user_to_db_id)

            if not user_from or not user_to:
                return {
                    "success": False,
                    "message": "Пользователь не найден"
                }

            print(f"DEBUG: Пользователи найдены: {user_from.name} → {user_to.name}")

            # Сохраняем дизлайк (обновляем существующий лайк на дизлайк или создаем новый)
            like = await like_repo.create_like(user_from_db_id, user_to_db_id, is_like=False)

            if like:
                print(f"DEBUG: Дизлайк сохранен: {like}")
                return {
                    "success": True,
                    "message": "👎 Профиль пропущен"
                }
            else:
                print(f"DEBUG: Ошибка сохранения дизлайка")
                return {
                    "success": False,
                    "message": "Ошибка при сохранении дизлайка"
                }

    @staticmethod
    async def get_user_matches(user_id: int) -> List[Dict[str, Any]]:
        """
        Получить все мэтчи пользователя
        """
        async with AsyncSessionLocal() as session:
            match_repo = MatchRepository(session)
            user_repo = UserRepository(session)

            # Получаем пользователя
            user = await user_repo.get_user_by_telegram_id(str(user_id))
            if not user:
                return []

            # Получаем мэтчи
            matches = await match_repo.get_user_matches(user.id)

            result = []
            for match in matches:
                # Определяем, кто второй пользователь в мэтче
                other_user_id = match.user2_id if match.user1_id == user.id else match.user1_id
                other_user = await user_repo.get_user_by_id(other_user_id)

                if other_user:
                    result.append({
                        "match_id": match.id,
                        "user": {
                            "id": other_user.id,
                            "name": other_user.name,
                            "age": other_user.age,
                            "city": other_user.city,
                            "photo_id": other_user.photo_id,
                            "username": other_user.username
                        },
                        "matched_at": match.matched_at
                    })

            return result

    @staticmethod
    async def get_likes_received(user_id: int) -> List[Dict[str, Any]]:
        """
        Получить лайки, полученные пользователем
        """
        async with AsyncSessionLocal() as session:
            like_repo = LikeRepository(session)
            user_repo = UserRepository(session)

            user = await user_repo.get_user_by_telegram_id(str(user_id))
            if not user:
                return []

            likes = await like_repo.get_likes_received(user.id)

            result = []
            for like in likes:
                user_from = await user_repo.get_user_by_id(like.user_from_id)
                if user_from:
                    result.append({
                        "from_user": {
                            "id": user_from.id,
                            "name": user_from.name,
                            "age": user_from.age,
                            "city": user_from.city
                        },
                        "liked_at": like.created_at
                    })

            return result