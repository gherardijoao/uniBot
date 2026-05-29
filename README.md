uniBot — Guia rápido 
Bem-vindo ao uniBot — um protótipo de assistente RAG que recupera informação de documentos da universidade.

Visão geral (simples)
- Backend: API em FastAPI dentro de `backend/`. Endpoints principais: `/health` e `/api/query`.
- RAGService: código em `backend/app/ai_service.py` faz ingestão, indexação (Chroma) e busca por similaridade.
- Frontend: app React + Vite em `frontend/` (cliente mínimo que consulta a API).

O que já está funcionando
- Ingestão de documentos (`.txt` e `.pdf`) em `backend/data/` via `backend/app/ingest.py`.
- Indexação persistente usando ChromaDB (configure `CHROMA_DIR` para a pasta local de vetores).
- Geração: `RAGService.generate()` está integrado com Gemini; defina `GOOGLE_API_KEY` para habilitar geração via LLM.
 - O documento `resolução_CEPE_473.pdf` (Resolução CEPE nº 473) já está em `backend/data/` e foi indexado.


Passo a passo rápido (direto)

1) Backend — execute cada linha abaixo na ordem:

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export CHROMA_DIR=$(pwd)/chroma_db
CHROMA_DIR=$CHROMA_DIR python -m app.ingest
./.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2) Frontend — em outra janela:

```bash
cd frontend
npm install
npm run dev
```

3) Verificar (em outra janela):

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/api/query -H 'Content-Type: application/json' -d '{"query":"resolução"}'
```

Nota rápida:
- Cada dev cria seu `chroma_db` local (por isso está em `.gitignore`).
- Se a API devolver 0 documentos: garanta que o `CHROMA_DIR` usado no `ingest` e no servidor é o mesmo e reinicie o servidor.

Como configurar o Gemini (opcional)
- Para habilitar geração com Gemini, defina a variável de ambiente `GOOGLE_API_KEY` com sua chave de API (NÃO comite essa chave):

```bash
export GOOGLE_API_KEY="sua_chave_aqui"
```

O `RAGService.generate()` usará essa chave para chamar a API do Gemini. Se a variável não estiver definida, a geração ficará desabilitada e o serviço retornará uma mensagem informativa solicitando a configuração da chave.

Usando `.env` para desenvolvimento
- Você pode copiar o exemplo para criar o arquivo real:

```bash
cd backend
cp .env.example .env
```

- Depois preencha `backend/.env` com as variáveis abaixo:

```text
GOOGLE_API_KEY=Sua_Chave_Gemini
CHROMA_DIR=./chroma_db
```

O backend foi atualizado para carregar automaticamente `backend/.env` via `python-dotenv` na inicialização.


