import os
import asyncio
import requests
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)

def get_soccer_odds():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds"
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

async def main():
    await send("🤖 Bot Live Foot IA connecté. En attente d'opportunités…")

    while True:
        try:
            games = get_soccer_odds()

            for game in games:
                home = game["home_team"]
                away = game["away_team"]

                if not game["bookmakers"]:
                    continue

                markets = game["bookmakers"][0]["markets"]

                for m in markets:
                    if m["key"] == "totals":
                        for o in m["outcomes"]:
                            if o["name"] == "Over":
                                odd = o["price"]

                                # probabilité simulée pour l’instant
                                prob = 0.55

                                result = classify(prob, odd)
                                if result:
                                    label, stake = result
                                    value = round((prob * odd - 1) * 100, 1)

                                    msg = f"""
⚽ {home} vs {away}

{label}
Over {o['point']} @ {odd}
Probabilité IA: {int(prob*100)}%
Value: +{value}%
Mise conseillée: {stake}%
"""
                                    await send(msg)
                                    await asyncio.sleep(10)

            await asyncio.sleep(120)

        except Exception as e:
            await send(f"⚠️ Erreur bot: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
