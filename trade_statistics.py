# trade_statistics.py
import os
import json
import pytz
from datetime import datetime, timedelta

# =========================
# CONFIG
# =========================
TZ_SP = pytz.timezone("America/Sao_Paulo")
LOG_DIR = "logs"
ENTRADAS_FILE = f"{LOG_DIR}/entradas.json"
RESULTADOS_FILE = f"{LOG_DIR}/resultados.json"

META_PCT = 0.02  # 2%
RESUMO_INTERVALO = timedelta(hours=12)
HORA_BASE_RESUMO = 21  # 21h São Paulo

# =========================
# ESTADO
# =========================
entradas_abertas = []
ultima_execucao_resumo = None

# =========================
# TEMPO
# =========================
def agora_sp():
    return datetime.now(TZ_SP)

def agora_str():
    return agora_sp().strftime("%Y-%m-%d %H:%M:%S")

# =========================
# INIT
# =========================
def init_statistics():
    os.makedirs(LOG_DIR, exist_ok=True)

    for f in [ENTRADAS_FILE, RESULTADOS_FILE]:
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as fp:
                json.dump([], fp)

    print("📊 Estatísticas inicializadas")

# =========================
# ENTRADAS
# =========================
def registrar_entrada(symbol, side, price):
    entrada = {
        "timestamp": agora_str(),
        "symbol": symbol,
        "side": side,
        "price": price,
        "status": "ABERTA"
    }

    entradas_abertas.append(entrada)

    with open(ENTRADAS_FILE, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append(entrada)
        f.seek(0)
        json.dump(data, f, indent=2)

# =========================
# VERIFICA RESULTADOS
# =========================
def verificar_resultados(preco_atual):
    fechadas = []

    for e in entradas_abertas:
        entrada_preco = e["price"]
        side = e["side"]

        alvo = (
            entrada_preco * (1 + META_PCT)
            if side == "LONG"
            else entrada_preco * (1 - META_PCT)
        )

        sucesso = (
            preco_atual >= alvo
            if side == "LONG"
            else preco_atual <= alvo
        )

        if sucesso:
            e["status"] = "SUCESSO"
            e["fechado_em"] = agora_str()
            fechadas.append(e)

    if fechadas:
        with open(RESULTADOS_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.extend(fechadas)
            f.seek(0)
            json.dump(data, f, indent=2)

    for f in fechadas:
        entradas_abertas.remove(f)

# =========================
# RESUMO 12H
# =========================
def enviar_resumo_12h(send_telegram):
    global ultima_execucao_resumo

    agora = agora_sp()

    if ultima_execucao_resumo:
        if agora - ultima_execucao_resumo < RESUMO_INTERVALO:
            return

    if agora.hour != HORA_BASE_RESUMO:
        return

    with open(RESULTADOS_FILE, "r", encoding="utf-8") as f:
        dados = json.load(f)

    total = len(dados)
    sucesso = sum(1 for d in dados if d["status"] == "SUCESSO")
    fracasso = total - sucesso
    pct = (sucesso / total * 100) if total else 0

    msg = (
        f"📊 RESUMO 12H\n"
        f"Entradas: {total}\n"
        f"Sucesso: {sucesso}\n"
        f"Fracasso: {fracasso}\n"
        f"Assertividade: {pct:.2f}%"
    )

    send_telegram(msg)
    ultima_execucao_resumo = agora
