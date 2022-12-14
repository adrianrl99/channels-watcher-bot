import os

from dotenv import load_dotenv

load_dotenv()

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_SESSION = os.environ.get("BOT_SESSION")
USER_SESSION = os.environ.get("USER_SESSION")
