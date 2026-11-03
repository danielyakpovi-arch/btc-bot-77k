import requests, yfinance as yf, pandas as pd, joblib, os

TOKEN = os.environ["8921621106:AAFnrFP_MkR9pkQ5LJhsOo0ZMFOvrmy1VpI"]
CHAT_ID = os.environ["6301782734"]
SEUIL = 0.60

def rsi(s, p=14):
    d = s.diff()
    g = d.where(d>0,0).rolling(p).mean()
    l = -d.where(d<0,0).rolling(p).mean()
    return 100-(100/(1+g/l))

def ema(s,p):
    return s.ewm(span=p, adjust=False).mean()

model = joblib.load('model_btc_77k.pkl')

df = yf.download("BTC-USD", period="700d", interval="4h", auto_adjust=True, progress=False)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
df = df[["Close","High","Low","Volume"]].copy()
df.columns = ["close","high","low","volume"]
df = df.dropna()
df['rsi'] = rsi(df['close'],14)
df['ema20'] = ema(df['close'],20)
df['ema50'] = ema(df['close'],50)
df['ema200'] = ema(df['close'],200)
df['macd'] = df['ema20']-df['ema50']
df['return_6h'] = df['close'].pct_change(6)
df['vol_ratio'] = df['volume'] / df['volume'].rolling(30).mean()
tr1 = df['high']-df['low']
tr2 = (df['high']-df['close'].shift()).abs()
tr3 = (df['low']-df['close'].shift()).abs()
tr = pd.concat([tr1,tr2,tr3], axis=1).max(axis=1)
df['atr'] = tr.rolling(14).mean()
df = df.dropna()

FEATURES = ['rsi','ema20','ema50','ema200','macd','return_6h','vol_ratio','atr']
X_live = df[FEATURES].iloc[[-1]]
prix = float(df['close'].iloc[-1])
proba = float(model.predict_proba(X_live)[0][1])

if proba >= SEUIL:
    text = f"🚀 SIGNAL BTC 4H\nProba: {proba*100:.1f}%\nPrix: {prix}$\nFiltre HAUSSE - W. Duffy"
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": text})
    print(f"Alerte envoyée {proba*100:.1f}%")
else:
    print(f"Pas de signal {proba*100:.1f}%")
