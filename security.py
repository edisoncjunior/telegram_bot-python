# security.py
import os
import requests


def _get_env():
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("[AVISO] Telegram desabilitado (env não disponível ainda)")
        return None, None

    return token, chat_id


def send_telegram(msg: str):
    print("[DEBUG] Preparando envio Telegram")

    token, chat_id = _get_env()

    if not token or not chat_id:
        print("[AVISO TELEGRAM] Variáveis ausentes no runtime")
        print(f"TELEGRAM_TOKEN={token}")
        print(f"TELEGRAM_CHAT_ID={chat_id}")
        return  # NÃO quebra o app

    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": msg
        }

        r = requests.post(url, json=payload, timeout=10)
        print(f"[TELEGRAM] {r.status_code} | {r.text}")

    except Exception as e:
        print("[ERRO TELEGRAM EXCEPTION]", e)
