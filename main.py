import os
import requests

# --- TES PARAMETRES OPTION B - 20$ ---
CAPITAL_PAR_TRADE = 20  # $
RISQUE_POURCENT = 2     # Stop-Loss -2%
GAIN_POURCENT = 6       # Take-Profit +6% (Ratio 1:3)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})

def main():
    urls = [
        "https://data-api.binance.vision/api/v3/ticker/24hr?symbol=BTCUSDT",
        "https://api.binance.us/api/v3/ticker/24hr?symbol=BTCUSDT"
    ]
    
    r = None
    for url in urls:
        try:
            resp = requests.get(url, timeout=10).json()
            if 'lastPrice' in resp:
                r = resp
                break
        except:
            continue
    
    if r is None:
        print("Impossible de récupérer le prix")
        return

    prix = float(r['lastPrice'])
    variation = float(r['priceChangePercent'])

    # --- CAS 1 : HAUSSE = ON ENVOIE LE PLAN COMPLET ---
    if variation >= 1:
        stop_loss = prix * (1 - RISQUE_POURCENT / 100)
        take_profit = prix * (1 + GAIN_POURCENT / 100)
        risque_dollar = CAPITAL_PAR_TRADE * (RISQUE_POURCENT / 100)
        gain_dollar = CAPITAL_PAR_TRADE * (GAIN_POURCENT / 100)

        message = f"""🟢 SIGNAL BTC - ACHAT - OPTION B (20$)

Prix actuel: {prix:.2f} $
Variation 24h: {variation:.2f}%

💰 Plan de trade (20$):
Entrée: {prix:.2f} $
Stop-Loss (-2%): {stop_loss:.2f} $
Take-Profit (+6%): {take_profit:.2f} $

Risque: -{risque_dollar:.2f} $
Gain visé: +{gain_dollar:.2f} $
Ratio: 1:3

👉 Tu peux acheter avec 20$, mets ton Stop et ton Take sur Binance.
"""

    # --- CAS 2 : BAISSE OU NEUTRE = ON DIT JUSTE D'ATTENDRE ---
    else:
        if variation <= -1:
            signal_txt = "🔴 BAISSE"
        else:
            signal_txt = "⚪ NEUTRE"

        message = f"""⏸️ SIGNAL BTC - ATTENDRE

Signal: {signal_txt}
Prix actuel: {prix:.2f} $
Variation 24h: {variation:.2f}%

❌ NE PAS ACHETER
Reste en dehors, attends un signal 🟢 HAUSSE.

Ton argent est en sécurité.
"""

    send_telegram(message)
    print("Envoyé !")

if __name__ == "__main__":
    main()
