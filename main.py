import os
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_btc_price():
    # Essai 1 : CoinGecko (marche toujours sur GitHub)
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        r = requests.get(url, timeout=15)
        data = r.json()
        return float(data["bitcoin"]["usd"])
    except Exception as e:
        print(f"CoinGecko fail: {e}")

    # Essai 2 : Coinbase en secours
    try:
        url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
        r = requests.get(url, timeout=15)
        return float(r.json()["data"]["amount"])
    except Exception as e:
        print(f"Coinbase fail: {e}")

    raise Exception("Impossible de récupérer le prix BTC")

def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("TOKEN ou CHAT_ID manquant dans Secrets")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

price = get_btc_price()
message = f"🚀 BTC Bot 77k\nPrix BTC actuel : {price:,.2f} USD"
print(message)
send_telegram(message)
