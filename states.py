from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    category = State()
    description = State()
    website = State()
