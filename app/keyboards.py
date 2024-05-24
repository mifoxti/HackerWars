from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

main = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="🎭 Phantoms"), KeyboardButton(text="☮️ Liberty")
    ],
    [
        KeyboardButton(text="💠 Aegis"), KeyboardButton(text="🗿 NotFounds")
    ]
])

start = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Конечно", callback_data="reg")
    ]
])

main_menu = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='👤 Профиль')
    ],
    [
        KeyboardButton(text='🌐 Сеть'), KeyboardButton(text='🗡 Битва'), KeyboardButton(text='⌛️ Дела')
    ],
    [
        KeyboardButton(text='⚙️ Настройки')
    ]
])

web_menu = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='🏪 Магазин'), KeyboardButton(text='🎪 Казино')
    ],
    [
        KeyboardButton(text='🏆 Топ лучших')
    ],
    [
        KeyboardButton(text='🔙 Домой')
    ]
])

fight_menu = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='🔪 Напасть')
    ],
    [
        KeyboardButton(text='🔙 Домой')
    ]
])

settings_menu = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='🔑 Ввести код')
    ],
    [
        KeyboardButton(text='🔙 Домой')
    ]
])
