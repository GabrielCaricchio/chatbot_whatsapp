import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from chatbot import responder

load_dotenv()

# No Docker, o endereço usa o nome do serviço WAHA definido em compose.yaml.
WAHA_API_URL = os.getenv("WAHA_API_URL", "http://localhost:3000").rstrip("/")
WAHA_SESSION = os.getenv("WAHA_SESSION", "default")
WAHA_API_KEY = os.getenv("WAHA_API_KEY")

app = FastAPI(title="Chatbot WhatsApp")


def extrair_mensagem(evento: dict) -> tuple[str, str] | None:
    """Retorna o identificador e o texto de uma mensagem recebida."""
    if evento.get("event") not in (None, "message", "message.any"):
        return None

    payload = evento.get("payload") or evento
    if not isinstance(payload, dict):
        return None

    # Ignora mensagens enviadas pelo próprio bot para evitar respostas em loop.
    if payload.get("fromMe") or payload.get("from_me"):
        return None

    texto = payload.get("body") or payload.get("text")
    chat_id = payload.get("from") or payload.get("chatId")
    if not isinstance(texto, str) or not texto.strip() or not chat_id:
        return None

    return str(chat_id), texto.strip()


def enviar_mensagem(chat_id: str, texto: str) -> None:
    """Envia uma resposta de texto pela API do WAHA."""
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

    try:
        with urlopen(request, timeout=30) as response:
            response.read()
    except HTTPError as erro:
        raise HTTPException(
            status_code=502,
            detail=f"WAHA respondeu com o erro HTTP {erro.code}.",
        ) from erro
    except URLError as erro:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível conectar à API do WAHA.",
        ) from erro


@app.post("/webhook")
def receber_webhook(evento: dict) -> dict[str, str]:
    """Recebe o evento do WAHA, gera a resposta e a envia ao contato."""
    mensagem = extrair_mensagem(evento)
    if mensagem is None:
        return {"status": "ignored"}

    chat_id, texto = mensagem
    resposta = responder(texto)
    enviar_mensagem(chat_id, resposta)
    return {"status": "sent"}
