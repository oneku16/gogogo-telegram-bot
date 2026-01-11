import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN env variable is not set")
