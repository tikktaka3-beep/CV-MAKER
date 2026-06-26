"""
main.py
SLIDE BOT - Yangi admin va limit boshqaruvi
"""

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
ADMIN_ID = int(os.getenv("ADMIN_ID", "1691140865"))  # Sizning ID'ingiz
ADMIN_CONTACT = os.getenv("ADMIN_CONTACT", "@tikitaka1103")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ---------- FSM holatlari ----------
class Flow(StatesGroup):
    waiting_text = State()
    waiting_language = State()
    waiting_slide_count = State()
    waiting_style = State()
    waiting_notes = State()


# ---------- Klaviaturalar ----------
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
        [InlineKeyboardButton(text="🧑‍💼 Rasmiy", callback_data="style_rasmiy")],
        [InlineKeyboardButton(text="🌟 Zamonaviy", callback_data="style_zamonaviy")],
        [InlineKeyboardButton(text="🌈 Rangbarang", callback_data="style_rangbarang")],
        [InlineKeyboardButton(text="☀️ Och ranglar", callback_data="style_och")],
        [InlineKeyboardButton(text="🌑 To'q ranglar", callback_data="style_toq")],
        [InlineKeyboardButton(text="🏛️ Qadimiy", callback_data="style_qadimiy")],
        [InlineKeyboardButton(text="📖 Adabiy", callback_data="style_adabiy")],
        [InlineKeyboardButton(text="📐 Matematik", callback_data="style_matematik")],
        [InlineKeyboardButton(text="🧪 Kimyoviy", callback_data="style_kimyoviy")],
        [InlineKeyboardButton(text="⚛️ Fizik", callback_data="style_fizik")],
        [InlineKeyboardButton(text="🌌 Astronomik", callback_data="style_astronomik")],
        [InlineKeyboardButton(text="🏆 Sport", callback_data="style_sport")],
    ])

def kb_notes() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Yo'q, davom et", callback_data="notes_skip")],
    ])


# ---------- Buyruqlar ----------
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    db.ensure_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "👋 Salom! Men taqdimot tayyorlovchi botman.\n\n"
        "Mavzu yuboring — men chiroyli PPTX tayyorlayman.\n\n"
        "✍️ Mavzuni yozing:"
    )
    await state.set_state(Flow.waiting_text)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📌 Bot qanday ishlaydi:\n"
        "1. Mavzu yuborish\n"
        "2. Til tanlash\n"
        "3. Slayd soni\n"
        "4. Dizayn uslubi\n"
        "5. Qo'shimcha izoh\n\n"
        f"⚠️ Kuniga {db.DEFAULT_DAILY_LIMIT} ta bepul.\n"
        f"Admin: {ADMIN_CONTACT}"
    )


@dp.message(Command("mylimit"))
async def cmd_mylimit(message: Message):
    db.ensure_user(message.from_user.id, message.from_user.username)
    remaining = db.remaining_today(message.from_user.id)
    limit = db.get_limit(message.from_user.id)
    await message.answer(
        f"📊 Sizning limitingiz: {limit} ta\n"
        f"Bugun qolgan: {remaining} ta"
    )


# ---------- FAQAT ADMIN UCHUN ----------
@dp.message(Command("setlimit"))
async def cmd_setlimit(message: Message, command: CommandObject):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Bu buyruq faqat admin uchun!")
        return
    if not command.args:
        await message.answer("Foydalanish: /setlimit <user_id> <limit>")
        return
    try:
        parts = command.args.split()
        target_id = int(parts[0])
        new_limit = int(parts[1])
        db.set_limit(target_id, new_limit)
        await message.answer(f"✅ Foydalanuvchi {target_id} uchun limit {new_limit} ga o‘zgartirildi.")
        try:
            await bot.send_message(target_id, f"🎉 Admin sizga kunlik limitni {new_limit} taga oshirdi!")
        except:
            pass
    except:
        await message.answer("❌ Noto‘g‘ri format. Misol: /setlimit 123456789 10")


# ---------- Oddiy foydalanuvchilar uchun limit so'rash (ixtiyoriy) ----------
@dp.message(Command("requestlimit"))
async def request_limit(message: Message):
    await message.answer(
        f"Admin ({ADMIN_CONTACT}) ga yozing va limit so'rang.\n"
        f"Misol: 'Limit bersangiz, user_id: {message.from_user.id}'"
    )


# Qolgan kodlar (oldingi versiyadan)
@dp.message(Flow.waiting_text, F.text)
async def receive_text(message: Message, state: FSMContext):
    await state.update_data(source_text=message.text)
    await message.answer("🌐 Tilni tanlang:", reply_markup=kb_language())
    await state.set_state(Flow.waiting_language)


@dp.callback_query(Flow.waiting_language, F.data.startswith("lang_"))
async def choose_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(language=lang)
    await callback.message.edit_text("📑 Nechta slayd kerak?")
    await callback.message.answer("Slayd sonini tanlang:", reply_markup=kb_slide_count())
    await state.set_state(Flow.waiting_slide_count)
    await callback.answer()


@dp.callback_query(Flow.waiting_slide_count, F.data.startswith("count_"))
async def choose_count(callback: CallbackQuery, state: FSMContext):
    count = int(callback.data.split("_")[1])
    await state.update_data(slide_count=count)
    await callback.message.edit_text(f"✅ Slayd soni: {count}")
    await callback.message.answer("🎨 Dizayn uslubini tanlang:", reply_markup=kb_style())
    await state.set_state(Flow.waiting_style)
    await callback.answer()


@dp.callback_query(Flow.waiting_style, F.data.startswith("style_"))
async def choose_style(callback: CallbackQuery, state: FSMContext):
    style = callback.data.split("_")[1]
    await state.update_data(style=style)
    await callback.message.edit_text("📝 Qo'shimcha izoh bormi?")
    await callback.message.answer(
        "Izoh yozing yoki pastdagi tugmani bosing:",
        reply_markup=kb_notes(),
    )
    await state.set_state(Flow.waiting_notes)
    await callback.answer()


@dp.callback_query(Flow.waiting_notes, F.data == "notes_skip")
async def skip_notes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(extra_notes="")
    await callback.message.edit_text("⏳ Tayyorlanmoqda...")
    await generate_and_send(callback.from_user.id, callback.message, state)


@dp.message(Flow.waiting_notes, F.text)
async def receive_notes(message: Message, state: FSMContext):
    await state.update_data(extra_notes=message.text)
    status = await message.answer("⏳ Tayyorlanmoqda...")
    await generate_and_send(message.from_user.id, status, state)


async def generate_and_send(user_id: int, status_message: Message, state: FSMContext):
    db.ensure_user(user_id)
    if not db.can_generate(user_id):
        await status_message.answer(f"🚫 Limitingiz tugadi.\nAdmin: {ADMIN_CONTACT}")
        await state.clear()
        return

    data = await state.get_data()
    source_text = data.get("source_text", "")
    language = data.get("language", "uz")
    slide_count = data.get("slide_count", 6)
    style = data.get("style", "rasmiy")
    extra_notes = data.get("extra_notes", "")

    output_path = f"presentation_{user_id}.pptx"

    try:
        content = await asyncio.to_thread(
            generate_slides_content, source_text, language, slide_count, style, extra_notes
        )
        await asyncio.to_thread(create_presentation, content["slides"], output_path, style)

        await bot.send_document(
            chat_id=user_id,
            document=FSInputFile(output_path, filename="taqdimot.pptx"),
            caption=f"✅ Tayyor!\nDizayn: {style.capitalize()}",
        )
        db.increment_usage(user_id)
    except Exception as e:
        logger.exception("Xatolik")
        await bot.send_message(user_id, "❌ Xatolik yuz berdi. Qayta urinib ko‘ring.")
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)
        await state.clear()


@dp.message(F.text)
async def fallback(message: Message, state: FSMContext):
    if await state.get_state() is None:
        await state.update_data(source_text=message.text)
        await message.answer("🌐 Tilni tanlang:", reply_markup=kb_language())
        await state.set_state(Flow.waiting_language)


async def main():
    db.init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    
    
