import json
import os
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from fastapi import FastAPI

from chatbot import responder

# Carrega as variáveis do arquivo .env ao iniciar o servidor.
load_dotenv()

# No Docker Compose, o WAHA é acessado pelo nome do serviço: waha.
WAHA_API_URL = os.getenv("WAHA_API_URL", "http://localhost:3000").rstrip("/")
WAHA_SESSION = os.getenv("WAHA_SESSION", "default")
WAHA_API_KEY = os.getenv("WAHA_API_KEY")

app = FastAPI()


def extrair_mensagem(evento: dict) -> tuple[str, str] | None:
    # Processa apenas mensagens novas recebidas do WhatsApp.
    if evento.get("event") != "message":
        return None

    payload = evento.get("payload", {})
    # Não responde às mensagens enviadas pelo próprio bot.
    if payload.get("fromMe"):
        return None

    texto = payload.get("body")
    chat_id = payload.get("from")
    if not texto or not chat_id:
        return None

    return chat_id, texto


def enviar_mensagem(chat_id: str, texto: str) -> None:
    # Prepara o pedido que envia o texto de volta ao WhatsApp pelo WAHA.
    url = f"{WAHA_API_URL}/api/sendText"
    dados = {"chatId": chat_id, "text": texto, "session": WAHA_SESSION}
    headers = {"Content-Type": "application/json"}
    if WAHA_API_KEY:
        headers["X-Api-Key"] = WAHA_API_KEY

    request = Request(
        url,
        data=json.dumps(dados).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    with urlopen(request) as response:
        response.read()


@app.post("/webhook")
def receber_webhook(evento: dict) -> dict[str, str]:
    # Recebe a mensagem, gera uma resposta e a envia ao mesmo contato.
    mensagem = extrair_mensagem(evento)
    if mensagem is None:
        return {"status": "ignored"}

    chat_id, texto = mensagem
    resposta = responder(texto)
    enviar_mensagem(chat_id, resposta)
    return {"status": "sent"}
