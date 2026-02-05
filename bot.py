import os
import asyncio
import requests
from telegram import Bot
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)

ALLOWED_LEAGUES = [
    "Premier League",
    "La Liga",
    "Serie A",
    "Bundesliga",
    "Ligue 1",
    "UEFA Champions League",
    "UEFA Europa League",
    "Eredivisie",
    "Primeira Liga",
    "Jupiler Pro League"
]

last_sent = {}

def get_games():
    url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "totals,btts,h2h",
        "oddsFormat": "decimal"
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return []
    return r.json()

def classify(prob, odd):
    value = (prob * odd) - 1
    if prob >= 0.65 and value >= 0:
        return "🟢 SAFE", 3
    elif prob >= 0.50 and value >= 0.05:
        return "🟡 VALUE", 1.5
    elif value >= 0.15:
        return "🔴 AGRESSIF", 0.5
    return None, None

async def send(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)

def allowed_league(game):
    league = game.get("sport_title", "")
    return any(l in league for l in ALLOWED_LEAGUES)

async def main():
    await send("🤖 Bot Live Foot IA SNIPER actif. Marchés filtrés, bruit coupé.")

    while True:
        try:
            games = get_games()

            for game in games:
                if not allowed_league(game):
                    continue

                home = game["home_team"]
                away = game["away_team"]
                match_id = f"{home}-{away}"

                now = datetime.utcnow().timestamp()
                if match_id in last_sent and now - last_sent[match_id] < 900:
                    continue

                if not game["bookmakers"]:
                    continue

                for m in game["bookmakers"][0]["markets"]:
                    if m["key"] not in ["totals", "btts"]:
                        continue

                    for o in m["outcomes"]:
                        odd = o["price"]

                        if odd < 1.40 or odd > 4.00:
                            continue

                        # Proba simulée (à remplacer plus tard par vraie IA)
                        prob = 0.57

                        label, stake = classify(prob, odd)
                        if not label:
                            continue

                        value = round((prob * odd - 1) * 100, 1)

                        msg = f"""
⚽ {home} vs {away}

{label}
{o['name
