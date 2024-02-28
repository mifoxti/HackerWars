import logging

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

# Настройка системы логирования для отслеживания работы бота
logging.basicConfig(level=logging.INFO)

# Инициализация объектов бота и диспетчера
bot = Bot(token="YOUR_BOT_TOKEN")  # Замените "YOUR_BOT_TOKEN" на реальный токен вашего бота
dp = Dispatcher(bot)

# Определение состояний пользователя с использованием StatesGroup
class Player(StatesGroup):
    name = State()        # Состояние для получения имени игрока
    fraction = State()    # Состояние для получения фракции игрока
    lvl = State()         # Состояние для получения уровня игрока
    xp = State()          # Состояние для получения опыта игрока
    attack = State()      # Состояние для получения параметра "Атака" игрока
    defense = State()     # Состояние для получения параметра "Защита" игрока
    mask = State()        # Состояние для получения параметра "Маскировка" игрока
    osint = State()       # Состояние для получения параметра "OSINT" игрока
    stamina = State()     # Состояние для получения параметра "Выносливость" игрока
