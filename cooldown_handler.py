import sqlite3
from datetime import datetime
import asyncio


async def remove_expired_cooldowns():
    while True:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM attack_cooldown WHERE cooldown_end <= ?', (int(datetime.now().timestamp()),))
        conn.commit()
        conn.close()
        await asyncio.sleep(60)
