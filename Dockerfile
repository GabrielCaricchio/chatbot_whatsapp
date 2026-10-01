# Usa a versão de Python solicitada pelo projeto.
FROM python:3.12-slim

# Evita arquivos .pyc e envia logs diretamente para o Docker.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala apenas as dependências declaradas pelo projeto.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os dois módulos da aplicação para a imagem.
COPY chatbot.py waha.py ./

# Porta usada pela API que recebe os webhooks do WAHA.
EXPOSE 8000

# Inicia a API do webhook quando o contêiner sobe.
CMD ["uvicorn", "waha:app", "--host", "0.0.0.0", "--port", "8000"]