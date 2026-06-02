# 🔧 Guia de Ferramentas MCP (uniBot)

Este documento explica como usar, criar e registrar novas ferramentas no uniBot.

---

## 📦 O que é MCP?

**Model Context Protocol (MCP)** é um padrão para conectar LLMs com ferramentas externas. No uniBot:
- **RAGService** busca documentos
- **MCPTool** coordena chamadas a ferramentas externas (SIG, APIs, etc)
- **Gemini** gera respostas usando documentos + resultados de ferramentas

---

## 🎯 Ferramentas Disponíveis

### 1. **SIGTool** — Sistema Integrado de Gestão (UFLA)
Consulta dados do SIG da UFLA (usuários, documentos, resoluções, etc).

**Endpoints suportados:**
- `usuarios` — Buscar alunos, professores, servidores
- `documentos` — Buscar documentos no SIG
- `resolucoes` — Buscar resoluções (ex: CEPE nº 473)
- `horarios` — Calendário e horários acadêmicos
- `notas` — Desempenho de alunos
- `disciplinas` — Informações de disciplinas
- `matriculas` — Dados de matrículas

**Exemplo de uso:**
```python
# Já registrada automaticamente no startup
result = mcp.call("sig", {
    "endpoint": "resolucoes",
    "query": "473"
})
```

---

### 2. **HTTPTool** — Requisições HTTP Genéricas
Ferramenta para fazer requisições GET/POST a qualquer API HTTP.

**Uso:**
```python
result = mcp.call("http", {
    "method": "GET",
    "url": "https://api.example.com/data",
    "params": {"q": "termo"}
})
```

---

## 🚀 Como Registrar uma Ferramenta

### Passo 1: Criar a Classe

Estenda `BaseTool`:

```python
# backend/app/tools/minha_ferramenta.py
from .base_tool import BaseTool
from typing import Any, Dict

class MinhaFerramenta(BaseTool):
    def __init__(self):
        super().__init__(
            name="minha_ferramenta",
            description="Descrição do que faz"
        )

    def call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validar parâmetros
        if not self.validate_params(params, required=["chave1"]):
            return self.format_result(
                success=False,
                error="Parâmetro obrigatório: chave1"
            )

        try:
            # Fazer o trabalho
            resultado = "processado"
            return self.format_result(success=True, data=resultado)
        except Exception as e:
            return self.format_result(success=False, error=str(e))
```

### Passo 2: Importar em `tools/__init__.py`

```python
# backend/app/tools/__init__.py
from .minha_ferramenta import MinhaFerramenta

__all__ = ["BaseTool", "HTTPTool", "SIGTool", "MinhaFerramenta"]
```

### Passo 3: Registrar no Startup

```python
# backend/app/main.py - no evento startup_event()

minha_ferramenta = MinhaFerramenta()
mcp.register("minha_ferramenta", minha_ferramenta)
```

---

## 📋 Exemplo Completo: Ferramenta de Cálculo

```python
# backend/app/tools/calc_tool.py
from typing import Any, Dict
from .base_tool import BaseTool
import logging

logger = logging.getLogger(__name__)

class CalculadoraTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="calculadora",
            description="Faz operações matemáticas básicas"
        )

    def call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.validate_params(params, required=["operacao", "a", "b"]):
            return self.format_result(
                success=False,
                error="Parâmetros obrigatórios: operacao, a, b"
            )

        operacao = params["operacao"]
        a = float(params["a"])
        b = float(params["b"])

        try:
            if operacao == "somar":
                resultado = a + b
            elif operacao == "subtrair":
                resultado = a - b
            elif operacao == "multiplicar":
                resultado = a * b
            elif operacao == "dividir":
                if b == 0:
                    return self.format_result(success=False, error="Divisão por zero")
                resultado = a / b
            else:
                return self.format_result(
                    success=False,
                    error=f"Operação desconhecida: {operacao}"
                )

            return self.format_result(
                success=True,
                data={"operacao": operacao, "a": a, "b": b, "resultado": resultado}
            )
        except Exception as e:
            return self.format_result(success=False, error=str(e))
```

**Uso:**
```python
result = mcp.call("calculadora", {
    "operacao": "somar",
    "a": 10,
    "b": 5
})
# {"success": True, "tool": "calculadora", "data": {"resultado": 15}, "error": None}
```

---

## 🔌 Integração com RAGService

A RAGService automaticamente chama ferramentas durante a geração:

```python
@app.post("/api/query")
async def query(req: QueryRequest):
    docs = rag.retrieve(req.query)

    # Chamar ferramenta para complementar (ex: SIG)
    if req.use_tools and mcp is not None:
        tool_result = mcp.call("sig", {
            "endpoint": "resolucoes",
            "query": req.query
        })

    # Gerar passa docs + resultado da ferramenta para Gemini
    resp = rag.generate(req.query, docs, tool_result)
    return {"response": resp, "docs_found": len(docs)}
```

---

## 🛠️ API de Teste

### Listar ferramentas disponíveis
```bash
curl http://localhost:8000/tools
```

Resposta:
```json
{
  "tools": {
    "sig": "Consulta dados do SIG (Sistema Integrado de Gestão) da UFLA",
    "http": "Faz requisições HTTP (GET, POST) para APIs externas"
  },
  "total": 2
}
```

### Chamar ferramenta diretamente (debug)
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

---

## 📊 Formato de Resultado Padrão

Toda ferramenta retorna:

```json
{
  "success": true,
  "tool": "nome_da_ferramenta",
  "data": {...},
  "error": null
}
```

**Campos:**
- `success` (bool): Operação foi bem-sucedida?
- `tool` (str): Nome da ferramenta
- `data` (any): Dados retornados (None se erro)
- `error` (str): Mensagem de erro (None se sucesso)

---

## 🧪 Testando Ferramentas Localmente

```python
from app.mcp_tools import MCPTool
from app.tools import SIGTool, HTTPTool

mcp = MCPTool()
sig = SIGTool()
mcp.register("sig", sig)

# Testar
result = mcp.call("sig", {
    "endpoint": "resolucoes",
    "query": "473"
})
print(result)
```

---

## 🔐 Segurança & Melhores Práticas

1. **Validar sempre** — Use `self.validate_params()`
2. **Logar operações** — Use `logger.info()` e `logger.error()`
3. **Tratar exceções** — Nunca deixar exceções escaparem
4. **Timeouts** — HTTPTool tem timeout padrão de 30s
5. **Credenciais** — Use `.env`, nunca hardcode chaves API

---

## 🐛 Debugging

### Ativar logs detalhados
```bash
# No PowerShell do backend:
$env:LOG_LEVEL = "DEBUG"
```

### Ver logs de uma ferramenta específica
```python
import logging
logging.getLogger("app.tools.sig_tool").setLevel(logging.DEBUG)
```

---

## 📝 Checklist para Nova Ferramenta

- [ ] Estende `BaseTool`
- [ ] Implementa método `call()`
- [ ] Valida parâmetros
- [ ] Trata exceções
- [ ] Usa `self.format_result()` para retorno
- [ ] Importada em `tools/__init__.py`
- [ ] Registrada em `main.py` no startup
- [ ] Documentada aqui

---

## 🎓 Próximos Passos

1. **Implementar SIG**: Ver `SIG_INTEGRATION.md`
2. **Adicionar autenticação**: Bearer token, OAuth, etc
3. **Adicionar cache**: Cachear respostas de ferramentas
4. **Rate limiting**: Limitar chamadas por minuto
5. **Monitoramento**: Logs e métricas de execução

