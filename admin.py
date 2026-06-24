from aiogram import Router, types
from config import settings

router = Router()

@router.message(lambda m: m.text == "👑 Admin Panel")
async def admin_panel(message: types.Message):
    if message.from_user.id != settings.ADMIN_ID:
        return await message.answer("Access denied.")
    await message.answer("👑 Admin Panel\n👥 Total users\n📄 Total CVs\n📊 Statistics\n📢 Broadcast message\n📋 Recent users")