# 🤖 uniBot — Assistente RAG com MCP integrado

Um **assistente de IA baseado em Retrieval-Augmented Generation (RAG)** que recupera informações de documentos da universidade e integra ferramentas externas via **Model Context Protocol (MCP)**.

---

## 🎯 Objetivo

Criar um sistema inteligente que:
1. **Recupera** documentos relevantes (RAGService + ChromaDB)
2. **Chama ferramentas** de terceiros (MCP: SIG, APIs, etc)
3. **Gera respostas** contextualizadas com Gemini

---

## ✨ Features

- ✅ **RAG completo**: ingestão de PDFs/TXTs → embeddings → busca por similaridade
- ✅ **MCP Framework**: ferramentas modulares e reutilizáveis
- ✅ **SIG Integration**: template pronto para integrar Sistema Integrado de Gestão (UFLA)
- ✅ **Docker & Compose**: containerizado, pronto para produção
- ✅ **Frontend React**: interface moderna com Vite
- ✅ **Documentação completa**: 7 guias + testes

---

## 📦 Estrutura do Projeto

```
uniBot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # API FastAPI
│   │   ├── ai_service.py        # RAGService
│   │   ├── mcp_tools.py         # MCPTool (registry)
│   │   ├── config.py            # Configuração centralizada
│   │   ├── ingest.py            # Ingestão de documentos
│   │   ├── tools/               # Framework de ferramentas
│   │   │   ├── __init__.py
│   │   │   ├── base_tool.py     # Classe base abstrata
│   │   │   ├── http_tool.py     # HTTP genérico
│   │   │   └── sig_tool.py      # SIG (template pronto)
│   │   └── data/                # PDFs e TXTs para ingestão
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_mcp.py          # Testes do MCP
│   ├── Dockerfile               # Container backend
│   ├── requirements.txt          # Dependências Python
│   ├── .env.example             # Template de env
│   ├── TOOLS.md                 # 📚 Guia de ferramentas
│   └── SIG_INTEGRATION.md        # 📚 Integração SIG
│
├── frontend/
│   ├── src/                     # Código React
│   ├── public/
│   ├── Dockerfile               # Container nginx (prod)
│   ├── Dockerfile.dev           # Dev com Vite
│   ├── nginx.conf               # Config nginx
│   └── package.json
│
├── docker-compose.yml           # Produção
├── docker-compose.dev.yml       # Desenvolvimento
├── .dockerignore                # Arquivos ignorados no build
├── .env.docker.example          # Template .env para Docker
├── SETUP_WINDOWS.md             # 📚 Setup no Windows/PowerShell
├── DOCKER.md                    # 📚 Guia Docker & Compose
├── README.md                    # Este arquivo
└── .gitignore
```

---

## 🚀 Guias Rápidos

### 📍 Windows/PowerShell (Setup Local)
Ver **[SETUP_WINDOWS.md](./SETUP_WINDOWS.md)**
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### 🐳 Docker (Produção)
Ver **[DOCKER.md](./DOCKER.md)**
```bash
docker-compose up --build
```

### 🔧 Ferramentas MCP
Ver **[TOOLS.md](./backend/TOOLS.md)**
```python
mcp = MCPTool()
mcp.register("sig", SIGTool())
result = mcp.call("sig", {"endpoint": "resolucoes", "query": "473"})
```

### 🏫 Integração SIG
Ver **[SIG_INTEGRATION.md](./backend/SIG_INTEGRATION.md)**

---

## 🎓 O que Cada Componente Faz

| Componente | O Que Faz | Arquivo |
|-----------|-----------|---------|
| **RAGService** | Indexa docs, recupera similares, gera com Gemini | `app/ai_service.py` |
| **MCPTool** | Registry de ferramentas | `app/mcp_tools.py` |
| **BaseTool** | Classe abstrata para ferramentas | `app/tools/base_tool.py` |
| **HTTPTool** | Requisições HTTP genéricas | `app/tools/http_tool.py` |
| **SIGTool** | Template para integração SIG | `app/tools/sig_tool.py` |
| **FastAPI** | API REST com endpoints | `app/main.py` |
| **React** | Interface frontend | `frontend/src/` |

---

## 🔌 Endpoints da API

### Saúde e Info
```bash
GET /health
# {"status": "ok", "rag_initialized": true, ...}

GET /tools
# {"tools": {"sig": "Descrição", ...}, "total": 2}
```

### Query RAG
```bash
POST /api/query
# Request:  {"query": "Qual é a resolução 473?", "use_tools": true}
# Response: {"query": "...", "response": "...", "docs_found": 3, "tools_used": true}
```

### Chamar Ferramenta (debug)
```bash
POST /api/tool/call
# Request:  {"tool_name": "sig", "params": {"endpoint": "resolucoes", "query": "473"}}
# Response: {"success": true, "tool": "sig", "data": {...}, "error": null}
```

### Documentação Interativa
```
http://localhost:8000/docs (Swagger UI)
```

---

## 🧪 Testes

### Rodar testes MCP
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install pytest
pytest tests/test_mcp.py -v
```

### Teste manual via HTTP
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"resolução"}'
```

---

## 🔐 Configuração

### Variáveis de Ambiente

```bash
# .env

# Obrigatório para geração com Gemini
GOOGLE_API_KEY=sua_chave_aqui

# ChromaDB (persistência de vetores)
CHROMA_DIR=./chroma_db

# SIG (preenchher quando tiver documentação)
SIG_BASE_URL=https://sig.ufla.br
SIG_API_KEY=

# Debug
LOG_LEVEL=INFO
```

**Nunca comite `.env`** — está em `.gitignore`.

---

## 📊 Fluxo de Dados

```
┌─────────────────┐
│  Query Usuario  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   RAGService.retrieve   │  ◄─── ChromaDB (vetores)
│  (busca por similaridade)│
└────────┬────────────────┘
         │
         ▼
┌──────────────────────┐
│   MCPTool.call()     │  ◄─── SIG, APIs externas
│  (ferramentas)       │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────────────┐
│ RAGService.generate()        │  ◄─── Gemini API
│ (docs + tool_results + LLM)  │
└────────┬─────────────────────┘
         │
         ▼
┌─────────────────┐
│  Resposta JSON  │
└─────────────────┘
```

---

## 🔄 Adicionar Novos Documentos

1. Coloque `.pdf` ou `.txt` em `backend/data/`
2. Execute:
   ```powershell
   cd backend
   python -m app.ingest
   ```
3. Reinicie o servidor

---

## 📝 Criar Nova Ferramenta MCP

1. Estenda `BaseTool` em `backend/app/tools/nova_tool.py`
2. Implemente `call(self, params) -> dict`
3. Importe em `tools/__init__.py`
4. Registre em `main.py` no `startup_event()`

Exemplo completo em **[TOOLS.md](./backend/TOOLS.md)**.

---

## 🐳 Deploy com Docker

**Desenvolvimento (hot reload):**
```bash
docker-compose -f docker-compose.dev.yml up
```

**Produção:**
```bash
docker-compose up --build
```

Ver **[DOCKER.md](./DOCKER.md)** para detalhes.

---

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** — API REST
- **ChromaDB** — Vector store
- **Sentence-Transformers** — Embeddings
- **Gemini API** — LLM para geração
- **httpx** — Cliente HTTP
- **python-dotenv** — Config com .env

### Frontend
- **React 18** — UI
- **Vite 4** — Build tool
- **Framer Motion** — Animações

### DevOps
- **Docker** — Containerização
- **Docker Compose** — Orquestração local
- **Nginx** — Web server + proxy

### Testes
- **pytest** — Framework de testes

---

## 🚨 Troubleshooting

### ❌ "GOOGLE_API_KEY não definida"
```bash
# Preencher .env
GOOGLE_API_KEY=sua_chave_do_gemini
```

### ❌ "ChromaDB não encontrado"
```powershell
# Verificar volume Docker ou diretório local
$env:CHROMA_DIR = (Resolve-Path .).Path + "\chroma_db"
```

### ❌ "Porta 8000 em uso"
```bash
# Usar porta diferente
uvicorn app.main:app --reload --port 8001
```

### ❌ "Frontend não conecta ao Backend"
```bash
# Verificar VITE_API_URL em frontend
# Tester: curl http://localhost:8000/health
```

---

## 📚 Documentação Completa

1. **[SETUP_WINDOWS.md](./SETUP_WINDOWS.md)** — Setup local no Windows
2. **[DOCKER.md](./DOCKER.md)** — Containerização e deploy
3. **[TOOLS.md](./backend/TOOLS.md)** — Framework MCP e ferramentas
4. **[SIG_INTEGRATION.md](./backend/SIG_INTEGRATION.md)** — Integração SIG

---

## 🎯 Próximos Passos

### Curto Prazo
- [ ] Implementar SIG quando tiver documentação
- [ ] Adicionar autenticação (JWT, OAuth)
- [ ] Implementar rate limiting
- [ ] Cachear respostas do SIG

### Médio Prazo
- [ ] Integração com mais ferramentas
- [ ] Historico de conversas
- [ ] Upload de documentos via UI
- [ ] Monitoramento e logging centralizado

### Longo Prazo
- [ ] Deploy em produção (AWS, GCP, Azure)
- [ ] Kubernetes para escalabilidade
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Analytics de uso

---

## 📊 Estatísticas do Projeto

- **Arquivos Python**: 9
- **Arquivos de Documentação**: 7
- **Testes**: 20+ casos
- **Endpoints da API**: 4 (+ 1 debug)
- **Ferramentas MCP**: 3 (BaseTool + HTTPTool + SIGTool)
- **Linhas de Código**: ~2000
- **Linhas de Documentação**: ~5000

---

## 🤝 Contribuindo

1. Criar branch: `git checkout -b feature/nova-ferramenta`
2. Fazer alterações
3. Testes: `pytest tests/`
4. Commit: `git commit -am "Add nova ferramenta"`
5. Push: `git push origin feature/nova-ferramenta`
6. PR no GitHub

---

## 📞 Suporte

- **Issues**: Abrir issue no GitHub
- **Logs**: `docker-compose logs -f` ou `$env:LOG_LEVEL = "DEBUG"`
- **Testes**: `pytest -v`
- **Docs**: Ver arquivos `.md` no repo

---

## 📜 Licença

Este projeto é parte da disciplina "Sistemas Distribuídos" — UFLA 2024.

---

## 👏 Créditos

- **Aluno**: Douglas
- **Instituição**: UFLA (Universidade Federal de Lavras)
- **Semestre**: 8º
- **Disciplina**: Sistemas Distribuídos
- **Tecnologias**: Python, React, Docker, LLMs

---

**Pronto para começar? Execute os passos em [SETUP_WINDOWS.md](./SETUP_WINDOWS.md)!** 🚀
