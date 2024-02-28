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
