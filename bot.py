# bot.py
import asyncio
from datetime import datetime, timedelta
import json
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold
from aiogram.types import ReplyKeyboardRemove
import app.keyboards as kb
from aiogram import F


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


def create_artifacts_table():
    """
    Создает таблицу 'artifacts' в базе данных, если ее нет.
    Поля таблицы включают информацию об артефактах.
    """
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artifacts (
            id INTEGER PRIMARY KEY,
            name TEXT,
            cost INTEGER,
            attack INTEGER,
            defense INTEGER,
            camouflage INTEGER,
            search INTEGER,
            agility INTEGER,
            endurance INTEGER,
            req_lvl INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def create_user_artifacts_table():
    """
    Создает таблицу 'user_artifacts' в базе данных, если ее нет.
    Поля таблицы включают информацию о купленных артефактах пользователей.
    """
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_artifacts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            artifact_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(artifact_id) REFERENCES artifacts(id)
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
    create_users_table()
    create_artifacts_table()
    create_user_artifacts_table()

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
    elif message.text.split(' ')[0] == '/add_artifact' and message.from_user.id == 808305848:
        await state.update_data(menu=message.text)
        await add_artifact_handler(message, state)
    else:
        await message.answer(f'Хм, кажется, такого выбора тебе не давали, не забывай свои права...')
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

                await message.answer(f"Вы начали выполнение задачи '{name}'. Она займет {duration} минут.")
            else:
                await message.answer("Задача не найдена.")
        else:
            if message.text == '🔙 Домой':
                stats_message = return_home(message)
                await message.answer(f'root@HackerWars:/$\n\n{stats_message}', reply_markup=kb.main_menu)
                await state.set_state(fsm.menu)
            else:
                await message.answer("Задача не найдена или вам недоступна.")
    else:
        await message.answer("Ваш уровень не найден. Пожалуйста, зарегистрируйтесь в игре.")
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
    encod = {
        "attack": "⚔️ Атака",
        "defense": "🛡 Защита",
        "camouflage": "📺 Камуфляж",
        "search": "🔭 Поиск",
        "agility": "💻 Ловкость",
        "endurance": "🔋 Выносливость"
    }

    if not artifacts:
        await message.answer("В магазине пока нет артефактов.")
        return

    shop_message = "Доступные артефакты (Для покупки введите номер):\n\n"
    for artifact in artifacts:
        art_id, art_name, art_cost, art_attack, art_defense, art_camouflage, art_search, art_agility, art_endurance, art_req_lvl = artifact

        artifact_info = f"{art_id} {art_name}\nСтоимость: {art_cost} монет\n"

        # Добавляем характеристики, которые не равны нулю
        if art_attack != 0:
            artifact_info += f"{encod['attack']}: {art_attack}\n"
        if art_defense != 0:
            artifact_info += f"{encod['defense']}: {art_defense}\n"
        if art_camouflage != 0:
            artifact_info += f"{encod['camouflage']}: {art_camouflage}\n"
        if art_search != 0:
            artifact_info += f"{encod['search']}: {art_search}\n"
        if art_agility != 0:
            artifact_info += f"{encod['agility']}: {art_agility}\n"
        if art_endurance != 0:
            artifact_info += f"{encod['endurance']}: {art_endurance}\n"

        artifact_info += "\n"  # Добавляем пустую строку для разделения артефактов
        shop_message += artifact_info
    await message.answer(shop_message)
    await state.set_state(fsm.buy)


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
    create_user_artifacts_table()

    # Проверяем, является ли введенный текст числом (ID артефакта) или нет
    try:
        artifact_id = int(args)
    except ValueError:
        # Если текст не является числом, обрабатываем его как другое действие
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
            await message.answer("ID артефакта должен быть числом. Пример: 1")
        return

    # Если текст является числом, обрабатываем его как ID артефакта и выполняем покупку артефакта
    # Остальной код остается без изменений
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('SELECT level FROM users WHERE user_id=?', (message.from_user.id,))
    user_level = cursor.fetchone()
    cursor.execute('SELECT * FROM artifacts WHERE id = ? AND req_lvl <= ?', (artifact_id, user_level[0]))
    artifact = cursor.fetchone()
    if not artifact:
        await message.answer("Артефакт с таким ID не найден.")
        conn.close()
        return

    cursor.execute('SELECT * FROM user_artifacts WHERE user_id=? AND artifact_id=?',
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
