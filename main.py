﻿# main.py
# versão estável git 998e572
# ajuste tirando statistics
# colocar no ambiente production

import time
import requests
import numpy as np

from security import send_telegram

# =========================
# CONFIGURAÇÕES
# =========================
SYMBOL = "ARPAUSDT"
INTERVAL = "1m"

BOLL_PERIOD = 8
BOLL_STD = 2

LOOP_SLEEP = 30
last_signal = None

# =========================
# MEXC
# =========================
def get_klines(symbol, interval, limit=200):
    url = "https://api.mexc.com/api/v3/klines"
    r = requests.get(
        url,
        params={
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        },
        timeout=10,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )
    r.raise_for_status()
    return r.json()


def bollinger(closes):
    arr = np.array(closes)
    sma = arr[-BOLL_PERIOD:].mean()
    std = arr[-BOLL_PERIOD:].std()
    upper = sma + BOLL_STD * std
    lower = sma - BOLL_STD * std
    return upper, lower


# =========================
# INIT
# =========================

ensure_log_files()
print("🚀 Bot Bollinger ARPAUSDT iniciado")
send_telegram("🚀 Bot Bollinger ARPAUSDT iniciado")


# =========================
# LOOP PRINCIPAL
# =========================
while True:
    try:
        klines = get_klines(SYMBOL, INTERVAL)
        closes = [float(k[4]) for k in klines]
        price = closes[-1]

        upper, lower = bollinger(closes)
        verificar_sinais(closes)

        ts = agora_sp_str()
        print(f"{ts} | SYMBOL: {SYMBOL} | Preço: {price:.8f} | Upper: {upper:.8f} | Lower: {lower:.8f}")
        send_telegram(f"{ts} | SYMBOL: {SYMBOL} | Preço: {price:.8f} | Upper: {upper:.8f} | Lower: {lower:.8f}")
        # ===== SHORT =====
        if price > upper:
            pct = (price - upper) / upper * 100
            label = "SHORT STRONG" if pct >= 0.2 else "SHORT"

            if label != last_signal:
                try:
                    send_telegram(f"{label} ARPAUSDT\nPreço: {price:.8f}")
                except Exception as e:
                    print("[Aviso Telegram]", e)

                write_signal_log(ts, SYMBOL, label, price, pct, "upper")
                registrar_sinal("SHORT", price, closes)
                last_signal = label

        # ===== LONG =====
        elif price < lower:
            pct = (lower - price) / lower * 100
            label = "LONG STRONG" if pct >= 0.2 else "LONG"

            if label != last_signal:
                try:
                    send_telegram(f"{label} ARPAUSDT\nPreço: {price:.8f}")
                except Exception as e:
                    print("[Aviso Telegram]", e)

                write_signal_log(ts, SYMBOL, label, price, pct, "lower")
                registrar_sinal("LONG", price, closes)
                last_signal = label


    except Exception as e:
        print("[ERRO]", e)

    time.sleep(LOOP_SLEEP)