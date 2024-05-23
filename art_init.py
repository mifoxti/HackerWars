import sqlite3

db_filename = 'users.db'


def add_artifact(name, cost, attack, defense, camouflage, search, agility, endurance, req_lvl):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO artifacts (name, cost, attack, defense, camouflage, search, agility, endurance, req_lvl)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, cost, attack, defense, camouflage, search, agility, endurance, req_lvl))
    conn.commit()
    conn.close()


# Пример добавления артефакта
add_artifact('⌨️ Клавиатура для МукбАнга', 500, 10, 5, 0, 0, 0, 0, 1)
add_artifact('🖱 Мышь Дорана', 300, 0, 10, 0, 0, 5, 0, 1)
add_artifact('☎️ Доисторический телефон', 450, 4, 10, 3, 0, 2, 0, 2)
