import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dating_bot.database.session import init_database


async def migrate_database():
    """Выполнить миграцию базы данных"""
    try:
        await init_database()

    except Exception as e:
        print(f"Ошибка миграции: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(migrate_database())