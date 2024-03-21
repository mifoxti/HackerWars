# Player.py

import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.state import State, StatesGroup

logging.basicConfig(level=logging.INFO)

bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher(bot)


class Player(StatesGroup):
    name = State()
    fraction = State()
    lvl = State()
    xp = State()
    attack = State()
    defense = State()
    mask = State()
    osint = State()
    stamina = State()
