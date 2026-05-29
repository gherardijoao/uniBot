from fastapi import FastAPI
from pydantic import BaseModel
from .ai_service import RAGService
from .mcp_tools import MCPTool

app = FastAPI(title="uniBot API")

# Instâncias serão inicializadas no evento de startup para evitar executar
# lógica pesada/risco de falha no momento da importação do módulo.
rag: RAGService | None = None
mcp: MCPTool | None = None


class QueryRequest(BaseModel):
    query: str


@app.on_event("startup")
async def startup_event():
    global rag, mcp
    rag = RAGService()
    mcp = MCPTool()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/query")
async def query(req: QueryRequest):
    if rag is None:
        return {"error": "RAG service not initialized"}
    docs = rag.retrieve(req.query)
    tool_result = mcp.call("example_tool", {"query": req.query}) if mcp is not None else None
    resp = rag.generate(req.query, docs, tool_result)
    return {"response": resp, "docs_found": len(docs)}
