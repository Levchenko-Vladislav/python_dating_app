import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from dating_bot.config import BOT_TOKEN
from dating_bot.handlers import start, profile



async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(profile.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
