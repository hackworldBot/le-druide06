import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_IDS = {
    int(user_id.strip())
    for user_id in os.getenv("ADMIN_IDS", "").split(",")
    if user_id.strip()
}


if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN n'est pas configuré dans .env")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL n'est pas configurée dans .env")
