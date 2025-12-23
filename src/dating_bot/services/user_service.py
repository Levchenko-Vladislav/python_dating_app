import logging
from typing import Optional, Dict, Any
from datetime import datetime

from src.dating_bot.database.session import AsyncSessionLocal
from src.dating_bot.database.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    async def register_user(
            name: str,
            telegram_id: str,
            username: Optional[str] = None,
            age: Optional[int] = None,
            city: Optional[str] = None,
            sex: Optional[str] = None,
            photo_id: Optional[str] = None,
            goal: Optional[str] = None
    ) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)

            existing = await repo.get_user_by_telegram_id(telegram_id)
            if existing:
                logger.info(f"Пользователь {telegram_id} уже зарегистрирован")
                return {
                    "success": True,
                    "message": "Вы уже зарегистрированы!",
                    "user": existing,
                    "is_new": False
                }

            user = await repo.create_user(
                telegram_id=telegram_id,
                username=username,
                name=name,
                age=age,
                city=city,
                sex=sex,
                goal=goal,
                photo_id=photo_id
            )

            if user:
                logger.info(f"Зарегистрирован новый пользователь: {telegram_id}")
                return {
                    "success": True,
                    "message": "Регистрация успешна!",
                    "user": user,
                    "is_new": True
                }
            else:
                logger.error(f"Ошибка регистрации пользователя: {telegram_id}")
                return {
                    "success": False,
                    "message": "Ошибка регистрации. Попробуйте позже.",
                    "user": None,
                    "is_new": False
                }

    @staticmethod
    async def get_user_profile(telegram_id: str) -> Optional[Dict[str, Any]]:
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_user_by_telegram_id(telegram_id)

            if not user:
                return None

            days_on_platform = (datetime.utcnow() - user.created_at).days
            created_str = user.created_at.strftime("%d.%m.%Y")

            profile_text = (
                f"👤 Имя: {user.name}\n"
                f"🎂 Возраст: {user.age if user.age else 'Не указан'}\n"
                f"🏙 Город: {user.city if user.city else 'Не указан'}\n"
                f"👫 Пол: {user.sex if user.sex else 'Не указан'}\n"
                f"📱 Telegram: {user.username if user.username else f'ID: {telegram_id}'}\n"
                f"📅 В боте с: {created_str} ({days_on_platform} дней)\n"
                f"⭐ Статус: {'Активен ✅' if user.is_active else 'Неактивен ❌'}"
            )

            return {
                "user": user,
                "text": profile_text,
                "photo_id": user.photo_id,
                "has_photo": bool(user.photo_id),
                "is_active": user.is_active
            }

    @staticmethod
    async def update_user_profile(
            telegram_id: str,
            **fields
    ) -> Dict[str, Any]:

        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)

            user = await repo.get_user_by_telegram_id(telegram_id)
            if not user:
                return {
                    "success": False,
                    "message": "Пользователь не найден",
                    "user": None
                }

            updated = await repo.update_user(telegram_id, **fields)

            if updated:
                return {
                    "success": True,
                    "message": "Профиль обновлен",
                    "user": updated
                }
            else:
                return {
                    "success": False,
                    "message": "Ошибка обновления профиля",
                    "user": None
                }



    @staticmethod
    async def check_user_exists(telegram_id: str) -> bool:
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            return await repo.user_exists(telegram_id)

    @staticmethod
    async def get_user_stats() -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)

            total = await repo.count_users()
            active_users = await repo.get_all_active_users()
            active_count = len(active_users)

            ages = [u.age for u in active_users if u.age]
            avg_age = sum(ages) / len(ages) if ages else 0

            from collections import Counter
            cities = [u.city for u in active_users if u.city]
            city_counter = Counter(cities)
            top_cities = city_counter.most_common(5)

            return {
                "total_users": total,
                "active_users": active_count,
                "inactive_users": total - active_count,
                "average_age": round(avg_age, 1),
                "top_cities": top_cities
            }

async def delete_user_completely(telegram_id: str) -> bool:
    try:
        from src.dating_bot.database.session import AsyncSessionLocal
        from src.dating_bot.database.repositories.user_repository import UserRepository
        
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            result = await repo.delete_user_completely(telegram_id)
            
            if result:
                # Также можно очистить фото из Telegram (опционально)
                try:
                    from src.dating_bot.bot.bot import bot_instance
                    user_profile = await get_user_profile(telegram_id)
                    if user_profile and user_profile.get('user') and user_profile['user'].photo_id:
                        # Здесь можно добавить логику удаления фото
                        pass
                except:
                    pass
            
            return result
            
    except Exception as e:
        logger.error(f"Ошибка в сервисе удаления пользователя: {e}")
        return False