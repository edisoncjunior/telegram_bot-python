# security.py
import os
import requests

# ======================================================
# VARIÁVEIS DE AMBIENTE (Railway / Local)
# ======================================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def _check_telegram_env():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError(
            "Variáveis de ambiente do Telegram não carregadas:\n"
            f"TELEGRAM_TOKEN={TELEGRAM_TOKEN}\n"
            f"TELEGRAM_CHAT_ID={TELEGRAM_CHAT_ID}\n"
            "➡️ Configure corretamente no Railway → Service → Variables"
        )


# ======================================================
# TELEGRAM
# ======================================================
def send_telegram(msg: str):
    _check_telegram_env()

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg
        }
        r = requests.post(url, json=payload, timeout=10)
        print(f"[Telegram] {r.status_code} | {r.text}")
    except Exception as e:
        print("[ERRO TELEGRAM]", e)
