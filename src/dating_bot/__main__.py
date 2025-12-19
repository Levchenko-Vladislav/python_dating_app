import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.dating_bot.config import BOT_TOKEN
from src.dating_bot.handlers import start, profile, psychological_test, menu, browse
from src.dating_bot.handlers.matches import router as matches_router





async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(psychological_test.router)
    dp.include_router(menu.router)
    dp.include_router(browse.router)
    dp.include_router(matches_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
