import os
from typing import List, Optional
import uuid

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class RAGService:
    """Serviço RAG simples usando ChromaDB para recuperação e
    `sentence-transformers` para embeddings.

    Observações:
    - Configure `CHROMA_DIR` para persistência (padrão: ./chroma_db)
    - O método `generate` é um placeholder; aqui deve-se integrar o LLM (ex.: Gemini)
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
        prompt = f"""Documentos relevantes:\n{docs}\n\nFerramenta:\n{tool_result}\n\nPergunta: {query}\nResposta:"""
        # TODO: integrar LangChain + Gemini aqui para geração baseada nos documentos
        return "Resposta gerada (placeholder) baseada nos documentos e na ferramenta."
