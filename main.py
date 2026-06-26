import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

import database as db
from ai_generator import generate_slides_content
from slide_generator import create_presentation

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
VIP_ADMIN_ID = 1691140865 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Flow(StatesGroup):
    waiting_text, waiting_language, waiting_slide_count, waiting_style, waiting_notes = State(), State(), State(), State(), State()

def kb_style() -> InlineKeyboardMarkup:
    styles = [
        ("Rasmiy", "style_rasmiy"), ("Zamonaviy", "style_zamonaviy"),
        ("Rangbarang", "style_rangbarang"), ("Och", "style_och_ranglar"),
        ("To'q", "style_toq_ranglar"), ("Qadimiy", "style_qadimiy"),
        ("Adabiy", "style_adabiy"), ("Matematik", "style_matematik"),
        ("Kimyoviy", "style_kimyoviy"), ("Fizik", "style_fizik"),
        ("Astronomik", "style_astronomik"), ("Sport", "style_sport")
    ]
    buttons = [InlineKeyboardButton(text=n, callback_data=c) for n, c in styles]
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Salom! Mavzuni yozing:")
    await state.set_state(Flow.waiting_text)

@dp.message(Flow.waiting_text, F.text)
async def receive_text(message: Message, state: FSMContext):
    await state.update_data(source_text=message.text)
    await message.answer("Uslubni tanlang:", reply_markup=kb_style())
    await state.set_state(Flow.waiting_style)

@dp.callback_query(Flow.waiting_style, F.data.startswith("style_"))
async def choose_style(callback: CallbackQuery, state: FSMContext):
    await state.update_data(style=callback.data.split("_")[1])
    await generate_and_send(callback.from_user.id, callback.message, state)

async def generate_and_send(user_id: int, message: Message, state: FSMContext):
    data = await state.get_data()
    is_admin = (user_id == VIP_ADMIN_ID or user_id == ADMIN_ID)
    
    if not is_admin and not db.can_generate(user_id):
        await message.answer("Limit tugadi!")
        return

    await message.edit_text("⏳ Ishlayapman...")
    output_path = f"pres_{user_id}.pptx"
    
    try:
        content = await asyncio.to_thread(generate_slides_content, data['source_text'], "uz", 6, data['style'])
        await asyncio.to_thread(create_presentation, content["slides"], output_path, data['style'])
        await bot.send_document(user_id, FSInputFile(output_path))
        if not is_admin: db.increment_usage(user_id)
    except Exception as e:
        await message.answer(f"Xatolik: {e}")
    finally:
        if os.path.exists(output_path): os.remove(output_path)
        await state.clear()

async def main():
    db.init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
    
    
