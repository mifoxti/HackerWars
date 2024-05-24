import sqlite3


# Функция для создания соединения с базой данных
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn


# Функция для создания таблицы заданий
def create_tasks_table(conn):
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                level_required INTEGER NOT NULL,
                stamina_cost INTEGER NOT NULL,
                duration INTEGER NOT NULL,
                reward_money INTEGER NOT NULL,
                reward_experience INTEGER NOT NULL,
                reward_artifact_chance INTEGER
            )
        ''')
    except sqlite3.Error as e:
        print(e)


# Функция для вставки задания в таблицу
def insert_task(conn, task_data):
    try:
        c = conn.cursor()
        c.execute('''
            INSERT INTO tasks (name, description, level_required, stamina_cost, duration, reward_money, reward_experience, reward_artifact_chance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', task_data)
        conn.commit()
        print("Задание успешно добавлено.")
    except sqlite3.Error as e:
        print(e)


# Функция для получения данных о задании от пользователя
def get_task_data():
    name = input("Введите название задания: ")
    description = input("Введите описание задания: ")
    level_required = int(input("Введите минимальный уровень для выполнения задания: "))
    stamina_cost = int(input("Введите стоимость выносливости для выполнения задания: "))
    duration = int(input("Введите время выполнения задания в минутах: "))
    reward_money = int(input("Введите сумму денег за выполнение задания: "))
    reward_experience = int(input("Введите количество опыта за выполнение задания: "))
    reward_artifact_chance = int(input("Введите шанс на получение артефакта (в процентах): "))
    return (
    name, description, level_required, stamina_cost, duration, reward_money, reward_experience, reward_artifact_chance)


def main():
    db_file = 'users.db'
    conn = create_connection(db_file)
    if conn is not None:
        create_tasks_table(conn)
        while True:
            task_data = get_task_data()
            insert_task(conn, task_data)
            choice = input("Хотите добавить еще одно задание? (yes/no): ")
            if choice.lower() != 'yes':
                break
        conn.close()
    else:
        print("Ошибка! Невозможно установить соединение с базой данных.")


if __name__ == '__main__':
    main()
