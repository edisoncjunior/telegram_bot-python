# statistics.py
import os
import time
import pytz
from datetime import datetime

# =========================
# CONFIG
# =========================
LOG_FILE = "bb_arpa_logs.txt"
STATS_LOG_FILE = "bb_arpa_stats.txt"

TELEGRAM_SEND_STATS = True
STATS_SEND_INTERVAL = 300

# =========================
# ESTADO
# =========================
sinais = []
estat = {
    "total": 0,
    "acertos_3": 0,
    "acertos_4": 0
}

_last_stats_sent_time = 0

# =========================
# TEMPO
# =========================
def agora_sp():
    return datetime.now(pytz.timezone("America/Sao_Paulo"))

def agora_sp_str():
    return agora_sp().strftime("%Y-%m-%d %H:%M:%S")

# =========================
# LOGS
# =========================
def ensure_log_files():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("timestamp\tsymbol\tsignal\tprice\trupture_percent\tmeta\n")

    if not os.path.exists(STATS_LOG_FILE):
        with open(STATS_LOG_FILE, "w", encoding="utf-8") as f:
            f.write("timestamp\ttotal\tacertos_3\tacertos_4\tacertos3_pct\tacertos4_pct\n")

def write_signal_log(ts, symbol, signal, price, percent, meta=""):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ts}\t{symbol}\t{signal}\t{price:.8f}\t{percent:.6f}\t{meta}\n")

def write_stats_log():
    if estat["total"] == 0:
        return

    ac3 = estat["acertos_3"] / estat["total"] * 100
    ac4 = estat["acertos_4"] / estat["total"] * 100

    with open(STATS_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"{agora_sp_str()}\t{estat['total']}\t"
            f"{estat['acertos_3']}\t{estat['acertos_4']}\t"
            f"{ac3:.2f}\t{ac4:.2f}\n"
        )

# =========================
# SINAIS
# =========================
def registrar_sinal(tipo, preco, closes):
    sinais.append({
        "tipo": tipo,
        "preco": preco,
        "index": len(closes) - 1,
        "v3": False,
        "v4": False
    })
    estat["total"] += 1

def verificar_sinais(closes):
    for s in sinais:
        i = s["index"]

        if not s["v3"] and len(closes) > i + 3:
            if (s["tipo"] == "LONG" and closes[i + 3] > s["preco"]) or \
               (s["tipo"] == "SHORT" and closes[i + 3] < s["preco"]):
                estat["acertos_3"] += 1
            s["v3"] = True

        if not s["v4"] and len(closes) > i + 4:
            if (s["tipo"] == "LONG" and closes[i + 4] > s["preco"]) or \
               (s["tipo"] == "SHORT" and closes[i + 4] < s["preco"]):
                estat["acertos_4"] += 1
            s["v4"] = True

    sinais[:] = [s for s in sinais if not (s["v3"] and s["v4"])]
