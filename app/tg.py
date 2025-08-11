import os
from telegram import Bot

bot = Bot(os.getenv("TELEGRAM_TOKEN"))
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def post_photo(path:str, caption:str|None=None):
    with open(path, "rb") as f:
        bot.send_photo(chat_id=CHAT_ID, photo=f, caption=caption)
