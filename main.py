import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)

import database as db
from ai_generator import generate_slides_content
from slide_generator import create_presentation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_CONTACT = os.getenv("ADMIN_CONTACT", "@tikitaka1103")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Flow(StatesGroup):
    waiting_text = State()
    waiting_language = State()
    waiting_slide_count = State()
    waiting_style = State()
    waiting_notes = State()


def kb_language() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Rus", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 Ingliz", callback_data="lang_en")],
    ])

def kb_slide_count() -> InlineKeyboardMarkup:
    row = [InlineKeyboardButton(text=str(n), callback_data=f"count_{n}") for n in range(5, 9)]
    return InlineKeyboardMarkup(inline_keyboard=[row])

def kb_style() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😄 Quvnoq & Rangli", callback_data="style_quvnoq")],
        [InlineKeyboardButton(text="✏️ Sodda (Simple)", callback_data="style_simple")],
        [InlineKeyboardButton(text="🧑‍💼 Rasmiy", callback_data="style_rasmiy")],
    ])

def kb_notes() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Yo'q, davom et", callback_data="notes_skip")],
    ])


@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    db.ensure_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "👋 Salom! Men AI yordamida **rasmli va quvnoq** taqdimotlar tayyorlovchi botman.\n\n"
        "Menga mavzu yoki matn yuboring — men sizga zo'r dizayndagi PowerPoint tayyorlab beraman.\n\n"
        "✍️ Mavzuni yozing:"
    )
    await state.set_state(Flow.waiting_text)

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📌 Qanday ishlaydi:\n"
        "1. Mavzu/matn yuborasiz\n"
        "2. Til, Slayd soni va Uslubni tanlaysiz\n"
        "3. AI har bir slayd uchun matn va mos rasmlarni avtomatik topib joylashtiradi!\n\n"
        f"⚠️ Kuniga bepul {db.DEFAULT_DAILY_LIMIT} ta.\nLimitni oshirish uchun: {ADMIN_CONTACT}\n\n"
        "/start - yangi taqdimot"
    )

@dp.message(Command("mylimit"))
async def cmd_mylimit(message: Message):
    db.ensure_user(message.from_user.id, message.from_user.username)
    remaining = db.remaining_today(message.from_user.id)
    limit = db.get_limit(message.from_user.id)
    await message.answer(f"📊 Kunlik limit: {limit}\nBugun qolgan: {remaining}\nBog'lanish: {ADMIN_CONTACT}")

@dp.message(Command("setlimit"))
async def cmd_setlimit(message: Message, command: CommandObject):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = command.args.split()
        target_id, new_limit = int(parts[0]), int(parts[1])
        db.set_limit(target_id, new_limit)
        await message.answer(f"✅ User {target_id} ga {new_limit} limit berildi.")
    except:
        await message.answer("Xato. /setlimit <id> <limit>")

@dp.message(Flow.waiting_text, F.text)
async def receive_text(message: Message, state: FSMContext):
    await state.update_data(source_text=message.text)
    await message.answer("🌐 Taqdimot qaysi tilda bo'lsin?", reply_markup=kb_language())
    await state.set_state(Flow.waiting_language)

@dp.callback_query(Flow.waiting_language, F.data.startswith("lang_"))
async def choose_language(callback: CallbackQuery, state: FSMContext):
    await state.update_data(language=callback.data.split("_")[1])
    await callback.message.edit_text("📑 Nechta slayd kerak?")
    await callback.message.answer("Slayd sonini tanlang:", reply_markup=kb_slide_count())
    await state.set_state(Flow.waiting_slide_count)

@dp.callback_query(Flow.waiting_slide_count, F.data.startswith("count_"))
async def choose_count(callback: CallbackQuery, state: FSMContext):
    await state.update_data(slide_count=int(callback.data.split("_")[1]))
    await callback.message.edit_text("🎨 Dizayn uslubini tanlang:")
    await callback.message.answer("Uslub:", reply_markup=kb_style())
    await state.set_state(Flow.waiting_style)

@dp.callback_query(Flow.waiting_style, F.data.startswith("style_"))
async def choose_style(callback: CallbackQuery, state: FSMContext):
    await state.update_data(style=callback.data.split("_")[1])
    await callback.message.edit_text("📝 Qo'shimcha izoh bormi?")
    await callback.message.answer("Masalan: 'Ko'proq rasm bo'lsin' yoki pastdagi tugmani bosing:", reply_markup=kb_notes())
    await state.set_state(Flow.waiting_notes)

@dp.callback_query(Flow.waiting_notes, F.data == "notes_skip")
async def skip_notes(callback: CallbackQuery, state: FSMContext):
    await state.update_data(extra_notes="")
    await callback.message.edit_text("⏳ AI matn yozib, avtomatik rasmlar qidirmoqda... Bu 1-2 daqiqa vaqt olishi mumkin. Iltimos kuting 🚀")
    user_id = callback.from_user.id
    await generate_and_send(user_id, callback.message, state)

@dp.message(Flow.waiting_notes, F.text)
async def receive_notes(message: Message, state: FSMContext):
    await state.update_data(extra_notes=message.text)
    status = await message.answer("⏳ AI matn yozib, avtomatik rasmlar qidirmoqda... Bu 1-2 daqiqa vaqt olishi mumkin. Iltimos kuting 🚀")
    await generate_and_send(message.from_user.id, status, state)

async def generate_and_send(user_id: int, status_message: Message, state: FSMContext):
    db.ensure_user(user_id)
    if not db.can_generate(user_id):
        await status_message.answer(f"🚫 Bugungi limit tugadi. Admin: {ADMIN_CONTACT}")
        await state.clear()
        return

    data = await state.get_data()
    output_path = f"taqdimot_{user_id}.pptx"

    try:
        content = await asyncio.to_thread(
            generate_slides_content, data.get("source_text"), data.get("language"), 
            data.get("slide_count"), data.get("style"), data.get("extra_notes")
        )
        await asyncio.to_thread(create_presentation, content["slides"], output_path)

        await bot.send_document(
            chat_id=user_id,
            document=FSInputFile(output_path, filename="Super_Taqdimot.pptx"),
            caption="🎉 Taqdimotingiz tayyor!\nAvtomatik AI rasmlari va quvnoq dizayn bilan maxsus siz uchun yaratildi.",
        )
        db.increment_usage(user_id)

    except Exception as e:
        logger.exception("Xatolik:")
        await bot.send_message(user_id, "❌ Taqdimot yaratishda xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")
    finally:
        if os.path.exists(output_path): os.remove(output_path)
        await state.clear()

@dp.message(F.text)
async def fallback(message: Message, state: FSMContext):
    current = await state.get_state()
    if current is None:
        await state.update_data(source_text=message.text)
        await message.answer("🌐 Taqdimot qaysi tilda bo'lsin?", reply_markup=kb_language())
        await state.set_state(Flow.waiting_language)

async def main():
    db.init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
