# bot.py

import json
import sqlite3

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.types import ReplyKeyboardRemove
import app.keyboards as kb


class Reg(StatesGroup):
    name = State()
    fraction = State()


# Загрузка токена из файла config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

TOKEN = config['telegram']['api_token']

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Имя файла базы данных SQLite
db_filename = 'users.db'


def create_users_table():
    """
    Создает таблицу 'users' в базе данных, если ее нет.
    Поля таблицы включают информацию о пользователях и их характеристиках в игре.
    """
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
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
            endurance INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def register_user(user: types.User, game_name: str, faction: str):
    """
    Регистрирует пользователя в базе данных со значениями по умолчанию для игровых характеристик.
    """
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (
            user_id, username, full_name, game_name, money, faction,
            level, experience, attack, defense, camouflage,
            search, agility, endurance
        ) VALUES (?, ?, ?, ?, 1000, ?, 1, 0, 0, 0, 0, 0, 0, 0)
    ''', (user.id, user.username, user.full_name, game_name, faction))
    conn.commit()
    conn.close()


@dp.message(Command('start'))
async def command_start_handler(message: Message, state: FSMContext):
    await message.answer("Привет, чтобы попасть в мир бесконечных сражений группировок хакеров тебе придется ответить "
                         "на пару моих вопросов. Начнем?")


@dp.message(Command('reg'))
async def command_reg_handler(message: Message, state: FSMContext):
    """
    Обработчик команды /start.
    Запрашивает у пользователя игровое имя и выбор фракции для регистрации в базе данных.
    """
    create_users_table()

    # Проверяем, зарегистрирован ли уже пользователь
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        await message.answer("Вы уже зарегистрированы в игре.")
        return
    await state.set_state(Reg.name)
    await message.answer("Для регистрации укажите свое игровое имя:")

    # register_user(message.from_user, game_name.text, faction.text)


@dp.message(F.text == "Я тут ")
async def stats_command_handler(message: Message) -> None:
    """
    Обработчик команды /stats.
    Отправляет пользователю его статистику в игре.
    """
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    user_data = cursor.fetchone()
    conn.close()

    if not user_data:
        await message.answer("Вы еще не зарегистрированы в игре.")
        return

    # Отправляем пользователю его статистику
    stats_message = (
        f"Статистика игрока {hbold(user_data[3])}:\n"
        f"Фракция: {user_data[5]}\n"
        f"Уровень: {user_data[6]}\n"
        f"Опыт: {user_data[7]}\n"
        f"Атака: {user_data[8]}\n"
        f"Защита: {user_data[9]}\n"
        f"Камуфляж: {user_data[10]}\n"
        f"Поиск: {user_data[11]}\n"
        f"Ловкость: {user_data[12]}\n"
        f"Выносливость: {user_data[13]}\n"
    )
    await message.answer(stats_message)


@dp.message(Reg.name)
async def reg_second(message: Message, state: FSMContext):
    print(type(message.text))
    if message.text != None:
        await state.update_data(name=message.text)
        await state.set_state(Reg.fraction)
        await message.answer('Выберите фракцию:', reply_markup=kb.main)
    else:
        await state.clear()
        await message.answer('Ну, не страшно, не все не могут просто напечатать своё имя....',
                             reply_markup=ReplyKeyboardRemove())


@dp.message(Reg.fraction)
async def second_third(message: Message, state: FSMContext):
    if message.text in [
        "🎭 Phantoms",
        "☮️ Liberty",
        "💠 Aegis",
        "🗿 NotFounds"
    ]:
        await state.update_data(fractions=message.text)
        data = await state.get_data()
        await message.answer(f'Поздравляю, ты прошел регистрацию!\nИмя: {data["name"]}\nФракция: {data["fractions"]}')
        await state.clear()
    else:
        await message.answer(f'Ты даже с таким простым вопросом не справился...\nКакой из тебя хакер')
        await state.clear()


@dp.message()
async def echo_handler(message: types.Message) -> None:
    """
    Обработчик для любых других сообщений, отправляет копию полученного сообщения.
    """
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Попробуйте еще раз!")


async def main() -> None:
    """
    Главная асинхронная функция для запуска бота.
    """
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)
