from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from logging.config import dictConfig

# Carregar .env automaticamente (se existir)
from dotenv import load_dotenv
load_dotenv()

from . import config
from .ai_service import RAGService
from .mcp_tools import MCPTool
from .tools import SIGTool, HTTPTool, RUTool

# Configurar logging
dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI(title="uniBot API", description="Assistente RAG com integração MCP e SIG")

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, use ["http://localhost:5173", "seu-dominio.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Validar configuração na inicialização
config.validate_config()

# Instâncias serão inicializadas no evento de startup para evitar executar
# lógica pesada/risco de falha no momento da importação do módulo.
rag: RAGService | None = None
mcp: MCPTool | None = None


class QueryRequest(BaseModel):
    query: str
    use_tools: bool = True


@app.on_event("startup")
async def startup_event():
    global rag, mcp
    logger.info("🚀 Iniciando uniBot Backend...")

    # Inicializar RAGService
    rag = RAGService()
    logger.info("✅ RAGService inicializado")

    # Inicializar MCPTool e registrar ferramentas
    mcp = MCPTool()

    # Registrar SIGTool
    try:
        sig_tool = SIGTool(base_url=config.SIG_BASE_URL)
        if config.SIG_ENDPOINTS:
            sig_tool.configure_endpoints(config.SIG_ENDPOINTS)
        mcp.register("sig", sig_tool)
        logger.info(f"✅ SIGTool registrada em {config.SIG_BASE_URL}")
    except Exception as e:
        logger.error(f"❌ Erro ao registrar SIGTool: {e}")

    # Registrar HTTPTool genérica
    try:
        http_tool = HTTPTool(name="http")
        mcp.register("http", http_tool)
        logger.info("✅ HTTPTool genérica registrada")
    except Exception as e:
        logger.error(f"❌ Erro ao registrar HTTPTool: {e}")

    # Registrar RUTool
    try:
        ru_tool = RUTool()
        mcp.register("ru", ru_tool)
        logger.info("✅ RUTool registrada")
    except Exception as e:
        logger.error(f"❌ Erro ao registrar RUTool: {e}")

    logger.info(f"🎯 Ferramentas disponíveis: {list(mcp.list_tools().keys())}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Encerrando uniBot Backend...")


@app.get("/health")
async def health():
    """Verificar saúde do servidor."""
    return {
        "status": "ok",
        "rag_initialized": rag is not None,
        "mcp_initialized": mcp is not None,
        "tools_available": list(mcp.list_tools().keys()) if mcp else []
    }


@app.get("/tools")
async def list_tools():
    """Listar ferramentas MCP disponíveis."""
    if mcp is None:
        return {"error": "MCP service not initialized"}
    return {
        "tools": mcp.list_tools(),
        "total": len(mcp.list_tools())
    }


@app.post("/api/query")
async def query(req: QueryRequest):
    """
    Faz uma query RAG com recuperação de documentos e geração.
    Opcionalmente chama ferramentas MCP.
    """
    if rag is None:
        return {"error": "RAG service not initialized"}

    logger.info(f"📤 Query recebida: {req.query}")

    # Recuperar documentos
    docs = rag.retrieve(req.query)
    logger.info(f"📚 {len(docs)} documentos recuperados")

    # Opcionalmente chamar ferramentas MCP
    tool_result = None
    if req.use_tools and mcp is not None:
        try:
            query_lower = req.query.lower()
            
            # Decidir qual ferramenta chamar
            if any(word in query_lower for word in ["cardapio", "cardápio", "ru", "almoço", "jantar", "refeição", "comida", "restaurante", "saldo", "crédito"]):
                action = "saldo" if any(word in query_lower for word in ["saldo", "crédito", "extrato"]) else "cardapio"
                raw_result = mcp.call("ru", {"action": action})
                tool_result = raw_result
                logger.info(f"🔧 Ferramenta RU chamada (action={action}): success={raw_result.get('success')}")
            else:
                # Fallback para SIG/Dados Abertos
                raw_result = mcp.call("sig", {
                    "endpoint": "resolucoes",
                    "query": req.query
                })
                
                # Simplificar o resultado para o Gemini não se perder no JSON gigante do CKAN
                if raw_result.get("success") and isinstance(raw_result.get("data"), dict):
                    body = raw_result["data"].get("body", {})
                    if isinstance(body, dict) and "result" in body:
                        results = body["result"].get("results", [])
                        # Pegar apenas títulos e notas dos primeiros 5 datasets
                        simplified = [
                            {"titulo": r.get("title"), "notas": r.get("notes")[:200] + "..." if r.get("notes") else ""}
                            for r in results[:5]
                        ]
                        tool_result = {
                            "success": True,
                            "source": "Portal de Dados Abertos UFLA",
                            "datasets_encontrados": simplified
                        }
                
                if not tool_result:
                    tool_result = raw_result

                logger.info(f"🔧 Ferramenta SIG chamada: success={raw_result.get('success')}")
        except Exception as e:
            logger.error(f"⚠️  Erro ao chamar ferramenta: {e}")
            tool_result = None

    # Gerar resposta com Gemini
    resp = rag.generate(req.query, docs, tool_result)

    return {
        "query": req.query,
        "response": resp,
        "docs_found": len(docs),
        "tools_used": tool_result is not None and tool_result.get("success", False)
    }


@app.post("/api/tool/call")
async def call_tool(tool_name: str, params: dict):
    """
    Chamar uma ferramenta MCP diretamente (debug/teste).
    """
    if mcp is None:
        return {"error": "MCP service not initialized"}

    logger.info(f"🔧 Chamada direta de ferramenta: {tool_name}")
    result = mcp.call(tool_name, params)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
