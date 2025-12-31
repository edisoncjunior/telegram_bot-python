# main.py
import time
import requests
import numpy as np
import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise RuntimeError("ERRO: TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não definidos no arquivo .env")


from statistics import (
    ensure_log_files, registrar_sinal, verificar_sinais,
    write_signal_log, estat, agora_sp_str
)
from security import send_telegram

# =========================
# CONFIG
# =========================
SYMBOL = "ARPAUSDT"
INTERVAL = "1m"

BOLL_PERIOD = 8
BOLL_STD = 2

LOOP_SLEEP = 2
last_signal = None

# =========================
# BINANCE
# =========================
def get_klines(symbol, interval, limit=200):
    r = requests.get(
        "https://fapi.binance.com/fapi/v1/klines",
        params={"symbol": symbol, "interval": interval, "limit": limit},
        timeout=10
    )
    r.raise_for_status()
    return r.json()

def bollinger(closes):
    arr = np.array(closes)
    sma = arr[-BOLL_PERIOD:].mean()
    std = arr[-BOLL_PERIOD:].std()
    return sma + BOLL_STD * std, sma - BOLL_STD * std

# =========================
# INIT
# =========================
ensure_log_files()
print("Bot Bollinger ARPAUSDT iniciado")

# =========================
# LOOP
# =========================
while True:
    try:
        klines = get_klines(SYMBOL, INTERVAL)
        closes = [float(k[4]) for k in klines]
        price = closes[-1]

        upper, lower = bollinger(closes)
        verificar_sinais(closes)

        ts = agora_sp_str()
        print(f"{ts} | {price:.8f} | U:{upper:.8f} L:{lower:.8f}")

        if price > upper:
            pct = (price - upper) / upper * 100
            label = "SHORT SHORT" if pct >= 0.2 else "SHORT"
            if label != last_signal:
                send_telegram(f"{label} ARPAUSDT\nPreço: {price:.8f}")
                write_signal_log(ts, SYMBOL, label, price, pct, "upper")
                registrar_sinal("SHORT", price, closes)
                last_signal = label

        elif price < lower:
            pct = (lower - price) / lower * 100
            label = "LONG LONG" if pct >= 0.2 else "LONG"
            if label != last_signal:
                send_telegram(f"{label} ARPAUSDT\nPreço: {price:.8f}")
                write_signal_log(ts, SYMBOL, label, price, pct, "lower")
                registrar_sinal("LONG", price, closes)
                last_signal = label

        if estat["total"] > 0:
            print(f"Total: {estat['total']} | "
                  f"3c: {estat['acertos_3']} | "
                  f"4c: {estat['acertos_4']}")

    except Exception as e:
        print("[ERRO]", e)

    time.sleep(LOOP_SLEEP)
