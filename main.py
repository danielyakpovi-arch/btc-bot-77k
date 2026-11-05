import os
import requests

# --- PARAMETRES OPTION B - 20$ ---
CAPITAL_PAR_TRADE = 20
RISQUE_POURCENT = 2
GAIN_POURCENT = 6

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})

def get_data():
    # Prix + variation
    base = "https://data-api.binance.vision"
    ticker = requests.get(f"{base}/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=10).json()
    # Bougies 1h pour calculer RSI et EMA
    klines = requests.get(f"{base}/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=250", timeout=10).json()
    closes = [float(k[4]) for k in klines]
    return float(ticker['lastPrice']), float(ticker['priceChangePercent']), closes

def calc_ema(prices, period):
    k = 2 / (period + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = p * k + ema * (1 - k)
    return ema

def calc_rsi(prices, period=14):
    gains = []
    losses = []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff >= 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-diff)
    # On prend les 14 dernières
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def main():
    try:
        prix, variation, closes = get_data()
    except Exception as e:
        print(f"Erreur: {e}")
        return

    ema50 = calc_ema(closes, 50)
    ema200 = calc_ema(closes, 200)
    rsi = calc_rsi(closes, 14)

    # --- LOGIQUE INTELLIGENTE ---
    tendance_ok = prix > ema50 and ema50 > ema200
    rsi_ok = 40 <= rsi <= 68
    momentum_ok = variation > -1  # On ne veut pas acheter en pleine chute

    raisons = []
    if not tendance_ok:
        raisons.append(f"Tendance baissière (Prix {prix:.0f} < EMA50 {ema50:.0f})")
    if not rsi_ok:
        if rsi > 68:
            raisons.append(f"RSI trop haut {rsi:.1f} (trop cher)")
        else:
            raisons.append(f"RSI trop bas {rsi:.1f} (pas de force)")
    if not momentum_ok:
        raisons.append(f"Chute 24h {variation:.2f}%")

    # --- CAS 1 : VRAI ACHAT ---
    if tendance_ok and rsi_ok and momentum_ok:
        stop_loss = prix * (1 - RISQUE_POURCENT / 100)
        take_profit = prix * (1 + GAIN_POURCENT / 100)
        message = f"""🟢 SIGNAL BTC - VRAI ACHAT - OPTION B (20$)

Prix: {prix:.2f} $
Variation 24h: {variation:.2f}%
RSI (14): {rsi:.1f} ✅
EMA50: {ema50:.2f} $ ✅
EMA200: {ema200:.2f} $ ✅
Tendance: HAUSSIÈRE CONFIRMÉE

💰 Plan de trade (20$):
Entrée: {prix:.2f} $
Stop-Loss (-2%): {stop_loss:.2f} $
Take-Profit (+6%): {take_profit:.2f} $

Risque: -0.40 $
Gain visé: +1.20 $
Ratio: 1:3
"""
    # --- CAS 2 : ATTENDRE ---
    else:
        raison_txt = "\n".join([f"- {r}" for r in raisons])
        message = f"""⏸️ SIGNAL BTC - ATTENDRE

Prix: {prix:.2f} $
Variation 24h: {variation:.2f}%
RSI (14): {rsi:.1f}
EMA50: {ema50:.2f} $
EMA200: {ema200:.2f} $

❌ NE PAS ACHETER
Pourquoi ?
{raison_txt}

Ton argent est en sécurité.
"""

    send_telegram(message)
    print("Envoyé !")

if __name__ == "__main__":
    main()
