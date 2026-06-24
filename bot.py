import logging
import asyncio
from aiogram import Bot, Dispatcher   # ✅ To‘g‘ri import
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from config import settings
from handlers import start, cv_builder, admin

logging.basicConfig(level=logging.INFO)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start bot"),
        BotCommand(command="help", description="Help"),
    ]
    await bot.set_my_commands(commands)

async def main():
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(cv_builder.router)
    dp.include_router(admin.router)

    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
