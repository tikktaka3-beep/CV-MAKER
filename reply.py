from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbek"), KeyboardButton(text="🇷🇺 Русский")]
        ],
        resize_keyboard=True
    )

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📄 CV yaratish")],
            [KeyboardButton(text="📂 Mening CVlarim")],
            [KeyboardButton(text="ℹ️ Yordam")],
            [KeyboardButton(text="👑 Admin Panel")]
        ],
        resize_keyboard=True
    )