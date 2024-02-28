import asyncio
import logging
import sys
from os import getenv
from bot import dp, bot, main  # Импорт необходимых модулей из файла bot

if __name__ == "__main__":
    # Настройка системы логирования для вывода информационных сообщений в стандартный поток вывода
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Запуск главной функции программы в асинхронном режиме
    asyncio.run(main())
