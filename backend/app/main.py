from fastapi import FastAPI
from pydantic import BaseModel
from .ai_service import RAGService
from .mcp_tools import MCPTool

app = FastAPI(title="uniBot API")

rag = RAGService()
mcp = MCPTool()


class QueryRequest(BaseModel):
    query: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/query")
async def query(req: QueryRequest):
    docs = rag.retrieve(req.query)
    tool_result = mcp.call("example_tool", {"query": req.query})
    resp = rag.generate(req.query, docs, tool_result)
    return {"response": resp, "docs_found": len(docs)}
