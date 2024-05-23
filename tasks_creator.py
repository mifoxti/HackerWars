import sqlite3

# Подключаемся к базе данных
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Создаем таблицу user_tasks
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_tasks (
    user_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    end_time DATETIME NOT NULL,
    PRIMARY KEY(user_id)
)
''')

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print("Таблица user_tasks успешно создана.")
