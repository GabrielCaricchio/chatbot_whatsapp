import json
import os
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from fastapi import FastAPI

from chatbot import responder

load_dotenv()

# Lê as configurações do WAHA do arquivo .env.
WAHA_API_URL = os.getenv("WAHA_API_URL", "http://localhost:3000").rstrip("/")
WAHA_SESSION = os.getenv("WAHA_SESSION", "default")
WAHA_API_KEY = os.getenv("WAHA_API_KEY")

app = FastAPI()


def extrair_mensagem(evento):
    # Ignora eventos que não sejam mensagens recebidas para evitar loops.
    if evento.get("event") not in (None, "message", "message.any"):
        return None

    payload = evento.get("payload") or evento
    if payload.get("fromMe") or payload.get("from_me"):
        return None

    texto = payload.get("body") or payload.get("text")
    chat_id = payload.get("from") or payload.get("chatId")
    if not texto or not chat_id:
        return None

    return chat_id, texto


def enviar_mensagem(chat_id, texto):
    url = f"{WAHA_API_URL}/api/sendText"
    body = json.dumps(
        {"chatId": chat_id, "text": texto, "session": WAHA_SESSION}
    ).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if WAHA_API_KEY:
        headers["X-Api-Key"] = WAHA_API_KEY

    request = Request(url, data=body, headers=headers, method="POST")
    with urlopen(request, timeout=30) as response:
        response.read()


@app.post("/webhook")
def receber_webhook(evento: dict):
    mensagem = extrair_mensagem(evento)
    if mensagem is None:
        return {"status": "ignored"}

    chat_id, texto = mensagem
    resposta = responder(texto)
    enviar_mensagem(chat_id, resposta)
    return {"status": "sent"}


if __name__ == "__main__":
    import uvicorn

    # Inicia o servidor que recebe os webhooks do WAHA.
    uvicorn.run("waha:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
