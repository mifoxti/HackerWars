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
        InlineKeyboardButton(text="Конечено")
    ]
])