import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from typing import Optional

from config import (
    BOT_TOKEN, WELCOME_MESSAGE, PROFILE_PROMPT, 
    DESCRIPTION_PROMPT, WEBSITE_PROMPT, REPORT_LINKS
)
from database import init_db, add_user, get_reports, get_all_users, get_user
from keyboards import get_categories_keyboard, get_profile_keyboard
from states import Form
from summarizer import generate_personalized_summary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    """Handle /start command"""
    try:
        await message.answer(
            WELCOME_MESSAGE,
            reply_markup=get_categories_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

async def send_report_with_summary(
    chat_id: int,
    title: str,
    source: str,
    category: str,
    file_path: str,
    user_data: Optional[tuple] = None
):
    """Send report with personalized summary if user profile exists"""
    try:
        base_text = f"📄 **{title}**\nИсточник: {source}"

        # Add file link based on category
        if category in REPORT_LINKS:
            file_info = f"\n[Открыть файл]({REPORT_LINKS[category]})"
        else:
            file_info = f"\nФайл: {file_path}"

        # Generate summary if user profile exists and has required data
        if isinstance(user_data, tuple) and len(user_data) >= 3:
            _, _, description, _, _ = user_data
            summary = await generate_personalized_summary(
                report_text=f"{title}\n{source}",  # You might want to load actual report text here
                user_description=description,
                industry=category
            )
            if summary:
                base_text += f"\n\n💡 Персональный анализ:\n{summary}"

        await bot.send_message(
            chat_id=chat_id,
            text=base_text + file_info,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error sending report with summary: {e}")
        await bot.send_message(
            chat_id=chat_id,
            text="Произошла ошибка при отправке отчета. Попробуйте позже."
        )

@router.message(lambda message: message.text in ["FinTech", "Automotive", "Retail", "Другие"])
async def get_category(message: types.Message, state: FSMContext):
    """Handle category selection"""
    try:
        category = message.text
        await state.update_data(category=category)
        await message.answer(
            f"Вы выбрали категорию: {category}\nОтправляем отчеты...",
            reply_markup=ReplyKeyboardRemove()
        )

        reports = get_reports(category)
        user_data = get_user(message.from_user.id)

        if reports:
            for report in reports:
                title, source, file_path = report
                await send_report_with_summary(
                    chat_id=message.from_user.id,
                    title=title,
                    source=source,
                    category=category,
                    file_path=file_path,
                    user_data=user_data
                )
        else:
            await message.answer("Пока нет отчетов для этой категории.")

        await asyncio.sleep(3)
        await message.answer(PROFILE_PROMPT, reply_markup=get_profile_keyboard())
    except Exception as e:
        logger.error(f"Error in category selection: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

@router.message(lambda message: message.text == "Позже")
async def handle_later(message: types.Message, state: FSMContext):
    """Handle 'Later' button press"""
    await state.clear()
    await message.answer(
        "Хорошо, вы можете создать профиль позже через команду /create_profile",
        reply_markup=get_categories_keyboard()
    )

@router.message(lambda message: message.text == "Создать профиль")
async def create_profile(message: types.Message, state: FSMContext):
    """Handle profile creation"""
    await message.answer(DESCRIPTION_PROMPT, reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.description)

@router.message(Form.description)
async def get_description(message: types.Message, state: FSMContext):
    """Handle product description"""
    if len(message.text) > 140:
        await message.answer("Описание слишком длинное. Пожалуйста, уложитесь в 140 символов.")
        return
    
    await state.update_data(description=message.text)
    await message.answer(WEBSITE_PROMPT)
    await state.set_state(Form.website)

@router.message(Form.website)
async def get_website(message: types.Message, state: FSMContext):
    """Handle website URL"""
    if not message.text.startswith(("http://", "https://")):
        await message.answer("Пожалуйста, введите корректный URL, начинающийся с http:// или https://")
        return

    try:
        user_data = await state.get_data()
        if add_user(
            message.from_user.id,
            user_data["category"],
            user_data["description"],
            message.text
        ):
            await message.answer(
                "✅ Спасибо! Ваш профиль успешно создан. "
                "Теперь отчеты будут содержать персонализированные саммари для вашего бизнеса."
            )
            await message.answer(
                "Выберите сферу деятельности вашего бизнеса:",
                reply_markup=get_categories_keyboard()
            )
        else:
            raise Exception("Failed to save user profile")
    except Exception as e:
        logger.error(f"Error saving profile: {e}")
        await message.answer("Произошла ошибка при сохранении профиля. Попробуйте позже.")
    finally:
        await state.clear()

@router.message(Command("users"))
async def show_users(message: types.Message):
    """Handle /users command"""
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

async def send_regular_reports():
    """Send daily reports to users"""
    while True:
        try:
            await asyncio.sleep(86400)  # 24 hours
            users = get_all_users()
            for user in users:
                user_id, category, description, website, _ = user
                reports = get_reports(category)
                if reports:
                    for report in reports:
                        title, source, file_path = report
                        await send_report_with_summary(
                            chat_id=user_id,
                            title=title,
                            source=source,
                            category=category,
                            file_path=file_path,
                            user_data=user
                        )
        except Exception as e:
            logger.error(f"Error in regular reports: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes before retrying

async def main():
    """Main function to start the bot"""
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")

        # Include router and start bot
        dp.include_router(router)
        await bot.delete_webhook(drop_pending_updates=True)
        asyncio.create_task(send_regular_reports())

        logger.info("Bot started successfully")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        raise  # Re-raise to ensure the error is visible in logs

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually")
    except Exception as e:
        logger.error(f"Critical error: {e}")