# uniBot

uniBot e uma aplicacao full-stack para consulta assistida a documentos institucionais com recuperacao semantica, chamadas a ferramentas externas via MCP e geracao de resposta com Gemini.

## Visao geral

O sistema combina quatro blocos principais:

1. Ingestao de documentos em PDF e TXT.
2. Indexacao vetorial em ChromaDB.
3. Orquestracao de ferramentas MCP para SIG, HTTP generico e RU.
4. Geracao de resposta contextualizada pela camada RAG.

O backend expoe uma API FastAPI e o frontend fornece a interface web para consulta e exibicao das respostas.

## Arquitetura

Fluxo de processamento da requisicao:

```text
Usuario -> /api/query -> RAGService.retrieve() -> [MCPTool.call()] -> RAGService.generate() -> resposta JSON
```

Durante o startup, o backend inicializa o servico de RAG e registra as ferramentas disponiveis no registry MCP. A decisao de acionar ferramenta e feita com base no conteudo da pergunta.

## Componentes principais

| Componente | Responsabilidade | Arquivo |
|-----------|------------------|---------|
| FastAPI | Inicializacao do servidor, rotas e CORS | [backend/app/main.py](backend/app/main.py) |
| RAGService | Recuperacao de documentos e geracao com Gemini | [backend/app/ai_service.py](backend/app/ai_service.py) |
| MCPTool | Registry e despacho de ferramentas | [backend/app/mcp_tools.py](backend/app/mcp_tools.py) |
| BaseTool | Contrato base para ferramentas | [backend/app/tools/base_tool.py](backend/app/tools/base_tool.py) |
| HTTPTool | Integracoes HTTP genericas | [backend/app/tools/http_tool.py](backend/app/tools/http_tool.py) |
| SIGTool | Integracao com o portal SIG/dados abertos | [backend/app/tools/sig_tool.py](backend/app/tools/sig_tool.py) |
| RUTool | Acesso a consultas relacionadas ao RU | [backend/app/tools/ru_tool.py](backend/app/tools/ru_tool.py) |
| Ingestao | Processamento e indexacao de documentos | [backend/app/ingest.py](backend/app/ingest.py) |
| Frontend | Interface React com Vite | [frontend/src/App.jsx](frontend/src/App.jsx) |

## Requisitos

- Python 3.11
- Node.js 18
- Docker e Docker Compose, se for usar containerizacao
- Chave valida para Gemini em `GOOGLE_API_KEY`

## Configuracao de ambiente

O backend carrega variaveis do arquivo `.env` quando presente. As principais configuracoes sao:

```bash
GOOGLE_API_KEY=chave_gemini
CHROMA_DIR=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
GEMINI_MODEL=gemini-flash-latest
SIG_BASE_URL=https://dados.ufla.br
SIG_API_KEY=
SIG_USERNAME=
SIG_PASSWORD=
HTTP_TOOL_TIMEOUT=30
LOG_LEVEL=INFO
DEBUG=False
```

Endpoints publicos do SIG podem ser sobrescritos por variaveis como `SIG_RESOLUCOES_ENDPOINT`, `SIG_HORARIOS_ENDPOINT` e similares. Consulte [backend/app/config.py](backend/app/config.py) para a lista completa.

## Execucao local

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Servico disponivel em `http://localhost:8000`.

Documentacao interativa:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Para build de producao:

```bash
cd frontend
npm run build
```

## Docker

### Desenvolvimento

```bash
docker-compose -f docker-compose.dev.yml up --build
```

Portas expostas:

- Backend: `8000`
- Frontend: `5173`

### Producao

```bash
docker-compose up --build
```

Portas expostas:

- Backend: `8000`
- Frontend: `80`

As definicoes completas estao em [DOCKER.md](./DOCKER.md).

## API

### Saude e inventario

```bash
GET /health
GET /tools
```

Resposta de `GET /health`:

```json
{
  "status": "ok",
  "rag_initialized": true,
  "mcp_initialized": true,
  "tools_available": ["sig", "http", "ru"]
}
```

Resposta de `GET /tools`:

```json
{
  "tools": {
    "sig": "...",
    "http": "...",
    "ru": "..."
  },
  "total": 3
}
```

### Consulta principal

```bash
POST /api/query
```

Exemplo de payload:

```json
{
  "query": "Qual e a resolucao 473?",
  "use_tools": true
}
```

Exemplo de resposta:

```json
{
  "query": "Qual e a resolucao 473?",
  "response": "...",
  "docs_found": 3,
  "tools_used": true
}
```

### Chamada direta de ferramenta

```bash
POST /api/tool/call
```

Este endpoint e util para depuracao e validacao manual de ferramentas MCP.

## Ingestao de documentos

Arquivos PDF e TXT devem ser colocados em [backend/data](backend/data).

Para reindexar o conteudo:

```bash
cd backend
python -m app.ingest
```

Depois da ingestao, reinicie o backend para carregar o novo indice vetorial.

## Ferramentas MCP

As ferramentas registradas no startup do backend sao:

- `sig`: consultas ao portal SIG/dados abertos da UFLA.
- `http`: chamadas HTTP genericas para integracoes futuras.
- `ru`: consultas relacionadas ao restaurante universitario.

Para criar uma nova ferramenta:

1. Estenda `BaseTool`.
2. Implemente `call(self, params) -> dict`.
3. Registre a ferramenta em [backend/app/main.py](backend/app/main.py) durante o startup.
4. Atualize [backend/app/tools/__init__.py](backend/app/tools/__init__.py) se necessario.

Detalhes adicionais estao em [backend/TOOLS.md](backend/TOOLS.md).

## Testes

### Backend

```bash
cd backend
pip install pytest
pytest tests/test_mcp.py -v
```

### Verificacao manual

```bash
curl http://localhost:8000/health
curl http://localhost:8000/tools
```

## Estrutura do repositorio

```text
.
|-- backend/
|   |-- app/
|   |-- data/
|   |-- tests/
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- TOOLS.md
|   `-- SIG_INTEGRATION.md
|-- frontend/
|   |-- src/
|   |-- public/
|   |-- Dockerfile
|   |-- Dockerfile.dev
|   |-- nginx.conf
|   `-- package.json
|-- docker-compose.yml
|-- docker-compose.dev.yml
|-- DOCKER.md
|-- SETUP_WINDOWS.md
`-- README.md
```

## Tecnologias

### Backend

- FastAPI
- ChromaDB
- Sentence-Transformers
- Gemini API
- httpx
- python-dotenv

### Frontend

- React 18
- Vite
- Framer Motion
- react-markdown
- remark-gfm

### Infraestrutura

- Docker
- Docker Compose
- Nginx

### Testes

- pytest

## Solucao de problemas

### `GOOGLE_API_KEY` ausente

Defina a variavel no arquivo `.env` antes de iniciar o backend.

### Erro de caminho do ChromaDB

Verifique se `CHROMA_DIR` aponta para um diretorio existente e gravavel.

### Porta 8000 ou 5173 ocupada

Altere a porta no comando de inicializacao ou encerre o processo que esta usando a porta.

### Frontend nao acessa o backend

Confirme se o backend esta ativo em `http://localhost:8000` e se o frontend foi iniciado com a URL correta da API.

## Documentacao complementar

1. [SETUP_WINDOWS.md](./SETUP_WINDOWS.md) - execucao local no Windows.
2. [DOCKER.md](./DOCKER.md) - ambiente com Docker e Docker Compose.
3. [backend/TOOLS.md](./backend/TOOLS.md) - especificacao do framework MCP.
4. [backend/SIG_INTEGRATION.md](./backend/SIG_INTEGRATION.md) - integracao com SIG.

## Contribuicao

Fluxo recomendado:

1. Criar uma branch de trabalho.
2. Implementar a mudanca.
3. Executar os testes relevantes.
4. Revisar o diff.
5. Abrir um pull request.

## Licenca

Projeto desenvolvido para a disciplina de Sistemas Distribuidos na UFLA.