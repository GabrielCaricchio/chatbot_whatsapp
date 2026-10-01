# Chatbot para WhatsApp

Bot simples que recebe mensagens pelo WAHA, gera respostas com a API do Groq e envia as respostas de volta ao WhatsApp. O projeto usa Python 3.12.

## Requisitos

- Docker e Docker Compose
- Uma chave de API do Groq
- Uma chave para proteger a API do WAHA

## Configuração

1. Copie `.env.example` para `.env`.
2. Preencha `GROQ_API_KEY` com sua chave do Groq e `WAHA_API_KEY` com uma chave longa e aleatória.
3. Mantenha o arquivo `.env` privado. Ele não deve ser enviado ao Git.

`GROQ_MODEL` é opcional; se não for configurado, o bot usa `openai/gpt-oss-20b`.
No Compose, o endereço interno do WAHA é `http://waha:3000`; não troque `waha` por `localhost` dentro do contêiner.

## Executar

Na pasta do projeto, inicie os serviços:

```bash
docker compose up --build -d
```

Abra [http://localhost:3000](http://localhost:3000), conecte a sessão `default` lendo o QR code do WhatsApp e confirme que a sessão está ativa. O endereço do webhook e o evento `message` já estão configurados no `compose.yaml`.

Se a imagem já estiver criada e você alterar o `.env`, reinicie os serviços para carregar as novas variáveis:

```bash
docker compose up -d
```

O endpoint que recebe os eventos é `POST http://localhost:8000/webhook`. Para conferir os registros:

```bash
docker compose logs -f chatbot
```

Para parar os serviços:

```bash
docker compose down
```

## Como funciona

1. O WAHA envia uma mensagem recebida para `/webhook`.
2. O bot ignora eventos que não sejam mensagens e mensagens enviadas por ele mesmo.
3. A pergunta é enviada ao Groq com instruções para responder em português e de forma adequada para todas as idades.
4. A resposta é enviada ao contato pela API do WAHA.

O bot precisa de acesso à internet para chamar o Groq. Se uma mensagem não gerar resposta, confira as chaves no `.env`, se a sessão do WhatsApp está ativa e os registros dos serviços.

## Segurança

As chaves de API não devem ser publicadas, colocadas no código ou compartilhadas em mensagens. Se uma chave tiver sido exposta, revogue-a no serviço correspondente e gere uma nova.