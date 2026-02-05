import os
import time
import requests
from telegram import Bot

print("BOT STARTED")

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

bot = Bot(TOKEN)

bot.send_message(chat_id=CHAT_ID, text="🤖 Bot Live Foot IA démarré et connecté.")

def run():
    while True:
        time.sleep(60)

run()
