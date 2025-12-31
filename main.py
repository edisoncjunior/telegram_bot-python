# main.py
import time
import requests
from datetime import datetime
import pytz

from statistics import (
    init_statistics,
    registrar_entrada,
    verificar_resultados,
    enviar_resumo_12h
)

# =========================
# CONFIGURAÇÃO GERAL
# =========================
SYMBOL = "ARPAUSDT"
INTERVAL = "Min1"
API_URL = "https://contract.mexc.com/api/v1/contract/kline"

TIMEOUT = 15          # segundos
RETRIES = 2
SLEEP_LOOP = 60       # 1 minuto

TZ_SP = pytz.timezone("America/Sao_Paulo")

# =========================
# LOG SIMPLES
# =========================
def log(msg):
    ts = datetime.now(TZ_SP).strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts} | {msg}", flush=True)

# =========================
# FETCH DADOS MEXC
# =========================
def fetch_klines():
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "limit": 50
    }

    for tentativa in range(1, RETRIES + 1):
        try:
            r = requests.get(API_URL, params=params, timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json()

            if "data" not in data:
                raise ValueError("Resposta inválida da MEXC")

            return data["data"]

        except Exception as e:
            log(f"[WARN] MEXC tentativa {tentativa}/{RETRIES} falhou: {e}")
            time.sleep(5)

    log("[ERRO LOOP] MEXC indisponível após múltiplas tentativas")
    return None

# =========================
# CÁLCULO BOLLINGER
# =========================
def bollinger_bands(closes, period=20, mult=2):
    if len(closes) < period:
        return None, None

    slice_ = closes[-period:]
    ma = sum(slice_) / period
    variance = sum((x - ma) ** 2 for x in slice_) / period
    std = variance ** 0.5

    upper = ma + mult * std
    lower = ma - mult * std

    return upper, lower

# =========================
# MAIN LOOP
# =========================
def main():
    log(f"🚀 Bot Bollinger 1min {SYMBOL} iniciado (Railway)")
    init_statistics()

    last_candle_time = None

    while True:
        try:
            klines = fetch_klines()
            if not klines:
                time.sleep(SLEEP_LOOP)
                continue

            closes = [float(k[4]) for k in klines]
            last_kline = klines[-1]
            candle_time = int(last_kline[0])

            # evita processar o mesmo candle
            if candle_time == last_candle_time:
                time.sleep(5)
                continue

            last_candle_time = candle_time
            price = closes[-1]

            upper, lower = bollinger_bands(closes)
            if not upper or not lower:
                time.sleep(SLEEP_LOOP)
                continue

            log(f"Preço: {price:.8f} | Upper: {upper:.8f} | Lower: {lower:.8f}")

            # =========================
            # SINAIS
            # =========================
            if price <= lower:
                log("📈 SINAL LONG detectado")
                registrar_entrada(
                    symbol=SYMBOL,
                    signal="LONG",
                    price=price
                )

            elif price >= upper:
                log("📉 SINAL SHORT detectado")
                registrar_entrada(
                    symbol=SYMBOL,
                    signal="SHORT",
                    price=price
                )

            # =========================
            # VERIFICA RESULTADOS
            # =========================
            verificar_resultados(price)
            enviar_resumo_12h()

        except Exception as e:
            log(f"[ERRO GERAL LOOP] {e}")

        time.sleep(SLEEP_LOOP)

# =========================
# START
# =========================
if __name__ == "__main__":
    main()
