# 🤖 uniBot — Setup Completo para Windows/PowerShell

Guia passo-a-passo para configurar e rodar o uniBot no Windows usando PowerShell.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se que tem instalado:
- **Python 3.10+** → Download: https://www.python.org/downloads/
- **Node.js 18+** → Download: https://nodejs.org/
- **Git** → Download: https://git-scm.com/

Verifique no PowerShell:
```powershell
python --version
node --version
npm --version
```

---

## 🔧 Passo 1: Setup do Backend

### 1.1 Abrir PowerShell e navegar para a pasta do backend

```powershell
cd backend
```

### 1.2 Criar e ativar ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Dica**: Se receber erro de política de execução, execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 1.3 Instalar dependências

```powershell
pip install -r requirements.txt
```

### 1.4 Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:
```powershell
Copy-Item .env.example .env
```

Abra o arquivo `.env` com seu editor preferido e preencha:
```
GOOGLE_API_KEY=sua_chave_do_gemini_aqui
CHROMA_DIR=./chroma_db
```

### 1.5 Fazer ingestão dos documentos

```powershell
$env:CHROMA_DIR = (Resolve-Path .).Path + "\chroma_db"
python -m app.ingest
```

Você verá algo como:
```
Ingestão concluída: X documentos adicionados à coleção.
```

### 1.6 Iniciar o servidor FastAPI

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Você verá:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **Backend rodando!** Deixe este PowerShell aberto.

---

## 🎨 Passo 2: Setup do Frontend

### 2.1 Abrir um NOVO PowerShell e navegar para frontend

```powershell
cd frontend
```

### 2.2 Instalar dependências

```powershell
npm install
```

### 2.3 Iniciar o dev server

```powershell
npm run dev
```

Você verá algo como:
```
  VITE v4.0.0  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

✅ **Frontend rodando!** Deixe este PowerShell aberto.

---

## ✅ Passo 3: Testes e Verificação

### 3.1 Abrir um TERCEIRO PowerShell e testar a API

```powershell
# Testar saúde do servidor
curl http://127.0.0.1:8000/health

# Testar query (com documento)
curl -X POST http://127.0.0.1:8000/api/query `
  -H 'Content-Type: application/json' `
  -d '{"query":"resolução"}'
```

Você deverá ver respostas JSON com os documentos recuperados.

### 3.2 Acessar o frontend

Abra seu navegador e vá para:
```
http://localhost:5173/
```

---

## 🌍 Seu Sistema está Pronto!

| Componente | URL | Status |
|-----------|-----|--------|
| **Backend API** | `http://localhost:8000` | ✅ Rodando |
| **Docs Swagger** | `http://localhost:8000/docs` | 📚 Disponível |
| **Frontend** | `http://localhost:5173` | ✅ Rodando |
| **Health Check** | `http://localhost:8000/health` | ✅ OK |

---

## 📁 Estrutura de Pastas

```
uniBot/
├── backend/
│   ├── .venv/              # Ambiente virtual (criado)
│   ├── chroma_db/          # Base de vetores (criada)
│   ├── data/               # PDFs e TXTs para ingestão
│   ├── app/
│   │   ├── main.py         # FastAPI app
│   │   ├── ai_service.py   # RAGService
│   │   ├── ingest.py       # Ingestão de docs
│   │   └── mcp_tools.py    # Ferramentas MCP
│   ├── .env                # Configuração (criar)
│   ├── .env.example        # Template
│   └── requirements.txt     # Dependências
│
├── frontend/
│   ├── node_modules/       # Dependências (criadas)
│   ├── src/                # Código React
│   └── package.json        # Scripts e dependências
```

---

## 🚀 Próximas Vezes

Para reabrir o projeto:

**Terminal 1 (Backend):**
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```powershell
cd frontend
npm run dev
```

---

## 🔑 Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `GOOGLE_API_KEY` | *(vazio)* | Chave de API do Gemini (obrigatória para geração) |
| `CHROMA_DIR` | `./chroma_db` | Diretório persistente dos vetores |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Modelo de embeddings (HuggingFace) |

---

## 🆘 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'X'"
```powershell
pip install -r requirements.txt
```

### ❌ "A variável CHROMA_DIR não está definida"
No backend, execute:
```powershell
$env:CHROMA_DIR = (Resolve-Path .).Path + "\chroma_db"
```

### ❌ "Erro de política de execução no PowerShell"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ "Porta 8000 já em uso"
Mude a porta:
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### ❌ "API retorna 0 documentos"
1. Verifique que `CHROMA_DIR` é o mesmo no `ingest` e no servidor
2. Reinicie o servidor após ingestão
3. Confirme que arquivos existem em `backend/data/`

---

## 📚 Adicionar Novos Documentos

1. Coloque arquivos `.txt` ou `.pdf` em `backend/data/`
2. Execute no PowerShell do backend:
   ```powershell
   python -m app.ingest
   ```
3. Reinicie o servidor FastAPI

---

## 🎯 Endpoints Disponíveis

### `GET /health`
Verifica saúde do servidor.

**Resposta:**
```json
{ "status": "ok" }
```

---

### `POST /api/query`
Faz query RAG (recupera docs + gera resposta).

**Request:**
```json
{
  "query": "Qual é a resolução sobre..."
}
```

**Resposta:**
```json
{
  "response": "Resposta gerada pelo Gemini...",
  "docs_found": 3
}
```

---

### `GET /docs`
Documentação interativa Swagger da API.

Acesse em: `http://localhost:8000/docs`

---

## 📝 Notas Finais

- A pasta `chroma_db` é gerada automaticamente e está em `.gitignore` (cada dev tem sua própria)
- A `GOOGLE_API_KEY` **não deve ser commitada** — está em `.env` e `.env` está em `.gitignore`
- O modelo de embeddings `all-MiniLM-L6-v2` é baixado automaticamente na primeira execução
- Para debug, abra `http://localhost:8000/docs` para testar endpoints

---

**Pronto para começar? Execute os passos acima e deixe duas abas do PowerShell rodando (backend + frontend)!** 🚀
