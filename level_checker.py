import asyncio
import sqlite3
from aiogram import Bot


async def check_and_update_player_levels(bot: Bot):
    """
    Проверяет и обновляет уровень игроков, если их опыт превышает необходимый для повышения уровня.
    """
    while True:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Получаем всех пользователей
        cursor.execute('SELECT user_id, experience, level FROM users')
        users = cursor.fetchall()

        # Список уровней и необходимого опыта для их достижения
        level_experience_thresholds = {
            1: 0,
            2: 100,
            3: 250,
            4: 500,
            5: 1000,
            6: 2000,
            7: 4000,
            8: 8000,
            9: 16000,
            10: 32000,
        }

        for user_id, experience, current_level in users:
            new_level = current_level
            for level, exp_threshold in level_experience_thresholds.items():
                if experience >= exp_threshold:
                    new_level = level
                else:
                    break

            if new_level != current_level:
                cursor.execute('UPDATE users SET level=? WHERE user_id=?', (new_level, user_id))
                await bot.send_message(user_id, f"Поздравляем! Ваш уровень повышен до {new_level}.")

        conn.commit()
        conn.close()

        # Ожидание перед следующей проверкой
        await asyncio.sleep(60)  # Проверять каждые 1 минут
