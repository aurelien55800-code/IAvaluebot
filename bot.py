import os
import time
import requests
from telegram import Bot

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SPORTMONKS_KEY = os.environ.get("SPORTMONKS_KEY")
ODDS_API_KEY = os.environ.get("ODDS_API_KEY")

bot = Bot(TOKEN)

def get_live_matches():
    url = f"https://api.sportmonks.com/v3/football/livescores?api_token={SPORTMONKS_KEY}"
    try:
        return requests.get(url).json().get("data", [])
    except:
        return []

def classify(prob, odd):
    value = (prob * odd) - 1
    if prob >= 0.65 and value >= 0:
        return "🟢 SAFE", 0.03
    elif prob >= 0.50 and value >= 0.05:
        return "🟡 VALUE", 0.015
    elif value >= 0.15:
        return "🔴 AGRESSIF", 0.005
    return None, 0

def run():
    while True:
        matches = get_live_matches()
        for m in matches:
            name = m.get("name", "Match")
            minute = m.get("time", {}).get("minute", 0)

            prob = 0.55
            odd = 2.0

            label, stake = classify(prob, odd)
            if label:
                msg = f"⚽ {minute}' {name}\n{label}\nCote: {odd}\nMise: {int(stake*100)}%"
                bot.send_message(chat_id=CHAT_ID, text=msg)

        time.sleep(60)

run()
