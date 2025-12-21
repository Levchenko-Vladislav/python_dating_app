#!/usr/bin/env python3
import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорты ваших обработчиков
try:
    from src.dating_bot.handlers.start import router as start_router
    from src.dating_bot.handlers.profile import router as profile_router
    from src.dating_bot.handlers.menu import router as menu_router
    from src.dating_bot.handlers.psychological_test import router as test_router
    from src.dating_bot.handlers.browse import router as browse_router
    from src.dating_bot.handlers.speed_dating import router as speed_dating_router  # ← ЗАМЕНИТЕ matches на speed_dating!

    logger.info("Все обработчики импортированы")
except ImportError as e:
    logger.error(f"Ошибка импорта: {e}")
    logger.error("Проверьте структуру проекта и наличие __init__.py файлов")
    sys.exit(1)


async def main():
    # Получаем токен бота
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    if not BOT_TOKEN:
        # Попробуем прочитать из .env файла
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.strip() and '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if key == 'BOT_TOKEN':
                            BOT_TOKEN = value
                            break
        except FileNotFoundError:
            pass

        if not BOT_TOKEN:
            # Запросим у пользователя
            BOT_TOKEN = input("Введите токен бота: ").strip()

    if not BOT_TOKEN:
        logger.error("Токен бота не указан!")
        return

    logger.info("Инициализация базы данных...")
    try:
        from src.dating_bot.database.session import init_database
        await init_database()
        logger.info("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        return

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(menu_router)
    dp.include_router(test_router)
    dp.include_router(browse_router)
    dp.include_router(speed_dating_router)  # ← ЗАМЕНИТЕ matches на speed_dating!

    logger.info("Бот запускается...")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()