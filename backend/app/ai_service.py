class RAGService:
    def __init__(self):
        # TODO: inicializar Chroma, embeddings e LangChain aqui
        pass

    def retrieve(self, query: str):
        # TODO: implementar busca vetorial com Chroma
        # Placeholder: retorna lista de textos
        return ["Documento exemplo: conteúdo relacionado a '" + query + "'"]

    def generate(self, query: str, docs, tool_result=None):
        # TODO: chamar modelo generativo (ex: Gemini) via LangChain
        prompt = f"""Usando documentos:\n{docs}\n\nFerramenta: {tool_result}\n\nPergunta: {query}\nResposta:"""
        return "Resposta gerada (placeholder) baseada nos documentos e na ferramenta." 
