import sqlite3

conn = sqlite3.connect('dating_app.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(speed_dating_sessions)")
columns = cursor.fetchall()

print("✅ Окончательная структура таблицы speed_dating_sessions:")
print("-" * 50)
for col in columns:
    print(f"{col[0]:2}. {col[1]:25} ({col[2]:15}) {'NOT NULL' if col[3] else ''}")
print("-" * 50)

conn.close()