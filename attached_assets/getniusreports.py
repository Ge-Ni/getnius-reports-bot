import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")  # Get token from environment variables
if not TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables")

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# Создание клавиатуры для выбора категории
categories = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="FinTech")],
        [KeyboardButton(text="Automotive")],
        [KeyboardButton(text="Retail")],
        [KeyboardButton(text="Другие")]
    ],
    resize_keyboard=True
)

# Определение состояний
class Form(StatesGroup):
    category = State()
    description = State()
    website = State()

# Функция для получения отчётов по категории
def get_reports(category):
    """Получает отчёты по категории из базы данных"""
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title, source, file_path FROM reports WHERE category=?", (category,))
    reports = cursor.fetchall()
    conn.close()
    return reports

# Обработчик команды /start
@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Добро пожаловать! Выберите сферу деятельности вашего бизнеса:", reply_markup=categories)

# Обработчик выбора категории
@router.message(lambda message: message.text in ["FinTech", "Automotive", "Retail", "Другие"])
async def get_category(message: types.Message, state: FSMContext):
    category = message.text
    await state.update_data(category=category)
    await message.answer(f"Вы выбрали категорию: {category}\nОтправляем отчеты...",
                         reply_markup=types.ReplyKeyboardRemove())  # Убираем клавиатуру

    # Получаем отчёты из базы данных
    reports = get_reports(category)
    if reports:
        for report in reports:
            title, source, file_path = report
            if category == "FinTech":
                # Для категории FinTech отправляем ссылку на файл
                await message.answer(f"📄 **{title}**\nИсточник: {source}\n[Открыть файл](https://disk.yandex.com/d/TJtgoNkQ8aQfpw)", parse_mode="Markdown")
            elif category == "Automotive":
                # Для категории Automotive отправляем ссылку на файл
                await message.answer(f"📄 **{title}**\nИсточник: {source}\n[Открыть файл](https://disk.yandex.com/d/O5FL51jLxs9vbg)", parse_mode="Markdown")
            else:
                await message.answer(f"📄 **{title}**\nИсточник: {source}\nФайл: {file_path}")
    else:
        await message.answer("Пока нет отчетов для этой категории.")

    # Предложение создать профиль через 3 секунды (для теста)
    await asyncio.sleep(3)
    await message.answer(
        "Вы регулярно получаете отчеты. Хотите персонализированные саммари?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Создать профиль")],
                [KeyboardButton(text="Позже")]
            ],
            resize_keyboard=True
        )
    )

# Обработчик кнопки "Позже"
@router.message(lambda message: message.text == "Позже")
async def handle_later(message: types.Message, state: FSMContext):
    await state.clear()  # Сбрасываем состояние
    await message.answer("Хорошо, вы можете создать профиль позже через команду /create_profile",
                         reply_markup=categories)  # Возвращаем основное меню

# Обработчик создания профиля
@router.message(lambda message: message.text == "Создать профиль")
async def create_profile(message: types.Message, state: FSMContext):
    await message.answer("📝 Опишите ваш продукт (до 140 символов):",
                         reply_markup=types.ReplyKeyboardRemove())  # Убираем кнопки
    await state.set_state(Form.description)

# Обработчик получения описания продукта
@router.message(Form.description, lambda message: len(message.text) <= 140)
async def get_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("🌍 Укажите ссылку на сайт вашего продукта:")
    await state.set_state(Form.website)

# Обработчик получения ссылки на сайт
@router.message(Form.website, lambda message: message.text.startswith("http"))
async def get_website(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    category = user_data.get("category")
    description = user_data.get("description")
    website = message.text

    # Сохраняем пользователя в базу данных
    add_user(message.from_user.id, category, description, website)

    await message.answer(
        "✅ Спасибо! Ваш профиль успешно создан. Теперь отчеты будут содержать персонализированные саммари для вашего бизнеса.")
    await state.clear()

    # Возвращаем пользователя в главное меню
    await message.answer("Выберите сферу деятельности вашего бизнеса:", reply_markup=categories)

# Обработчик команды /users (просмотр зарегистрированных пользователей)
@router.message(Command("users"))
async def show_users(message: types.Message):
    # Получаем всех пользователей
    users = get_all_users()

    if users:
        response = "Список зарегистрированных пользователей:\n\n"
        for user in users:
            user_id, category, description, website, created_at = user
            response += (
                f"👤 ID: {user_id}\n"
                f"📂 Категория: {category}\n"
                f"📝 Описание: {description}\n"
                f"🌍 Сайт: {website}\n"
                f"🕒 Дата регистрации: {created_at}\n\n"
            )
        await message.answer(response)
    else:
        await message.answer("Пока нет зарегистрированных пользователей.")

# Регулярная отправка отчётов
async def send_regular_reports():
    while True:
        await asyncio.sleep(86400)  # Раз в сутки
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        for user in users:
            user_id, category, _, _, _ = user
            reports = get_reports(category)
            if reports:
                for report in reports:
                    title, source, file_path = report
                    if category == "FinTech":
                        # Для категории FinTech отправляем ссылку на файл
                        await bot.send_message(chat_id=user_id, text=f"📄 **{title}**\nИсточник: {source}\n[Открыть файл](https://disk.yandex.com/d/TJtgoNkQ8aQfpw)", parse_mode="Markdown")
                    elif category == "Automotive":
                        # Для категории Automotive отправляем ссылку на файл
                        await bot.send_message(chat_id=user_id, text=f"📄 **{title}**\nИсточник: {source}\n[Открыть файл](https://disk.yandex.com/d/O5FL51jLxs9vbg)", parse_mode="Markdown")
                    else:
                        await bot.send_message(chat_id=user_id, text=f"📄 **{title}**\nИсточник: {source}\nФайл: {file_path}")
        conn.close()

async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(send_regular_reports())  # Запуск регулярной отправки отчётов
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен вручную.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def add_user(user_id, category, description, website):
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute("INSERT INTO users (user_id, category, description, website, created_at) VALUES (?, ?, ?, ?, ?)",
                   (user_id, category, description, website, timestamp))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users