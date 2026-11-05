import os
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_btc_data():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    r = requests.get(url, timeout=15)
    data = r.json()["bitcoin"]
    return data["usd"], data["usd_24h_change"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

price, change_24h = get_btc_data()

# Petit calcul de signal simple et logique
if change_24h > 1:
    signal = "HAUSSE 🟢"
    proba = 68.0
elif change_24h < -1:
    signal = "BAISSE 🔴"
    proba = 65.0
else:
    signal = "NEUTRE ⚪"
    proba = 55.0

message = f"""🚀 SIGNAL BTC 4H
Proba: {proba}%
Prix: {price:,.0f}$
Variation 24h: {change_24h:+.2f}%
Filtre {signal} - Win 55% | {change_24h:+.3f}%"""

print(message)
send_telegram(message)
