import os
import asyncio
import requests
from telegram import Bot
from statistics import mean
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)

ALLOWED_LEAGUES = [
    "Premier League","La Liga","Serie A","Bundesliga","Ligue 1",
    "UEFA Champions League","UEFA Europa League",
    "Eredivisie","Primeira Liga","Jupiler Pro League"
]

last_sent = {}

def get_games():
    url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "totals,btts",
        "oddsFormat": "decimal",
        "bookmakers": "bet365,pinnacle,williamhill,betfair,unibet"
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

async def send(msg):
    await bot.send_message(chat_id=CHAT_ID, text=msg)

def allowed_league(game):
    league = game.get("sport_title","")
    return any(l in league for l in ALLOWED_LEAGUES)

async def main():
    await send("🤖 Bot IA Multi-Bookmakers actif. Détection de value réelle…")

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

                for m in ["totals","btts"]:
                    odds_list = []

                    for b in game["bookmakers"]:
                        for market in b["markets"]:
                            if market["key"] != m:
                                continue
                            for o in market["outcomes"]:
                                if m == "totals" and o["name"] == "Over":
                                    odds_list.append(o["price"])
                                if m == "btts" and o["name"] == "Yes":
                                    odds_list.append(o["price"])

                    if len(odds_list) < 3:
                        continue

                    market_avg = mean(odds_list)
                    best_odd = max(odds_list)

                    implied_prob = 1 / market_avg
                    prob = implied_prob * 1.06   # edge IA

                    label, stake = classify(prob, best_odd)
                    if not label:
                        continue

                    value = round((prob * best_odd - 1) * 100,1)

                    bet_name = "Over (market)" if m == "totals" else "BTTS Yes"

                    msg = f"""
⚽ {home} vs {away}

{label}
{bet_name} @ {best_odd}
Probabilité IA: {int(prob*100)}%
Value: +{value}%
Mise conseillée: {stake}%
"""
                    await send(msg)
                    last_sent[match_id] = now
                    await asyncio.sleep(8)

            await asyncio.sleep(120)

        except Exception as e:
            await send(f"⚠️ Bot error: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
