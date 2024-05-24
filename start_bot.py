# start_bot.py

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from bot import dp, TOKEN
import sqlite3
from level_checker import check_and_update_player_levels
import nest_asyncio
from cooldown_handler import remove_expired_cooldowns

nest_asyncio.apply()

def create_tables():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Таблица active_attacks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_attacks (
            attacker_id INTEGER,
            target_id INTEGER,
            attack_time INTEGER
        )
    ''')

    # Таблица artifacts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            cost INTEGER,
            attack INTEGER,
            defense INTEGER,
            camouflage INTEGER,
            search INTEGER,
            agility INTEGER,
            endurance INTEGER,
            req_lvl INTEGER
        )
    ''')

    # Таблица tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            level_required INTEGER NOT NULL,
            stamina_cost INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            reward_money INTEGER NOT NULL,
            reward_experience INTEGER NOT NULL,
            reward_artifact_chance INTEGER NOT NULL
        )
    ''')

    # Таблица user_artifacts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_artifacts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            artifact_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(artifact_id) REFERENCES artifacts(id)
        )
    ''')

    # Таблица user_tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_tasks (
            user_id INTEGER NOT NULL,
            task_id INTEGER NOT NULL,
            end_time DATETIME NOT NULL,
            PRIMARY KEY(user_id)
        )
    ''')

    # Таблица users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            username TEXT,
            full_name TEXT,
            game_name TEXT,
            money INTEGER,
            faction TEXT,
            level INTEGER,
            experience INTEGER,
            attack INTEGER,
            defense INTEGER,
            camouflage INTEGER,
            search INTEGER,
            agility INTEGER,
            endurance INTEGER,
            status TEXT
        )
    ''')

    # Создание таблицы attack_cooldown, если она не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS attack_cooldown (
                        user_id INTEGER PRIMARY KEY,
                        cooldown_end INTEGER
                    )''')
    conn.commit()
    conn.close()

async def main():
    """
    Главная асинхронная функция для запуска бота.
    """
    # Создание таблиц перед запуском бота
    create_tables()
    print("Таблицы созданы или уже существуют.")

    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    # Запуск асинхронной задачи для проверки уровня игроков
    asyncio.create_task(check_and_update_player_levels(bot))

    # Запуск асинхронной задачи для удаления истекших кулдаунов
    asyncio.create_task(remove_expired_cooldowns())

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
