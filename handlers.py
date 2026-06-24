from aiogram import Router, types
from aiogram.filters import CommandStart
from keyboards.reply import language_keyboard
from database import get_session
from models import User
from sqlalchemy import select

router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("🇺🇿 O'zbek\n🇷🇺 Русский", reply_markup=language_keyboard())