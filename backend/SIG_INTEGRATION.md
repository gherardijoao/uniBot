# 🏫 Integração com SIG (Sistema Integrado de Gestão)

Guia passo-a-passo para integrar os endpoints do SIG da UFLA no uniBot.

---

## 📍 Pré-requisitos

1. Ter acesso à documentação da API do SIG
2. Conhecer os endpoints disponíveis (URLs e parâmetros)
3. Saber como se autenticar (se necessário)
4. Ter uma chave API ou credenciais (se necessário)

---

## 🔧 Passo 1: Descobrir Endpoints do SIG

**Perguntas a responder:**
- Qual é a URL base? (ex: `https://sig.ufla.br/api/`)
- Quais endpoints existem? (ex: `/usuarios`, `/documentos`, etc)
- Como se autenticar? (token, basic auth, etc)
- Quais parâmetros cada endpoint aceita?
- Qual é o formato de resposta?

**Exemplo hipotético:**
```
GET https://sig.ufla.br/api/resolucoes?q=473
Headers: Authorization: Bearer TOKEN
Response: {"data": [{"id": "473", "titulo": "...", "data": "..."}]}
```

---

## 🔐 Passo 2: Configurar Credenciais

Adicione ao `.env`:

```bash
# .env
SIG_BASE_URL=https://sig.ufla.br
SIG_RESOLUCOES_ENDPOINT=/api/resolucoes
SIG_USUARIOS_ENDPOINT=/api/usuarios
SIG_DOCUMENTOS_ENDPOINT=/api/documentos
SIG_HORARIOS_ENDPOINT=/api/horarios

# Autenticação (conforme necessário)
SIG_API_KEY=sua_chave_aqui
SIG_USERNAME=seu_usuario
SIG_PASSWORD=sua_senha
```

**Nunca comite `.env`** — está em `.gitignore`.

---

## 🛠️ Passo 3: Atualizar `SIGTool`

Abra `backend/app/tools/sig_tool.py` e adapte conforme a API real:

### 3.1 Adicionar Headers de Autenticação

```python
from app.config import SIG_API_KEY, SIG_USERNAME, SIG_PASSWORD

class SIGTool(HTTPTool):
    def __init__(self, base_url: str = "https://sig.ufla.fr", name: str = "sig_tool"):
        super().__init__(base_url=base_url, name=name)
        self.api_key = SIG_API_KEY
        self.username = SIG_USERNAME
        self.password = SIG_PASSWORD

    def _get_auth_headers(self) -> dict:
        """Retorna headers de autenticação conforme configurado."""
        headers = {}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        # Ou basic auth:
        # elif self.username and self.password:
        #     import base64
        #     creds = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        #     headers["Authorization"] = f"Basic {creds}"

        return headers
```

### 3.2 Adaptar métodos conforme a API real

Se a API retorna resultado diferente, adapte:

```python
def call(self, params: Dict[str, Any]) -> Dict[str, Any]:
    endpoint = params.get("endpoint")
    # ... validação ...

    url = self.endpoints[endpoint]
    headers = self._get_auth_headers()
    query_params = {}

    if "query" in params:
        query_params["q"] = params["query"]

    # Adaptar conforme a API real
    # Exemplo: talvez use "search" em vez de "q"
    # query_params["search"] = params.get("query")

    return super().call({
        "method": "GET",
        "url": url,
        "params": query_params,
        "headers": headers,
    })
```

### 3.3 Adicionar métodos específicos (opcional)

```python
def search_resolucoes_cepe(self, numero: str) -> Dict[str, Any]:
    """Buscar Resoluções CEPE por número."""
    return self.call({
        "endpoint": "resolucoes",
        "filters": {"tipo": "CEPE", "numero": numero}
    })

def get_horario_semestre(self, semestre: str, curso: str) -> Dict[str, Any]:
    """Obter horários de um semestre/curso."""
    return self.call({
        "endpoint": "horarios",
        "filters": {"semestre": semestre, "curso": curso}
    })
```

---

## 📝 Passo 4: Testar a Integração

### 4.1 Teste local (sem FastAPI)

```python
# test_sig_integration.py
from app.config import SIG_BASE_URL
from app.tools import SIGTool

# Testar
sig = SIGTool(base_url=SIG_BASE_URL)

# Buscar resoluções
result = sig.search_resolucoes("473")
print(result)
# Esperado: {"success": True, "data": {"status": 200, "body": [...]}, "error": None}

# Buscar usuários
result = sig.search_usuarios("João")
print(result)
```

Execute:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest test_sig_integration.py -v
```

### 4.2 Teste via API HTTP

**1. Iniciar o servidor:**
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**2. Chamar endpoint de teste:**
```bash
curl -X POST http://localhost:8000/api/tool/call \
  -H 'Content-Type: application/json' \
  -d '{
    "tool_name": "sig",
    "params": {
      "endpoint": "resolucoes",
      "query": "473"
    }
  }'
```

Esperado:
```json
{
  "success": true,
  "tool": "sig",
  "data": {
    "status": 200,
    "body": [{"id": "473", "titulo": "..."}]
  },
  "error": null
}
```

### 4.3 Teste via Query RAG

```bash
curl -X POST http://localhost:8000/api/query \
  -H 'Content-Type: application/json' \
  -d '{"query": "Qual é a resolução 473 do CEPE?", "use_tools": true}'
```

---

## 🐛 Troubleshooting

### ❌ "HTTP 401 - Unauthorized"
- Verificar `SIG_API_KEY` ou credenciais em `.env`
- Testar credenciais diretamente (curl, Postman)
- Confirmar formato de autenticação (Bearer vs Basic)

### ❌ "HTTP 404 - Not Found"
- Verificar se o endpoint existe
- Confirmar `SIG_BASE_URL` e caminho do endpoint
- Usar ferramentas como Postman para testar URL

### ❌ "Timeout (30s)"
- SIG está respondendo lentamente
- Aumentar timeout em `.env`:
  ```
  HTTP_TOOL_TIMEOUT=60
  ```

### ❌ "SIGTool retorna empty"
- Verificar se a query é válida
- Testar com Postman/curl primeiro
- Adaptar parser de resposta se formato é diferente

---

## 🔄 Atualizar Endpoints Dinamicamente

Se os endpoints mudarem sem redeployar:

```python
# Em main.py no startup
sig_tool = SIGTool(base_url=config.SIG_BASE_URL)

# Atualizar endpoints conforme necessário
custom_endpoints = {
    "usuarios": "/v2/usuarios",  # versão 2
    "documentos": "/v2/docs",
}
sig_tool.configure_endpoints(custom_endpoints)
mcp.register("sig", sig_tool)
```

---

## 📊 Monitorar Uso

Ativar logs detalhados:

```bash
# PowerShell
$env:LOG_LEVEL = "DEBUG"
```

Ver logs de SIGTool:
```
[2024-06-01 12:34:56] INFO [sig_tool] Consultando resolucoes com query={'q': '473'}
[2024-06-01 12:34:57] INFO [http_tool] Chamando GET https://sig.ufla.br/api/resolucoes?q=473
[2024-06-01 12:34:58] INFO [MCPTool] sig retornou: success=True
```

---

## ✅ Checklist de Integração

- [ ] URL base do SIG conhecida
- [ ] Endpoints documentados
- [ ] Autenticação configurada em `.env`
- [ ] `SIGTool` adaptada conforme API real
- [ ] Testado localmente (Python)
- [ ] Testado via HTTP `/api/tool/call`
- [ ] Testado com Query RAG completa
- [ ] Logs monitorando chamadas
- [ ] Performance aceitável (< 30s)
- [ ] Tratamento de erros funcionando

---

## 🚀 Próximos Passos

1. **Documentar endpoints** — Criar tabela de todos os endpoints
2. **Rate limiting** — Limitar chamadas por minuto
3. **Cache** — Cachear respostas do SIG (ex: 5min)
4. **Monitoramento** — Alertas se SIG está down
5. **Fallback** — Dados em cache se SIG falhar

---

## 📚 Referências

- [HTTPTool docs](TOOLS.md#2-httptool--requisições-http-genéricas)
- [BaseTool docs](TOOLS.md)
- [SIGTool source](./app/tools/sig_tool.py)
- [Config](./app/config.py)

