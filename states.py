from aiogram.fsm.state import StatesGroup, State

class CVBuilder(StatesGroup):
    full_name = State()
    position = State()
    birth_date = State()
    phone = State()
    email = State()
    address = State()
    education = State()
    experience = State()
    skills = State()
    languages = State()
    certificates = State()
    additional_info = State()
    photo = State()
    template = State()
    preview = State()