import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
import sqlite3

# Загрузка токена из файла config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

TOKEN = config['telegram']['api_token']

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Имя файла базы данных SQLite
db_filename = 'users.db'


# Функция для создания таблицы пользователей в базе данных
def create_users_table():
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            username TEXT,
            full_name TEXT,
            game_name TEXT,
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


# Функция для регистрации пользователя в базе данных
def register_user(user: types.User, game_name: str, faction: str):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (
            user_id, username, full_name, game_name, faction,
            level, experience, attack, defense, camouflage,
            search, agility, endurance
        ) VALUES (?, ?, ?, ?, ?, 1, 0, 0, 0, 0, 0, 0, 0)
    ''', (user.id, user.username, user.full_name, game_name, faction))
    conn.commit()
    conn.close()


# Обработка команды /start
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    create_users_table()  # Создаем таблицу, если ее нет

    # Запрашиваем игровое имя
    await message.answer("Для регистрации укажите свое игровое имя:")
    game_name_message = await bot.send_message(message.chat.id, "Введите свое игровое имя:")
    game_name = await bot.wait_for('message', timeout=60)
    await bot.delete_message(chat_id=message.chat.id, message_id=game_name_message.message_id)

    # Запрашиваем выбор фракции
    factions_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton("🎭 Phantoms"),
        KeyboardButton("☮️ Liberty"),
        KeyboardButton("💠 Aegis"),
        KeyboardButton("🗿 NotFounds")
    )
    await message.answer("Выберите фракцию:", reply_markup=factions_keyboard)
    faction_message = await bot.send_message(message.chat.id, "Выберите фракцию:", reply_markup=factions_keyboard)
    faction = await bot.wait_for('message', timeout=60)
    await bot.delete_message(chat_id=message.chat.id, message_id=faction_message.message_id)

    # Регистрируем пользователя в базе данных
    register_user(message.from_user, game_name.text, faction.text)

    await message.answer(f"Привет, {hbold(message.from_user.full_name)}! Ты успешно зарегистрирован.")
    await message.answer("Теперь ты в игре! Удачи!")


# Обработка любых других сообщений
@dp.message()
async def echo_handler(message: types.Message) -> None:
    try:
        # Отправляем копию полученного сообщения
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # Не все типы поддерживаются для копирования, поэтому обрабатываем это
        await message.answer("Попробуйте еще раз!")


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)
