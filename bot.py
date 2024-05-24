# bot.py
import asyncio
from datetime import datetime, timedelta
import json
import os
import sqlite3
import json
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold
from aiogram.types import ReplyKeyboardRemove
import app.keyboards as kb
from aiogram import F
import nest_asyncio
from random import randint

nest_asyncio.apply()


class fsm(StatesGroup):
    reg = State()
    name = State()
    fraction = State()
    menu = State()
    web = State()
    profile = State()
    fight = State()
    tasks = State()
    settings = State()
    shop = State()
    add_art = State()
    buy = State()
    tasks_init = State()
    broadcast = State()
    parry = State()
    ready_for_fight = State()
    settings = State()
    code_reviewer = State()
    generate_code = State()


# Загрузка токена из файла config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

TOKEN = config['telegram']['api_token']

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Имя файла базы данных SQLite
db_filename = 'users.db'


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
            search, agility, endurance, status
        ) VALUES (?, ?, ?, ?, 1000, ?, 1, 0, 0, 0, 0, 0, 0, 100, 'active')
    ''', (user.id, user.username, user.full_name, game_name, faction))
    conn.commit()
    conn.close()


@dp.message(Command('start'))
async def command_start_handler(message: Message, state: FSMContext):
    await message.answer("Привет, чтобы попасть в мир бесконечных сражений группировок хакеров тебе придется ответить "
                         "на пару моих вопросов. Начнем?", reply_markup=kb.start)


@dp.callback_query(F.data == 'reg')
async def reg_into(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(menu=callback.message.text)
    await command_reg_handler(callback.message, state)


@dp.message(fsm.reg)
async def command_reg_handler(message: Message, state: FSMContext):
    """
    Обработчик команды /reg.
    Запрашивает у пользователя игровое имя и выбор фракции для регистрации в базе данных.
    """
    # Проверяем, зарегистрирован ли уже пользователь
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        await message.answer("Вы уже зарегистрированы в игре.", reply_markup=kb.main_menu)
        await state.set_state(fsm.menu)
        return
    await state.set_state(fsm.name)
    await message.answer("Для регистрации укажите свое игровое имя:")


@dp.message(fsm.profile)
async def stats_command_handler(message: Message, state: FSMContext) -> None:
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
        f"👤 {hbold(user_data[4])} ({user_data[6]}):\n"
        f"💿 Уровень: {user_data[7]}\n"
        f"💡 Опыт: {user_data[8]}\n"
        f"💰 Деньги: {user_data[5]}\n"
        f"⚔️ Атака: {user_data[9]}\n"
        f"🛡 Защита: {user_data[10]}\n"
        f"📺 Камуфляж: {user_data[11]}\n"
        f"🔭 Поиск: {user_data[12]}\n"
        f"💻 Ловкость: {user_data[13]}\n"
        f"🔋 Выносливость: {user_data[14]}\n"
    )
    await state.set_state(fsm.menu)
    await message.answer(stats_message)


@dp.message(fsm.name)
async def reg_name_handler(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(name=message.text)
        await state.set_state(fsm.fraction)
        await message.answer('Выберите фракцию:', reply_markup=kb.main)
    else:
        await state.clear()
        await message.answer('Ну, не страшно, не все могут просто напечатать своё имя....',
                             reply_markup=ReplyKeyboardRemove())


@dp.message(fsm.fraction)
async def reg_fraction_handler(message: Message, state: FSMContext):
    if message.text in ["🎭 Phantoms", "☮️ Liberty", "💠 Aegis", "🗿 NotFounds"]:
        await state.update_data(fraction=message.text)
        data = await state.get_data()
        register_user(message.from_user, data['name'], data['fraction'])
        await message.answer(f'Поздравляю, ты прошел регистрацию!\nИмя: {data["name"]}\nФракция: {data["fraction"]}',
                             reply_markup=kb.main_menu)
        await state.set_state(fsm.menu)
    else:
        await message.answer(f'Ты даже с таким простым вопросом не справился...\nКакой из тебя хакер')
        await state.clear()


@dp.message(fsm.menu)
async def menu_handler(message: Message, state: FSMContext):
    if message.text in ["👤 Профиль", "🌐 Сеть", "🗡 Битва", "⌛️ Дела", "⚙️ Настройки"]:
        if message.text == "👤 Профиль":
            await state.update_data(menu=message.text)
            await stats_command_handler(message, state)
        elif message.text == "🌐 Сеть":
            await message.answer(f'Сеть - опасное место, но именно здесь находится много всего интересного.\n\n'
                                 f'🏪Магазин\n'
                                 f'На прилавках интернет-барахолок можно всегда найти самые разнообразные устройства.\n\n'
                                 f'🎪Казино\n'
                                 f'Очень опасные развлечения, которые могут как сделать вас богаче, так и лишить всех денег, что у вас есть.\n',
                                 reply_markup=kb.web_menu)
            await state.set_state(fsm.web)
        elif message.text == "⌛️ Дела":
            await message.answer(f'Хакер - тоже человек, а значит и обычными делами должен заниматься.')
            await state.update_data(menu=message.text)
            await tasks(message, state)
        elif message.text == "🗡 Битва":
            await message.answer(f'Битва - возможность испытать свои навыки в бою с другим пользователем.\n\n'
                                 f'Есть два игрока: А (атакующий) и З (защищающийся).\n'
                                 f'Атаковать можно в любое время, кроме времени "сна".\n'
                                 f'При выборе атаки А ищет игроков, у которых "маскировка" меньше, чем его "поиск".\n'
                                 f'Если игрок З "спит", его "защита" снижается на 5%, а если он "в отключке" — на 25%. Поэтому важно правильно распределять "выносливость".\n'
                                 f'Если "взлом" игрока А больше "защиты" игрока З, атака успешна. Награды за успешную атаку включают опыт и часть денег.\n'
                                 f'Если З не "спит" и не в "отключке", он получает уведомление о попытке "взлома" и может "парировать" атаку в течение 2 минут. Успех парирования зависит от "ловкости", и если она сработает, защита атакующего игрока уменьшается на 50%.',
                                 reply_markup=kb.fight_menu
                                 )
            await state.set_state(fsm.ready_for_fight)
        elif message.text == '⚙️ Настройки':
            await message.answer(
                f'В будущем, в настройках будет много всего интересного, а пока можно ввести подарочный код)',
                reply_markup=kb.settings_menu)
            await state.set_state(fsm.settings)
    elif message.text.split(' ')[0] == '/add_artifact' and message.from_user.id == 808305848:
        await state.update_data(menu=message.text)
        await add_artifact_handler(message, state)
    elif message.text.split(' ')[0] == '/broadcast' and message.from_user.id == 808305848:
        await state.update_data(menu=message.text)
        await broadcast_handler(message, state)
    elif message.text.split(' ')[0] == '/generate_code' and message.from_user.id == 808305848:
        await state.update_data(menu=message.text)
        await generate_code(message, state)
    else:
        await message.answer(f'Хм, кажется, такого выбора тебе не давали, не забывай свои права...')
        await state.set_state(fsm.menu)


@dp.message(fsm.settings)
async def settings_handler(message: Message, state: FSMContext):
    if message.text in ["🔑 Ввести код", "🔙 Домой"]:
        if message.text == "🔑 Ввести код":
            await state.update_data(settings_handler=message.text)
            await message.answer(f'Ожидаю ввод подарочного кода!')
            await state.set_state(fsm.code_reviewer)
        elif message.text == "🔙 Домой":
            stats_message = return_home(message)
            await message.answer(f'root@HackerWars:/$\n\n{stats_message}', reply_markup=kb.main_menu)
            await state.set_state(fsm.menu)
    else:
        await message.answer(f'Хм, кажется, такого выбора тебе не давали, не забывай свои права...')
        await state.set_state(fsm.menu)


@dp.message(fsm.code_reviewer)
async def code_reviewer(message: types.Message, state: FSMContext):
    # Получаем данные о пользователе из состояния
    user_data = await state.get_data()
    slovar = {
        "attack": '⚔️ Атака',
        "defense": '🛡 Защита',
        "camouflage": '📺 Камуфляж',
        "search": '🔭 Поиск',
        "agility": '💻 Ловкость',
        "endurance": '🔋 Выносливость',
    }
    # Получаем текст сообщения и извлекаем из него информацию о подарочном коде
    text = message.text

    code = text

    # Проверяем, есть ли такой код в базе данных или JSON-файле
    with open('gift_codes.json', 'r+') as file:
        data = json.load(file)
        if code not in data:
            await message.answer("Указанный подарочный код недействителен.", reply_markup=kb.main_menu)
            await state.set_state(fsm.menu)
            return

        # Проверяем, активировал ли текущий пользователь данный код
        if message.from_user.id in data[code]['activated_users']:
            await message.answer("Вы уже активировали данный подарочный код.", reply_markup=kb.main_menu)
            await state.set_state(fsm.menu)
            return

        # Получаем характеристики из подарочного кода
        characteristics = data[code]

        # Добавляем ID текущего пользователя в список активированных пользователей для данного кода
        characteristics['activated_users'].append(message.from_user.id)

        # Обновляем JSON-файл
        file.seek(0)
        json.dump(data, file)

    # Обновляем характеристики пользователя в базе данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    updated_characteristics = []

    for characteristic, value in characteristics.items():
        if value != 0 and characteristic != 'activated_users':
            cursor.execute(f"UPDATE users SET {characteristic} = {characteristic} + ? WHERE user_id = ?",
                           (value, message.from_user.id))
            updated_characteristics.append(f"{slovar[characteristic]} +{value}")

    # Применяем изменения в базе данных
    conn.commit()
    conn.close()

    # Обновляем данные пользователя в состоянии
    await state.update_data(user_data=user_data)

    # Отправляем сообщение о том, какие характеристики были улучшены
    if updated_characteristics:
        characteristics_message = "\n".join(updated_characteristics)
        await message.answer(f"Характеристики пользователя успешно обновлены:\n\n{characteristics_message}",
                             reply_markup=kb.main_menu)
    else:
        await message.answer("Подарочный код успешно активирован, но не было ненулевых характеристик для обновления.",
                             reply_markup=kb.main_menu)

    # Переходим в основное меню
    await state.set_state(fsm.menu)


@dp.message(fsm.generate_code)
async def generate_code(message: types.Message, state: FSMContext):
    # Получение текста сообщения и анализирование его для извлечения характеристик
    text = message.text.split(' ')
    if len(text) != 8:
        await message.answer(
            "Некорректное количество аргументов. Используйте: /generate_code [code] [attack] [defense] [camouflage] [search] [agility] [endurance]")
        return

    # Извлечение характеристик из текста сообщения
    try:
        code = text[1]
        attack = int(text[2])
        defense = int(text[3])
        camouflage = int(text[4])
        search = int(text[5])
        agility = int(text[6])
        endurance = int(text[7])
    except ValueError:
        await message.answer("Характеристики должны быть числами.")
        return

    # Сохранение подарочного кода и его характеристик в JSON-файле или базе данных
    with open('gift_codes.json', 'r+') as file:
        data = json.load(file)
        data[code] = {
            "attack": attack,
            "defense": defense,
            "camouflage": camouflage,
            "search": search,
            "agility": agility,
            "endurance": endurance,
            "activated_users": []  # Поле для хранения ID пользователей, активировавших данный код
        }
        file.seek(0)
        json.dump(data, file)

    # Отправка подарочного кода пользователю
    await message.answer(f"Сгенерирован новый подарочный код: {code}")
    await state.set_state(fsm.menu)


@dp.message(fsm.ready_for_fight)
async def ready_for_fight(message: types.Message, state: FSMContext):
    if message.text in ["🔪 Напасть", "🔙 Домой"]:
        if message.text == "🔪 Напасть":
            await state.update_data(fight_handler=message.text)
            await state.set_state(fsm.menu)
            await fight_handler(message, state)
        elif message.text == "🔙 Домой":
            stats_message = return_home(message)
            await message.answer(f'root@HackerWars:/$\n\n{stats_message}', reply_markup=kb.main_menu)
            await state.set_state(fsm.menu)
    else:
        print(1)
        await message.answer(f'Хм, кажется, такого выбора тебе не давали, не забывай свои права...')
        await state.set_state(fsm.menu)


# Вспомогательные функции для обновления и извлечения данных из БД
def get_user_data(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data


def update_user_data(user_id, field, value):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE users SET {field}=? WHERE user_id=?', (value, user_id))
    conn.commit()
    conn.close()


def find_targets(attacker_search, attacker_faction):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users WHERE camouflage < ? AND faction != ?',
                   (attacker_search, attacker_faction))
    potential_targets = cursor.fetchall()
    conn.close()

    # Исключаем цели, которые находятся на кулдауне
    targets = [target[0] for target in potential_targets if not is_user_on_cooldown(target[0])]
    return targets


@dp.message(fsm.fight)
async def fight_handler(message: types.Message, state: FSMContext):
    print(1)
    attacker_id = message.from_user.id
    attacker_data = get_user_data(attacker_id)

    if not attacker_data:
        await message.answer("Не удалось найти ваши данные. Пожалуйста, зарегистрируйтесь в игре.")
        return

    attacker_search = attacker_data[12]  # Поле "Поиск"
    attacker_attack = attacker_data[9]  # Поле "Атака"
    attacker_faction = attacker_data[6]  # Поле "Фракция"
    attacker_lvl = attacker_data[7]
    attacker_name = f'{attacker_faction[0]} {attacker_data[4]} 💿{attacker_lvl}'

    # Проверка на активную атаку
    if is_user_on_cooldown(attacker_id):
        await message.answer("Вы уже атакуете цель. Дождитесь завершения текущей атаки.", reply_markup=kb.main_menu)
        await state.set_state(fsm.menu)
        return

    # Поиск цели
    targets = find_targets(attacker_search, attacker_faction)
    if not targets:
        await message.answer("Не удалось найти подходящих целей для атаки.", reply_markup=kb.main_menu)
        await state.set_state(fsm.menu)
        return

    target_id = targets[randint(0, len(targets) - 1)]
    target_data = get_user_data(target_id)
    target_defense = target_data[10]  # Поле "Защита"
    target_status = target_data[15]  # Поле "Статус" (например, "активен", "спит", "отруб")
    target_agility = target_data[13]  # Поле "Ловкость"
    target_faction = target_data[6]  # Поле "Фракция"
    target_lvl = target_data[7]
    target_name = f'{target_faction[0]} {target_data[4]} 💿{target_lvl}'
    # Применение штрафов к защите в зависимости от статуса
    if target_status == 'sleeping':
        target_defense *= 0.95
    elif target_status == 'unconscious':
        target_defense *= 0.75

    # Сохраняем атаку в базе данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO active_attacks (attacker_id, target_id, attack_time) VALUES (?, ?, ?)',
                   (attacker_id, target_id, int(datetime.now().timestamp())))
    conn.commit()
    conn.close()

    # Уведомление цели с возможностью парирования атаки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Парировать атаку", callback_data=f"parry_{attacker_id}")]
    ])
    try:
        await bot.send_message(target_id,
                               f"Вас атакует {attacker_name}\nВы можете попытаться парировать атаку в течение 2 минут.",
                               reply_markup=keyboard)
    except Exception as e:
        print(f"Не удалось отправить сообщение пользователю {target_id}: {e}")

    await message.answer(f"Вы напали на {target_name}\nОжидайте результат атаки.", reply_markup=kb.main_menu)

    # Запуск ожидания парирования атаки
    await asyncio.sleep(120)

    # Проверяем, существует ли еще активная атака (пользователь не парировал)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM active_attacks WHERE attacker_id = ?', (attacker_id,))
    active_attack = cursor.fetchone()
    conn.close()

    if active_attack:
        # Если атака все еще активна, то продолжаем выполнение
        await check_parry(attacker_id, target_id, target_agility, target_defense, state)
        await state.set_state(fsm.parry)
    else:
        # Если атака уже не активна (пользователь парировал), то просто выходим из функции
        return


@dp.message(fsm.parry)
async def check_parry(attacker_id, target_id, target_agility, target_defense, state: FSMContext):
    await state.set_state(fsm.parry)
    target_data = get_user_data(target_id)
    attacker_data = get_user_data(attacker_id)

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Проверка успешности парирования
    if target_agility > attacker_data[10] * 0.5:
        update_user_data(attacker_id, 'defense', attacker_data[10] * 0.5)
        await bot.send_message(attacker_id, "Ваша атака была парирована! Ваша защита была уменьшена на 50%.",
                               reply_markup=kb.main_menu)
        await bot.send_message(target_id, "Вы пробуете парировать атаку!", reply_markup=kb.main_menu)

        # Удаление атаки из базы данных
        cursor.execute('DELETE FROM active_attacks WHERE attacker_id=? AND target_id=?', (attacker_id, target_id))
        # Установка кулдауна для цели
        cooldown_end = datetime.now() + timedelta(hours=1)
        cursor.execute('INSERT OR REPLACE INTO attack_cooldown (user_id, cooldown_end) VALUES (?, ?)',
                       (target_id, int(cooldown_end.timestamp())))
        conn.commit()
        conn.commit()
    else:
        # Пример награды деньгами
        reward_money = round(target_data[7] * 0.1)
        reward_experience = 100  # Пример награды опытом

        # Обновление данных атакующего
        update_user_data(attacker_id, 'money', round(attacker_data[7] + reward_money))
        update_user_data(attacker_id, 'experience', attacker_data[8] + reward_experience)

        # Обновление данных цели
        update_user_data(target_id, 'money', round(target_data[7] - reward_money))

        await bot.send_message(target_id, f"Вам не удалось парировать атаку. Вы потеряли {reward_money} монет.",
                               reply_markup=kb.main_menu)
        await bot.send_message(attacker_id,
                               f"Атака успешна! Вы получили {reward_money} монет и {reward_experience} опыта.",
                               reply_markup=kb.main_menu)

        # Удаление атаки из базы данных
        cursor.execute('DELETE FROM active_attacks WHERE attacker_id=? AND target_id=?', (attacker_id, target_id))
        conn.commit()

        # Установка кулдауна для цели
        cooldown_end = datetime.now() + timedelta(hours=1)
        cursor.execute('INSERT OR REPLACE INTO attack_cooldown (user_id, cooldown_end) VALUES (?, ?)',
                       (target_id, int(cooldown_end.timestamp())))
        conn.commit()
    conn.close()
    await state.set_state(fsm.menu)
    return


def is_user_on_cooldown(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT cooldown_end FROM attack_cooldown WHERE user_id=?', (user_id,))
    cooldown = cursor.fetchone()
    conn.close()
    if cooldown:
        cooldown_end = datetime.fromtimestamp(cooldown[0])
        return datetime.now() < cooldown_end
    return False


def is_target_under_attack(target_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM active_attacks WHERE target_id=?', (target_id,))
    active_attack = cursor.fetchone()
    conn.close()
    return active_attack is not None


@dp.message(fsm.parry)
async def parry_attack(attacker_id, target_id, target_agility, attacker_defense, state: FSMContext):
    # await asyncio.sleep(20)  # Ожидание 2 минут
    await state.set_state(fsm.parry)
    await bot.send_message(attacker_id, "Ваша атака была парирована! Ваша защита была уменьшена на 50%.",
                           reply_markup=kb.main_menu)
    await bot.send_message(target_id, "Вы пробуете парировать атаку!", reply_markup=kb.main_menu)
    target_data = get_user_data(target_id)
    attacker_data = get_user_data(attacker_id)

    # Проверка успешности парирования
    if target_agility > attacker_defense * 0.5:
        # update_user_data(attacker_id, 'defense', attacker_defense * 0.5)
        # Обновление данных защищающегося
        reward_money = round(attacker_data[5] * 0.1)  # Пример награды деньгами
        reward_experience = 100  # Пример награды опытом
        update_user_data(target_id, 'money', round(target_data[5] + reward_money))
        update_user_data(target_id, 'experience', target_data[8] + reward_experience)

        # Обновление данных цели
        update_user_data(attacker_id, 'money', round(attacker_data[5] - reward_money))

        await bot.send_message(attacker_id,
                               "Вашей защиты не хватило, чтобы переиграть цель. Охотник превратился в добычу..."
                               "\n\n"
                               " Вы потеряли часть своих монет.", reply_markup=kb.main_menu)
        await bot.send_message(target_id, "Вашей ловкости хватило, чтобы переиграть гадкого воришку!",
                               reply_markup=kb.main_menu)
        # Удаление атаки из базы данных
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM active_attacks WHERE attacker_id=? AND target_id=?', (attacker_id, target_id))

        conn.commit()
        # Установка кулдауна для цели
        cooldown_end = datetime.now() + timedelta(hours=1)
        cursor.execute('INSERT OR REPLACE INTO attack_cooldown (user_id, cooldown_end) VALUES (?, ?)',
                       (target_id, int(cooldown_end.timestamp())))
        conn.commit()
        conn.close()
    else:
        reward_money = round(target_data[5] * 0.1)  # Пример награды деньгами
        reward_experience = 100  # Пример награды опытом

        # Обновление данных атакующего
        update_user_data(attacker_id, 'money', round(attacker_data[5] + reward_money))
        update_user_data(attacker_id, 'experience', attacker_data[8] + reward_experience)

        # Обновление данных цели
        update_user_data(target_id, 'money', round(target_data[5] - reward_money))

        await bot.send_message(target_id, f"Вам не удалось парировать атаку. Вы потеряли {reward_money} монет.",
                               reply_markup=kb.main_menu)
        await bot.send_message(attacker_id,
                               f"Атака успешна! Вы получили {reward_money} монет и {reward_experience} опыта.",
                               reply_markup=kb.main_menu)

        # Удаление атаки из базы данных
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM active_attacks WHERE attacker_id=? AND target_id=?', (attacker_id, target_id))
        conn.commit()
        # Установка кулдауна для цели
        cooldown_end = datetime.now() + timedelta(hours=1)
        cursor.execute('INSERT OR REPLACE INTO attack_cooldown (user_id, cooldown_end) VALUES (?, ?)',
                       (target_id, int(cooldown_end.timestamp())))
        conn.commit()
        conn.close()
    await state.set_state(fsm.menu)
    return


@dp.callback_query(F.data.startswith('parry_'))
async def process_callback_parry(callback_query: types.CallbackQuery, state: FSMContext):
    attacker_id = int(callback_query.data.split('_')[1])
    target_id = callback_query.from_user.id
    target_data = get_user_data(target_id)
    attacker_data = get_user_data(attacker_id)

    if target_data and attacker_data:
        await callback_query.answer('Атака парирована, ожидаем результаты боя', reply_markup=kb.main_menu)
        await parry_attack(attacker_id, target_id, target_data[13], attacker_data[10],
                           state)  # Поля "Ловкость" и "Защита"
    else:
        await bot.answer_callback_query(callback_query.id, text="Ошибка при обработке данных пользователя.")


def is_user_on_cooldown(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT cooldown_end FROM attack_cooldown WHERE user_id=?', (user_id,))
    cooldown = cursor.fetchone()
    conn.close()
    if cooldown:
        cooldown_end = datetime.fromtimestamp(cooldown[0])
        return datetime.now() < cooldown_end
    return False


@dp.message(fsm.parry)
async def parry_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    # Проверьте, есть ли у пользователя активная атака
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM active_attacks WHERE target_id=?', (user_id,))
    attack = cursor.fetchone()
    conn.close()

    if attack:
        attacker_id = attack[1]
        attacker_data = get_user_data(attacker_id)
        target_data = get_user_data(user_id)

        await parry_attack(attacker_id, user_id, target_data[13], attacker_data[10],
                           state)  # Поля "Ловкость" и "Защита"
    else:
        await message.answer("Нет активных атак, которые можно парировать.", reply_markup=kb.main_menu)

    await state.set_state(fsm.menu)


@dp.message(fsm.tasks)
async def tasks(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Подключаемся к базе данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Извлекаем уровень игрока
    cursor.execute('SELECT level FROM users WHERE user_id=?', (user_id,))
    user_level = cursor.fetchone()

    if user_level:
        user_level = user_level[0]

        # Извлекаем задачи, где level_required <= уровню игрока
        cursor.execute('SELECT * FROM tasks WHERE level_required <= ?', (user_level,))
        tasks = cursor.fetchall()
        buttons = []
        row = []
        # Формируем сообщение с доступными задачами
        tasks_message = "Доступные задачи:\n\n"
        for task in tasks:
            task_id, name, description, level_required, stamina_cost, duration, reward_money, reward_experience, reward_artifact_chance = task
            tasks_message += (f"{name}\n"
                              f"{description}\n"
                              f"💿 Требуемый уровень: {level_required}\n"
                              f"🔥 Стоимость выносливости: {stamina_cost}\n"
                              f"🕔 Время выполнения: {duration} минут\n"
                              f"💰 Награда (деньги): {reward_money}\n"
                              f"💡 Награда (опыт): {reward_experience}\n\n")
            row.append(KeyboardButton(text=name))
            if len(row) == 2:
                buttons.append(row)
                row = []

        if row:
            buttons.append(row)
        buttons.append([KeyboardButton(text='🔙 Домой')])
        keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer(tasks_message, reply_markup=keyboard)
        await state.set_state(fsm.tasks_init)
    else:
        await message.answer("Ваш уровень не найден. Пожалуйста, зарегистрируйтесь в игре.")

    # Закрываем соединение с базой данных
    conn.close()


def get_user_artifacts(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_artifacts WHERE user_id=?', (user_id,))
    artifacts = cursor.fetchall()
    conn.close()
    return artifacts


def calculate_stamina_with_artifacts(base_stamina, artifacts):
    additional_stamina = sum(artifact[3] for artifact in
                             artifacts)  # Предполагая, что 4-й столбец в таблице артефактов это бонус к выносливости
    return base_stamina + additional_stamina


@dp.message(fsm.tasks_init)
async def tasks_init(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Подключаемся к базе данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Извлекаем уровень игрока
    cursor.execute('SELECT level FROM users WHERE user_id=?', (user_id,))
    user_level = cursor.fetchone()
    if user_level:
        user_level = user_level[0]

        # Извлекаем задачи, где level_required <= уровню игрока
        cursor.execute('SELECT * FROM tasks WHERE level_required <= ?', (user_level,))
        tasks = cursor.fetchall()
        task_names = [task[1] for task in tasks]

        if message.text in task_names:
            # Проверяем, выполняет ли пользователь уже задачу
            cursor.execute('SELECT * FROM user_tasks WHERE user_id=?', (user_id,))
            current_task = cursor.fetchone()
            if current_task:
                await message.answer("Вы уже выполняете задачу. Дождитесь её завершения.")
                conn.close()
                return

            # Извлекаем выбранную задачу
            cursor.execute('SELECT * FROM tasks WHERE name=?', (message.text,))
            task = cursor.fetchone()
            if task:
                task_id, name, description, level_required, stamina_cost, duration, reward_money, reward_experience, reward_artifact_chance = task

                if name == "🥱 Спать":
                    # Устанавливаем статус "sleeping"
                    cursor.execute('UPDATE users SET status=? WHERE user_id=?', ('sleeping', user_id))
                    conn.commit()
                    conn.close()

                    # Запускаем таймер выполнения задачи
                    end_time = datetime.now() + timedelta(minutes=duration)
                    asyncio.create_task(complete_task(user_id, task_id, end_time))

                    await message.answer(f"Вы начали выполнение задачи '{name}'. Она займет {duration} минут.",
                                         reply_markup=kb.main_menu)
                    await state.set_state(fsm.menu)
                else:
                    # Проверяем достаточно ли выносливости у пользователя
                    cursor.execute('SELECT endurance FROM users WHERE user_id=?', (user_id,))
                    user_stamina = cursor.fetchone()[0]
                    if user_stamina < stamina_cost:
                        await message.answer("У вас недостаточно выносливости для выполнения этой задачи.")
                        conn.close()
                        return

                    # Обновляем выносливость пользователя
                    new_stamina = user_stamina - stamina_cost
                    cursor.execute('UPDATE users SET endurance=? WHERE user_id=?', (new_stamina, user_id))

                    # Добавляем задачу в user_tasks
                    end_time = datetime.now() + timedelta(minutes=duration)
                    cursor.execute('INSERT INTO user_tasks (user_id, task_id, end_time) VALUES (?, ?, ?)',
                                   (user_id, task_id, end_time))

                    conn.commit()
                    conn.close()

                    # Запускаем таймер выполнения задачи
                    asyncio.create_task(complete_task(user_id, task_id, end_time))

                    await message.answer(f"Вы начали выполнение задачи '{name}'. Она займет {duration} минут.",
                                         reply_markup=kb.main_menu)
                    await state.set_state(fsm.menu)
            else:
                await message.answer("Задача не найдена.", reply_markup=kb.main_menu)
                await state.set_state(fsm.menu)
        else:
            if message.text == '🔙 Домой':
                stats_message = return_home(message)
                await message.answer(f'root@HackerWars:/$\n\n{stats_message}', reply_markup=kb.main_menu)
                await state.set_state(fsm.menu)
            else:
                await message.answer("Задача не найдена или вам недоступна.", reply_markup=kb.main_menu)
                await state.set_state(fsm.menu)
    else:
        await message.answer("Ваш уровень не найден. Пожалуйста, зарегистрируйтесь в игре.", reply_markup=kb.main_menu)
        await state.set_state(fsm.menu)
        conn.close()


async def complete_task(user_id, task_id, end_time):
    await asyncio.sleep((end_time - datetime.now()).total_seconds())

    # Подключаемся к базе данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Получаем данные задачи
    cursor.execute('SELECT * FROM tasks WHERE id=?', (task_id,))
    task = cursor.fetchone()
    if task:
        _, name, description, level_required, stamina_cost, duration, reward_money, reward_experience, reward_artifact_chance = task

        if name == "🥱 Спать":
            # Извлекаем текущую выносливость и бонусы от артефактов
            cursor.execute('SELECT endurance FROM users WHERE user_id=?', (user_id,))
            user_stamina = cursor.fetchone()[0]
            artifacts = get_user_artifacts(user_id)
            max_stamina = calculate_stamina_with_artifacts(100, artifacts)

            # Обновляем выносливость пользователя
            new_stamina = min(user_stamina + 100, max_stamina)
            cursor.execute('UPDATE users SET endurance=?, status=? WHERE user_id=?', (new_stamina, 'active', user_id))

            conn.commit()
            conn.close()

            # Отправляем сообщение пользователю
            await bot.send_message(user_id,
                                   f"Вы завершили задачу '{name}'. Ваша выносливость восстановлена до {new_stamina}.")
        else:
            # Выдаём награду пользователю
            cursor.execute('UPDATE users SET money=money+?, experience=experience+? WHERE user_id=?',
                           (reward_money, reward_experience, user_id))

            # Удаляем задачу из user_tasks
            cursor.execute('DELETE FROM user_tasks WHERE user_id=?', (user_id,))

            conn.commit()
            conn.close()

            # Отправляем сообщение пользователю
            await bot.send_message(user_id,
                                   f"Вы завершили задачу '{name}'. Награда: {reward_money} денег, {reward_experience} опыта.")
    else:
        conn.close()


@dp.message(fsm.web)
async def web_handler(message: Message, state: FSMContext):
    await state.set_state(fsm.web)
    if message.text in ["🏪 Магазин", "🎪 Казино", "🔙 Домой"]:
        if message.text == "🏪 Магазин":
            await state.update_data(menu=message.text)
            await shop_command_handler(message, state)
        elif message.text == "🎪 Казино":
            await message.answer(f'Казино пока открыто только в Сочи, но скоро будет и здесь!')
            await state.set_state(fsm.web)
        elif message.text == '🔙 Домой':
            stats_message = return_home(message)
            await message.answer(f'root@HackerWars:/$\n\n{stats_message}', reply_markup=kb.main_menu)
            await state.set_state(fsm.menu)
    else:
        await message.answer(f'Хм, кажется, такого выбора тебе не давали, не забывай свои права...')
        await state.set_state(fsm.menu)


@dp.message(fsm.shop)
async def shop_command_handler(message: Message, state: FSMContext):
    """
    Обработчик команды /shop.
    Показывает пользователю список доступных артефактов для покупки.
    """
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # Получаем уровень пользователя
    cursor.execute('SELECT level FROM users WHERE user_id=?', (message.from_user.id,))
    user_level = cursor.fetchone()

    if not user_level:
        await message.answer("Вы еще не зарегистрированы в игре.")
        conn.close()
        return

    user_level = user_level[0]

    # Получаем артефакты, где req_lvl >= user_level
    cursor.execute('SELECT * FROM artifacts WHERE req_lvl <= ?', (user_level,))
    artifacts = cursor.fetchall()
    conn.close()

    if not artifacts:
        await message.answer("В магазине пока нет артефактов.")
        return

    buttons = []
    row = []
    art_msg = 'Доступные артефакты:\n\n'
    for art in artifacts:
        id, name, cost, attack, defense, camouflage, search, agility, endur, req_lvl = art
        art_msg += (f"{name}\n"
                    f"💰 {cost} монет\n"
                    f"💿 Требуемый уровень: {req_lvl}\n")
        if attack != 0:
            art_msg += f'⚔️ Атака: {attack}\n'
        if defense != 0:
            art_msg += f'🛡 Защита: {defense}\n'
        if camouflage != 0:
            art_msg += f'📺 Камуфляж: {camouflage}\n'
        if search != 0:
            art_msg += f'🔭 Поиск: {search}\n'
        if agility != 0:
            art_msg += f'💻 Ловкость: {agility}\n'
        if endur != 0:
            art_msg += f'🔋 Выносливость: {endur}\n'
        art_msg += '\n'
        row.append(KeyboardButton(text=name))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([KeyboardButton(text='🔙 Домой')])
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer(art_msg, reply_markup=keyboard)
    await state.set_state(fsm.buy)


@dp.message(fsm.broadcast)
async def broadcast_handler(message: Message, state: FSMContext) -> None:
    """
    Рассылает сообщение всем пользователям. Команда только для администраторов.
    Формат команды: /broadcast <message>
    """
    broadcast_message = message.text.partition(' ')[2]

    if not broadcast_message:
        await message.answer("Использование команды: /broadcast [message]")
        return

    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    conn.close()

    for user in users:
        user_id = user[0]
        try:
            await bot.send_message(user_id, broadcast_message)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

    await message.answer("Сообщение успешно разослано всем пользователям.")
    await state.set_state(fsm.menu)


@dp.message(fsm.add_art)
async def add_artifact_handler(message: Message, state: FSMContext) -> None:
    """
    Добавляет артефакт в базу данных. Команда только для администраторов.
    Формат команды: /add_artifact <name> <cost> <attack> <defense> <camouflage> <search> <agility> <endurance>
    """
    try:
        parts = message.text.split(maxsplit=9)
        name, cost, attack, defense, camouflage, search, agility, endurance, req_lvl = parts[1], int(parts[2]), int(
            parts[3]), int(parts[4]), int(parts[5]), int(parts[6]), int(parts[7]), int(parts[8]), int(parts[9])
    except (IndexError, ValueError):
        await message.answer(
            "Использование команды: /add_artifact [name] [cost] [attack] [defense] [camouflage] [search] [agility] [endurance] [req_lvl]")
        return

    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO artifacts (name, cost, attack, defense, camouflage, search, agility, endurance, req_lvl)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, cost, attack, defense, camouflage, search, agility, endurance, req_lvl))
    conn.commit()
    conn.close()

    await message.answer(f"Артефакт {name} успешно добавлен в магазин.")


@dp.message(fsm.buy)
async def buy_command_handler(message: Message, state: FSMContext):
    """
    Обработчик команды /buy.
    Позволяет пользователю купить артефакт по его ID или выполнить другое действие.
    """
    args = message.text
    if args == "🔙 Домой":
        stats_message = return_home(message)
        await message.answer(f'root@HackerWars:/$\n\n{stats_message}', reply_markup=kb.main_menu)
        await state.set_state(fsm.menu)
        return
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('SELECT level FROM users WHERE user_id=?', (message.from_user.id,))
    user_level = cursor.fetchone()

    cursor.execute('SELECT * FROM artifacts WHERE name = ? AND req_lvl <= ?', (args, user_level[0]))
    artifact = cursor.fetchone()
    if not artifact:
        await message.answer("Такого артифакта нет.")
        conn.close()
        return
    artifact_id = artifact[0]
    cursor.execute('SELECT * FROM user_artifacts WHERE user_id=? AND id=?',
                   (message.from_user.id, artifact_id))
    existing_artifact = cursor.fetchone()
    if existing_artifact:
        await message.answer("У вас уже есть этот артефакт.")
        conn.close()
        return

    # Получаем данные пользователя
    cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    user_data = cursor.fetchone()
    if not user_data:
        await message.answer("Вы еще не зарегистрированы в игре.")
        conn.close()
        return

    user_money = user_data[5]
    artifact_cost = artifact[2]

    if user_money < artifact_cost:
        await message.answer("У вас недостаточно монет для покупки этого артефакта.")
        conn.close()
        return

    # Обновляем баланс пользователя
    new_balance = user_money - artifact_cost
    cursor.execute('UPDATE users SET money=? WHERE user_id=?', (new_balance, message.from_user.id))

    # Добавляем артефакт пользователю
    cursor.execute('INSERT INTO user_artifacts (user_id, artifact_id) VALUES (?, ?)',
                   (message.from_user.id, artifact_id))

    conn.commit()
    conn.close()
    # Вызываем функцию обновления характеристик игрока
    update_player_stats(message.from_user.id, artifact_id)
    await message.answer(f"Вы успешно купили артефакт {artifact[1]} за {artifact_cost} монет.",
                         reply_markup=kb.main_menu)
    await state.set_state(fsm.menu)


def update_player_stats(user_id, artifact_id):
    """
    Обновляет характеристики пользователя после покупки артефакта.
    """
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # Получаем данные об артефакте
    cursor.execute('SELECT * FROM artifacts WHERE id = ?', (artifact_id,))
    artifact_data = cursor.fetchone()

    # Получаем текущие характеристики пользователя
    cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    user_data = cursor.fetchone()

    if not artifact_data or not user_data:
        # Если артефакт или пользователь не найдены, прекращаем выполнение функции
        conn.close()
        return

    # Рассчитываем новые характеристики пользователя на основе купленного артефакта
    new_attack = user_data[9] + artifact_data[3]
    new_defense = user_data[10] + artifact_data[4]
    new_camouflage = user_data[11] + artifact_data[5]
    new_search = user_data[12] + artifact_data[6]
    new_agility = user_data[13] + artifact_data[7]
    new_endurance = user_data[14] + artifact_data[8]

    # Обновляем данные пользователя в базе данных
    cursor.execute('''
        UPDATE users 
        SET 
            attack=?, 
            defense=?, 
            camouflage=?, 
            search=?, 
            agility=?, 
            endurance=?
        WHERE 
            user_id=?
    ''', (new_attack, new_defense, new_camouflage, new_search, new_agility, new_endurance, user_id))

    conn.commit()
    conn.close()


def return_home(message):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    user_data = cursor.fetchone()
    conn.close()

    # Отправляем пользователю его статистику
    stats_message = (
        f"👤 {hbold(user_data[4])} ({user_data[6]}):\n"
        f"💿 Уровень: {user_data[7]}\n"
        f"💡 Опыт: {user_data[8]}\n"
        f"💰 Деньги: {user_data[5]}\n"
        f"⚔️ Атака: {user_data[9]}\n"
        f"🛡 Защита: {user_data[10]}\n"
        f"📺 Камуфляж: {user_data[11]}\n"
        f"🔭 Поиск: {user_data[12]}\n"
        f"💻 Ловкость: {user_data[13]}\n"
        f"🔋 Выносливость: {user_data[14]}\n"
    )

    return stats_message


@dp.message()
async def echo_handler(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик для любых других сообщений, отправляет копию полученного сообщения.
    """
    try:
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            stats_message = return_home(message)
            await message.answer(f'root@HackerWars:/$\n\n{stats_message}', reply_markup=kb.main_menu)
            await state.set_state(fsm.menu)
            return
    except TypeError:
        await message.answer("Попробуйте еще раз!")
