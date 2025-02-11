import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables")

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("No OPENAI_API_KEY found in environment variables")

# Database configuration
DATABASE_NAME = "database.db"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Report categories
CATEGORIES = ["FinTech", "Automotive", "Retail", "Другие"]

# Report links
REPORT_LINKS = {
    "FinTech": "https://disk.yandex.com/d/TJtgoNkQ8aQfpw",
    "Automotive": "https://disk.yandex.com/d/O5FL51jLxs9vbg"
}

# Message templates
WELCOME_MESSAGE = "Добро пожаловать! Выберите сферу деятельности вашего бизнеса:"
PROFILE_PROMPT = "Вы регулярно получаете отчеты. Хотите персонализированные саммари?"
DESCRIPTION_PROMPT = "📝 Опишите ваш продукт (до 140 символов):"
WEBSITE_PROMPT = "🌍 Укажите ссылку на сайт вашего продукта:"

# OpenAI settings
SUMMARY_SYSTEM_PROMPT = """
You are a business analyst specializing in creating personalized report summaries.
Focus on aspects most relevant to the user's business profile and industry.
Keep summaries concise and actionable.
"""