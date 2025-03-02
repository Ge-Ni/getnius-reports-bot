from aiogram.dispatcher.filters.state import State, StatesGroup

class Form(StatesGroup):
    description = State()
    website = State()
    category = State()
