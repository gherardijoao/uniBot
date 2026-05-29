import os
from typing import List, Optional
import uuid
import os
import json

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import httpx


class RAGService:
    """Serviço RAG simples usando ChromaDB para recuperação e
    `sentence-transformers` para embeddings.

    Observações:
    - Configure `CHROMA_DIR` para persistência (padrão: ./chroma_db)
    """

    def __init__(self, collection_name: str = "unibot_docs"):
        persist_dir = os.getenv("CHROMA_DIR", os.path.join(os.path.dirname(__file__), "..", "chroma_db"))
        # Use the current Chroma client Settings API for persistence
        try:
            settings = Settings(persist_directory=persist_dir, is_persistent=True)
            self.client = chromadb.Client(settings)
        except Exception:
            try:
                # Fallback to default client (may be in-memory depending on install)
                self.client = chromadb.Client()
            except Exception:
                self.client = None

        self.collection = None
        if self.client is not None:
            try:
                # Prefer get_or_create_collection where available
                if hasattr(self.client, 'get_or_create_collection'):
                    self.collection = self.client.get_or_create_collection(collection_name)
                else:
                    try:
                        self.collection = self.client.get_collection(collection_name)
                    except Exception:
                        self.collection = self.client.create_collection(name=collection_name)
            except Exception:
                self.collection = None

        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.embedder = SentenceTransformer(model_name)

    def ingest_documents(self, docs: List[str], metadatas: Optional[List[dict]] = None):
        ids = [str(uuid.uuid4()) for _ in docs]
        embeddings = self.embedder.encode(docs, show_progress_bar=False)
        # sentence-transformers retorna numpy arrays; convertemos para listas
        embeddings = [e.tolist() for e in embeddings]
        self.collection.add(documents=docs, metadatas=(metadatas or [{} for _ in docs]), ids=ids, embeddings=embeddings)

    def retrieve(self, query: str, n_results: int = 3) -> List[str]:
        q_emb = self.embedder.encode([query], show_progress_bar=False)[0].tolist()
        result = self.collection.query(query_embeddings=[q_emb], n_results=n_results, include=["documents", "metadatas", "distances"])
        docs = []
        if result and "documents" in result:
            docs = result["documents"][0]
        return docs

    def generate(self, query: str, docs: List[str], tool_result: Optional[dict] = None) -> str:
        # Monta um prompt simples combinando documentos recuperados e resultado da ferramenta
        docs_text = "\n\n---\n\n".join(docs) if docs else ""
        tool_text = json.dumps(tool_result, ensure_ascii=False, indent=2) if tool_result else ""
        prompt = (
            "Você é o uniBot, um assistente que responde com base em documentos fornecidos. "
            "Use apenas as informações dos documentos e, se necessário, os resultados da ferramenta. "
            "Se não souber a resposta, admita que não sabe.\n\n"
            f"Documentos:\n{docs_text}\n\n"
            f"Resultado da ferramenta:\n{tool_text}\n\n"
            f"Pergunta do usuário: {query}\n\nResposta:" 
        )

        # Tentar usar a API do Gemini via Generative Language API se a chave estiver definida
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "Resposta gerada (placeholder) baseada nos documentos e na ferramenta. (GOOGLE_API_KEY não definido)"

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": api_key,
        }
        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()

            # Extrair texto de resposta de forma robusta
            # A API de GGL pode retornar em diferentes campos; tentamos alguns caminhos comuns
            text = None
            # caminho provável: 'candidates' -> list of { 'output': '...' } or { 'content': ... }
            candidates = data.get("candidates") or []
            if candidates:
                first = candidates[0]
                # checar chaves possíveis
                text = first.get("output") or first.get("content") or first.get("text") or first.get("message")
                # Se o campo for um dict com 'parts', extrair os textos
                if isinstance(text, dict):
                    if "parts" in text and isinstance(text["parts"], list):
                        parts = []
                        for p in text["parts"]:
                            if isinstance(p, dict) and isinstance(p.get("text"), str):
                                parts.append(p.get("text"))
                        text = "\n".join(parts) if parts else None
                    else:
                        # procurar por campos de texto dentro do dict
                        for k in ("text", "output", "content"):
                            if k in text and isinstance(text[k], str):
                                text = text[k]
                                break

            # fallback genérico: procurar por qualquer string profundo
            if not text:
                # alguns retornos contém 'candidates' -> [{'message':{'content':[...parts...]}}]
                try:
                    # Procura recursiva por primeiras strings
                    def find_first_str(obj):
                        if isinstance(obj, str):
                            return obj
                        if isinstance(obj, dict):
                            for v in obj.values():
                                res = find_first_str(v)
                                if res:
                                    return res
                        if isinstance(obj, list):
                            for it in obj:
                                res = find_first_str(it)
                                if res:
                                    return res
                        return None
                    text = find_first_str(data)
                except Exception:
                    text = None

            if not text:
                return "Resposta gerada (placeholder): não foi possível extrair texto da resposta do Gemini."

            return text
        except httpx.HTTPStatusError as e:
            return f"Erro na chamada ao Gemini: {e.response.status_code} {e.response.text}"
        except Exception as e:
            return f"Erro ao chamar Gemini: {str(e)}"
