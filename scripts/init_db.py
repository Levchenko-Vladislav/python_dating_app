import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.dating_bot.database.session import engine, Base


async def create_tables():
    """Создать все таблицы в БД"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Таблицы созданы!")
    print("Созданы таблицы:")
    for table in Base.metadata.tables:
        print(f"   - {table}")


async def main():
    """Основная функция"""
    print("Создание базы данных...")
    try:
        await create_tables()
        print("База данных готова!")
        print("Файл: dating_app.db")
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())