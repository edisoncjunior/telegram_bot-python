# main.py
import time
import requests
import numpy as np

from security import send_telegram

from statistics import (
    ensure_files,
    register_entry,
    check_trades,
    maybe_send_report
)


# =========================
# CONFIGURAÇÕES GERAIS
# =========================
SYMBOL = "ARPAUSDT"
INTERVAL = "1m"

BOLL_PERIOD = 8
BOLL_STD = 2

LOOP_SLEEP = 5 # segundos
last_signal = None

# =========================
# MEXC API
# =========================
# =========================
# MEXC API
# =========================
def get_klines(symbol, interval, limit=200, retries=3):
    url = "https://contract.mexc.com/api/v1/contract/kline"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, timeout=5)
            r.raise_for_status()

            data = r.json()
            if "data" not in data:
                raise RuntimeError("Resposta inválida da MEXC")

            return data["data"]

        except Exception as e:
            print(f"[WARN] MEXC tentativa {attempt}/{retries} falhou: {e}")
            time.sleep(2)

    raise RuntimeError("MEXC indisponível após múltiplas tentativas")

# =========================
# BOLLINGER BANDS
# =========================
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
ensure_files()
print("🚀 Bot Bollinger 1min ARPAUSDT iniciado (Railway)")


# =========================
# LOOP PRINCIPAL
# =========================
while True:
    try:
        klines = get_klines(SYMBOL, INTERVAL)

        closes = [float(k["close"]) for k in klines]
        price = closes[-1]

        upper, lower = bollinger(closes)

        print(
            f"Preço: {price:.8f} | "
            f"Upper: {upper:.8f} | "
            f"Lower: {lower:.8f}"
        )

        # =========================
        # VERIFICA ALVOS ATIVOS
        # =========================
        check_trades(price, send_telegram)

        # =========================
        # SHORT
        # =========================
        if price > upper:
            label = "SHORT"
            if last_signal != label:
                send_telegram(
                    f"🔴 SHORT {SYMBOL}\n"
                    f"Preço: {price:.8f}\n"
                    f"Rompimento Bollinger Superior"
                )

                register_entry(SYMBOL, "SHORT", price)
                last_signal = label

        # =========================
        # LONG
        # =========================
        elif price < lower:
            label = "LONG"
            if last_signal != label:
                send_telegram(
                    f"🟢 LONG {SYMBOL}\n"
                    f"Preço: {price:.8f}\n"
                    f"Rompimento Bollinger Inferior"
                )

                register_entry(SYMBOL, "LONG", price)
                last_signal = label

        # =========================
        # RELATÓRIO 12H
        # =========================
        maybe_send_report(send_telegram)

    except Exception as e:
        print("[ERRO LOOP]", e)
        time.sleep(LOOP_SLEEP)
