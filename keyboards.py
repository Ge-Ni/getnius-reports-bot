from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import CATEGORIES

def get_categories_keyboard() -> ReplyKeyboardMarkup:
    """Create keyboard with category buttons"""
    keyboard = [[KeyboardButton(text=category)] for category in CATEGORIES]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_profile_keyboard() -> ReplyKeyboardMarkup:
    """Create keyboard for profile creation prompt"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать профиль")],
            [KeyboardButton(text="Позже")]
        ],
        resize_keyboard=True
    )
