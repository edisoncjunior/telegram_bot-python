# security.py
import os
import requests
from dotenv import load_dotenv

# ======================================================
# CARREGAMENTO EXPLÍCITO DO .env (WINDOWS SAFE)
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

if not os.path.exists(ENV_PATH):
    raise RuntimeError(f"Arquivo .env NÃO encontrado em: {ENV_PATH}")

load_dotenv(dotenv_path=ENV_PATH, override=True)

# ======================================================
# VARIÁVEIS DE AMBIENTE
# ======================================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# ======================================================
# VALIDAÇÃO
# ======================================================
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise RuntimeError(
        f"Variáveis não carregadas.\n"
        f"TELEGRAM_TOKEN={TELEGRAM_TOKEN}\n"
        f"TELEGRAM_CHAT_ID={TELEGRAM_CHAT_ID}"
    )

# ======================================================
# TELEGRAM
# ======================================================
def send_telegram(msg: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
        r = requests.post(url, json=payload, timeout=10)
        print(f"[Telegram] {r.status_code} | {r.text}")
    except Exception as e:
        print("[ERRO TELEGRAM]", e)
