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
        "markets": "totals,btts",
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
    await send("🤖 Bot Live Foot IA filtré actif. En attente d'opportunités propres…")

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
                if match_id in last_sent and now - last_sent[match_id] < 600:
                    continue

                if not game["bookmakers"]:
                    continue

                for m in game["bookmakers"][0]["markets"]:
                    if m["key"] != "totals":
                        continue

                    for o in m["outcomes"]:
                        if o["name"] != "Over":
                            continue

                        odd = o["price"]
                        line = o["point"]

                        if odd < 1.40 or odd > 4.00:
                            continue

                        # Probabilité simulée (sera remplacée plus tard par vrai modèle)
                        prob = 0.56

                        result = classify(prob, odd)
                        if not result:
                            continue

                        label, stake = result
                        value = round((prob * odd - 1) * 100, 1)

                        msg = f"""
⚽ {home} vs {away}

{label}
Over {line} @ {odd}
Probabilité IA: {int(prob*100)}%
Value: +{value}%
Mise conseillée: {stake}%
"""

                        await send(msg)
                        last_sent[match_id] = now
                        await asyncio.sleep(8)

            await asyncio.sleep(120)

        except Exception as e:
            await send(f"⚠️ Erreur bot: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
