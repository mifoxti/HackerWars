# start_bot.py

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from bot import dp, TOKEN
from level_checker import check_and_update_player_levels


async def main():
    """
    Главная асинхронная функция для запуска бота.
    """
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    # Запуск асинхронной задачи для проверки уровня игроков
    asyncio.create_task(check_and_update_player_levels(bot))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
