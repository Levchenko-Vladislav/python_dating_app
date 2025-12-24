import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dating_bot.database.session import init_database
from sqlalchemy import text 

async def migrate_database():
    try:
        from src.dating_bot.database.session import engine
        from sqlalchemy import inspect, text
        
        async with engine.connect() as conn:
            inspector = await conn.run_sync(lambda sync_conn: inspect(sync_conn))
            
            columns = await conn.run_sync(
                lambda sync_conn: inspector.get_columns('speed_dating_sessions')
            )
            
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")
            
            column_names = [col['name'] for col in columns]
            required_columns = ['current_responder_id', 'updated_at']
            
            for required_col in required_columns:
                if required_col not in column_names:
                    print(f"Колонка {required_col} отсутствует! Добавляем...")
                    await add_column(conn, required_col)
                else:
                    print(f"Колонка {required_col} уже существует.")
        
        await init_database()
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)

async def add_column(conn, column_name):
    try:
        if column_name == 'current_responder_id':
            sql = "ALTER TABLE speed_dating_sessions ADD COLUMN current_responder_id INTEGER"
        elif column_name == 'updated_at':
            sql = "ALTER TABLE speed_dating_sessions ADD COLUMN updated_at DATETIME"
        else:
            return
            
        await conn.execute(text(sql))
        await conn.commit()
    except Exception as e:
        print(f"Ошибка при добавлении колонки {column_name}: {e}")

if __name__ == "__main__":
    asyncio.run(migrate_database())