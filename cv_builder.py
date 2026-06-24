from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from states import CVBuilder
from keyboards.reply import main_menu_keyboard

router = Router()

@router.message(lambda m: m.text == "📄 CV yaratish")
async def start_cv(message: types.Message, state: FSMContext):
    await state.set_state(CVBuilder.full_name)
    await message.answer("Ismingizni kiriting:")