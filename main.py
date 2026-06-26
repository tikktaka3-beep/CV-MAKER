"""
main.py
SLIDE BOT - matn asosida taqdimot (.pptx) yaratuvchi Telegram bot.
Yangi ko'p theme (dizayn) qo'llab-quvvatlanadi.
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
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
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


# ---------- Inline klaviaturalar ----------
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


# ---------- /start ----------
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    db.ensure_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "👋 Salom! Men taqdimot (slayd) tayyorlovchi botman.\n\n"
        "Menga mavzu yoki matn yuboring — men chiroyli "
        "PowerPoint taqdimotini tayyorlab beraman.\n\n"
        "✍️ Mavzuni yoki matnni yuboring:"
    )
    await state.set_state(Flow.waiting_text)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📌 Qanday ishlaydi:\n"
        "1. Mavzu yoki matn yuboring\n"
        "2. Tilni tanlang (uz/ru/en)\n"
        "3. Slayd sonini tanlang (5-8)\n"
        "4. Dizayn uslubini tanlang\n"
        "5. Qo'shimcha izoh (ixtiyoriy)\n\n"
        f"⚠️ Kuniga bepul {db.DEFAULT_DAILY_LIMIT} ta taqdimot yaratish mumkin.\n"
        f"Limitni oshirish uchun: {ADMIN_CONTACT}\n\n"
        "/start - yangi taqdimot boshlash\n"
        "/mylimit - bugungi limitingizni ko'rish"
    )


@dp.message(Command("mylimit"))
async def cmd_mylimit(message: Message):
    db.ensure_user(message.from_user.id, message.from_user.username)
    remaining = db.remaining_today(message.from_user.id)
    limit = db.get_limit(message.from_user.id)
    await message.answer(
        f"📊 Kunlik limitingiz: {limit} ta\n"
        f"Bugun qolgan: {remaining} ta\n\n"
        f"Limitni oshirish uchun: {ADMIN_CONTACT}"
    )


# ---------- Admin: limitni o'zgartirish ----------
@dp.message(Command("setlimit"))
async def cmd_setlimit(message: Message, command: CommandObject):
    if message.from_user.id != ADMIN_ID:
        return
    if not command.args:
        await message.answer("Foydalanish: /setlimit <user_id> <limit>")
        return
    try:
        parts = command.args.split()
        target_id = int(parts[0])
        new_limit = int(parts[1])
    except (ValueError, IndexError):
        await message.answer("Foydalanish: /setlimit <user_id> <limit>")
        return

    db.set_limit(target_id, new_limit)
    await message.answer(f"✅ Foydalanuvchi {target_id} uchun kunlik limit {new_limit} ga o'zgartirildi.")
    try:
        await bot.send_message(target_id, f"🎉 Sizning kunlik limitingiz {new_limit} taga oshirildi!")
    except Exception:
        pass


# ---------- 1. Matn qabul qilish ----------
@dp.message(Flow.waiting_text, F.text)
async def receive_text(message: Message, state: FSMContext):
    await state.update_data(source_text=message.text)
    await message.answer(
        "🌐 Taqdimot qaysi tilda bo'lsin?",
        reply_markup=kb_language(),
    )
    await state.set_state(Flow.waiting_language)


# ---------- 2. Til tanlash ----------
@dp.callback_query(Flow.waiting_language, F.data.startswith("lang_"))
async def choose_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(language=lang)
    await callback.message.edit_text("📑 Nechta slayd kerak?")
    await callback.message.answer("Slayd sonini tanlang:", reply_markup=kb_slide_count())
    await state.set_state(Flow.waiting_slide_count)
    await callback.answer()


# ---------- 3. Slayd soni ----------
@dp.callback_query(Flow.waiting_slide_count, F.data.startswith("count_"))
async def choose_count(callback: CallbackQuery, state: FSMContext):
    count = int(callback.data.split("_")[1])
    await state.update_data(slide_count=count)
    await callback.message.edit_text(f"✅ Slayd soni: {count}")
    await callback.message.answer("🎨 Taqdimot dizayn uslubini tanlang:", reply_markup=kb_style())
    await state.set_state(Flow.waiting_style)
    await callback.answer()


# ---------- 4. Uslub / Theme ----------
@dp.callback_query(Flow.waiting_style, F.data.startswith("style_"))
async def choose_style(callback: CallbackQuery, state: FSMContext):
    style = callback.data.split("_")[1]
    await state.update_data(style=style)
    await callback.message.edit_text("📝 Qo'shimcha izoh yoki talab bormi?")
    await callback.message.answer(
        "Agar bo'lsa yozing (masalan: 'statistik raqamlar qo'shilsin', 'rasmlar bo'lsin'), "
        "yo'q bo'lsa pastdagi tugmani bosing:",
        reply_markup=kb_notes(),
    )
    await state.set_state(Flow.waiting_notes)
    await callback.answer()


# ---------- 5a. Izohni o'tkazib yuborish ----------
@dp.callback_query(Flow.waiting_notes, F.data == "notes_skip")
async def skip_notes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(extra_notes="")
    await callback.message.edit_text("⏳ Tayyorlanmoqda...")
    await generate_and_send(callback.from_user.id, callback.message, state)


# ---------- 5b. Izohni matn sifatida qabul qilish ----------
@dp.message(Flow.waiting_notes, F.text)
async def receive_notes(message: Message, state: FSMContext):
    await state.update_data(extra_notes=message.text)
    status = await message.answer("⏳ Tayyorlanmoqda, biroz kuting...")
    await generate_and_send(message.from_user.id, status, state)


# ---------- Generatsiya va yuborish ----------
async def generate_and_send(user_id: int, status_message: Message, state: FSMContext):
    db.ensure_user(user_id)

    if not db.can_generate(user_id):
        await status_message.answer(
            "🚫 Bugungi bepul limitingiz tugadi.\n"
            f"Limitni oshirish uchun admin bilan bog'laning: {ADMIN_CONTACT}"
        )
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
        
        # Yangi theme bilan yaratish
        await asyncio.to_thread(
            create_presentation, content["slides"], output_path, style
        )

        await bot.send_document(
            chat_id=user_id,
            document=FSInputFile(output_path, filename="taqdimot.pptx"),
            caption="✅ Taqdimotingiz tayyor!\n"
                    f"Dizayn: {style.capitalize()}",
        )
        db.increment_usage(user_id)

        remaining = db.remaining_today(user_id)
        if remaining <= 0:
            await bot.send_message(
                user_id,
                f"ℹ️ Bugungi limitingiz tugadi. Yana yaratish uchun: {ADMIN_CONTACT}",
            )

    except Exception as e:
        logger.exception("Taqdimot yaratishda xatolik")
        await bot.send_message(
            user_id,
            "❌ Taqdimot yaratishda xatolik yuz berdi. Birozdan keyin qaytadan urinib ko'ring.",
        )
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)
        await state.clear()


# ---------- Holatdan tashqari matn ----------
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
    
    
    
