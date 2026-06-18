# uniBot

Assistente RAG com MCP: recupera documentos, orquestra ferramentas externas e gera respostas contextualizadas com IA.

## Fluxo de usuario

```
Usuario digita pergunta
    |
    v
RAG recupera documentos similares (ChromaDB)
    |
    v
MCP aciona ferramentas externas (SIG, RU, HTTP)
    |
    v
Gemini sintetiza resposta com contexto (docs + dados)
    |
    v
Frontend exibe resposta formatada
```

## Como interagem

| Componente | Faz o que | Interage com |
|-----------|-----------|--------------|
| Frontend | Captura pergunta, exibe resposta | Backend /api/query |
| RAGService | Busca documentos por similaridade | ChromaDB, Gemini |
| MCPTool | Registry e roteia chamadas de ferramentas | SIGTool, RUTool, HTTPTool |
| RUTool | Cardapio e saldo RU | APIs UFLA |
| HTTPTool | Chamadas HTTP genericas | APIs externas |
| ChromaDB | Vetores de documentos | RAGService |
| Gemini | Gera texto contextualizado | RAGService |

## Decisao de ferramentas

O backend detecta automaticamente:

- "cardapio", "ru", "almoço" → aciona **RUTool**
- Caso contrario → usa apenas **docs**

Cada ferramenta enriquece o prompt que vai para Gemini.

## Ingestao de documentos

```bash
# 1. Coloque PDFs/TXTs em backend/data/
# 2. Reindexe
cd backend
python -m app.ingest
# 3. Reinicie backend
```

Documentos viram embeddings armazenados em ChromaDB para recuperacao semantica.

## Executar

### Docker (recomendado)

```bash
docker compose up --build
# Frontend: http://localhost
# Backend: http://localhost:8000
# Swagger: http://localhost:8000/docs
```

### Local

Backend:
```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend && npm install && npm run dev -- --port 5173
```

## Configuracao (.env)

```bash
GOOGLE_API_KEY=chave_gemini
CHROMA_DIR=./chroma_db
```

## API

POST /api/query:
```bash
curl -X POST http://localhost:8000/api/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"Qual e o cardapio?","use_tools":true}'
```

GET /health, /tools - verificar status e ferramentas disponiveis.

## Criar ferramenta MCP

1. Estenda `BaseTool` em `backend/app/tools/`
2. Implemente `call(self, params)`
3. Registre em `backend/app/main.py`

Veja [backend/TOOLS.md](backend/TOOLS.md).

## Documentacao

- [DOCKER.md](./DOCKER.md) - Setup Docker
- [SETUP_WINDOWS.md](./SETUP_WINDOWS.md) - Setup Windows
- [backend/TOOLS.md](./backend/TOOLS.md) - Framework MCP

## Stack

Backend: FastAPI, ChromaDB, Sentence-Transformers, Gemini, httpx

Frontend: React 18, Vite, Framer Motion

Infraestrutura: Docker, Nginx

UFLA 2026 Sistemas Distribuidos