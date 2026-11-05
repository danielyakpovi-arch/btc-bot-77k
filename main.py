import os
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_btc_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    r = requests.get(url, timeout=10)
    return float(r.json()["price"])

def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("TOKEN ou CHAT_ID manquant dans Secrets")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

price = get_btc_price()
message = f"🚀 BTC Bot 77k\nPrix BTC actuel : {price:,.2f} USDT"
print(message)
send_telegram(message)
