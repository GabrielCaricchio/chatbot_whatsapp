import os

from langchain_groq import ChatGroq

# Estas instruções definem o idioma, o tom e os assuntos que o bot evita.
INSTRUCOES = """Você é um assistente pessoal que conversa em português do Brasil.
Responda de forma clara, educada e adequada para todas as idades.
Se pedirem conteúdo sexual explícito, assuntos relacionados a política ou religião,
instruções para violência ou atividades perigosas ou ilegais, não dê detalhes.
Responda apenas: "Não sei responder a isso."""


def responder(pergunta: str) -> str:
    # Lê a chave do ambiente para não gravá-la no código.
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Configure GROQ_API_KEY no arquivo .env.")

    # Cria o modelo e envia as instruções junto com a pergunta.
    modelo = ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        api_key=api_key,
    )
    resposta = modelo.invoke(
        [
            ("system", INSTRUCOES),
            ("human", pergunta),
        ]
    )
    return str(resposta.content).strip()
