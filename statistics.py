# statistics_v2.py
import os
import csv
import pytz
from datetime import datetime, timedelta

# =========================
# CONFIG
# =========================
TZ = pytz.timezone("America/Sao_Paulo")

SIGNALS_LOG = "signals_log.csv"
STATS_LOG = "stats_log.csv"

TARGET_PCT = 0.02  # 2%
REPORT_HOURS = [9, 21]

# =========================
# STATE
# =========================
open_trades = []
last_report_sent = None

# =========================
# TIME
# =========================
def now_sp():
    return datetime.now(TZ)

def now_str():
    return now_sp().strftime("%Y-%m-%d %H:%M:%S")

# =========================
# INIT FILES
# =========================
def ensure_files():
    if not os.path.exists(SIGNALS_LOG):
        with open(SIGNALS_LOG, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "symbol", "signal",
                "entry_price", "target_price", "status"
            ])

    if not os.path.exists(STATS_LOG):
        with open(STATS_LOG, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "entry_time", "close_time", "symbol", "signal",
                "entry_price", "exit_price",
                "result", "duration_sec", "pct_move"
            ])

# =========================
# REGISTER ENTRY
# =========================
def register_entry(symbol, signal, price):
    entry_time = now_sp()
    target = price * (1 + TARGET_PCT) if signal == "LONG" else price * (1 - TARGET_PCT)

    trade = {
        "entry_time": entry_time,
        "symbol": symbol,
        "signal": signal,
        "entry_price": price,
        "target_price": target
    }
    open_trades.append(trade)

    with open(SIGNALS_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            entry_time.strftime("%Y-%m-%d %H:%M:%S"),
            symbol, signal, f"{price:.8f}", f"{target:.8f}", "OPEN"
        ])

# =========================
# CHECK TARGET
# =========================
def check_trades(current_price, send_telegram):
    global open_trades

    still_open = []

    for t in open_trades:
        hit = (
            current_price >= t["target_price"]
            if t["signal"] == "LONG"
            else current_price <= t["target_price"]
        )

        if hit:
            close_time = now_sp()
            duration = (close_time - t["entry_time"]).total_seconds()
            pct = (
                (current_price - t["entry_price"]) / t["entry_price"]
                if t["signal"] == "LONG"
                else (t["entry_price"] - current_price) / t["entry_price"]
            ) * 100

            with open(STATS_LOG, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    t["entry_time"].strftime("%Y-%m-%d %H:%M:%S"),
                    close_time.strftime("%Y-%m-%d %H:%M:%S"),
                    t["symbol"], t["signal"],
                    f"{t['entry_price']:.8f}",
                    f"{current_price:.8f}",
                    "SUCCESS",
                    int(duration),
                    f"{pct:.2f}"
                ])

            send_telegram(
                f"✅ {t['signal']} {t['symbol']} ATINGIU META\n"
                f"Entrada: {t['entry_price']:.8f}\n"
                f"Saída: {current_price:.8f}\n"
                f"Tempo: {int(duration)}s\n"
                f"Resultado: +{pct:.2f}%"
            )
        else:
            still_open.append(t)

    open_trades = still_open

# =========================
# PERIODIC REPORT
# =========================
def maybe_send_report(send_telegram):
    global last_report_sent

    now = now_sp()
    if now.hour not in REPORT_HOURS:
        return

    if last_report_sent and (now - last_report_sent) < timedelta(hours=1):
        return

    total = success = fail = 0

    if os.path.exists(STATS_LOG):
        with open(STATS_LOG, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                total += 1
                if r["result"] == "SUCCESS":
                    success += 1
                else:
                    fail += 1

    if total == 0:
        return

    pct = success / total * 100
    send_telegram(
        f"📊 RELATÓRIO 12H\n"
        f"Total: {total}\n"
        f"Sucesso: {success}\n"
        f"Fracasso: {fail}\n"
        f"Assertividade: {pct:.2f}%"
    )

    last_report_sent = now
