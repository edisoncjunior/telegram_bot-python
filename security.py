# security.py
import os
import requests


def _get_env():
    """
    Lê variáveis de ambiente SOMENTE em runtime.
    Funciona 100% local + Railway.
    """
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise RuntimeError(
            "Variáveis de ambiente obrigatórias NÃO disponíveis em runtime:\n"
            f"TELEGRAM_TOKEN={token}\n"
            f"TELEGRAM_CHAT_ID={chat_id}\n"
            "➡️ Verifique o Service ativo no Railway"
        )

    return token, chat_id


def send_telegram(msg: str):
    """
    Envia mensagem ao Telegram com validação tardia (safe).
    """
    print("[DEBUG] Preparando envio Telegram")

    token, chat_id = _get_env()

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"[TELEGRAM] status={r.status_code}")
        print(f"[TELEGRAM] response={r.text}")
    except Exception as e:
        print("[ERRO TELEGRAM]", e)
