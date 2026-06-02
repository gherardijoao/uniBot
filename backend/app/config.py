"""
Configuração centralizada do backend.
Gerencia variáveis de ambiente, URLs de APIs externas, e configurações de ferramentas.
"""

import os
from dotenv import load_dotenv

# Carregar .env se existir
load_dotenv()


# ============================================================================
# Configurações Gerais
# ============================================================================

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# ============================================================================
# ChromaDB - Persistência de Vetores
# ============================================================================

CHROMA_DIR = os.getenv("CHROMA_DIR", os.path.join(os.path.dirname(__file__), "..", "chroma_db"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


# ============================================================================
# Gemini API - Geração de Respostas
# ============================================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")


# ============================================================================
# SIG (Sistema Integrado de Gestão) da UFLA
# ============================================================================

SIG_BASE_URL = os.getenv("SIG_BASE_URL", "https://sig.ufla.br")

# Endpoints do SIG (usar template em sig_tool.py até ter documentação real)
SIG_ENDPOINTS = {
    "usuarios": os.getenv("SIG_USUARIOS_ENDPOINT", "/api/usuarios"),
    "documentos": os.getenv("SIG_DOCUMENTOS_ENDPOINT", "/api/documentos"),
    "resolucoes": os.getenv("SIG_RESOLUCOES_ENDPOINT", "/api/resolucoes"),
    "horarios": os.getenv("SIG_HORARIOS_ENDPOINT", "/api/horarios"),
    "notas": os.getenv("SIG_NOTAS_ENDPOINT", "/api/notas"),
    "disciplinas": os.getenv("SIG_DISCIPLINAS_ENDPOINT", "/api/disciplinas"),
    "matriculas": os.getenv("SIG_MATRICULAS_ENDPOINT", "/api/matriculas"),
}

# Autenticação SIG (se necessário)
SIG_USERNAME = os.getenv("SIG_USERNAME", "")
SIG_PASSWORD = os.getenv("SIG_PASSWORD", "")
SIG_API_KEY = os.getenv("SIG_API_KEY", "")


# ============================================================================
# HTTPTool - Chamadas HTTP Genéricas
# ============================================================================

HTTP_TOOL_TIMEOUT = int(os.getenv("HTTP_TOOL_TIMEOUT", "30"))


# ============================================================================
# Logging
# ============================================================================

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
    },
    "handlers": {
        "default": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["default"]
    }
}


# ============================================================================
# Validações
# ============================================================================

def validate_config():
    """Valida se configurações essenciais estão presentes."""
    issues = []

    if not CHROMA_DIR:
        issues.append("CHROMA_DIR não configurada")

    if not GOOGLE_API_KEY:
        print("⚠️  AVISO: GOOGLE_API_KEY não definida. Geração com Gemini desabilitada.")

    if issues:
        print("❌ Problemas na configuração:")
        for issue in issues:
            print(f"  - {issue}")
        return False

    return True


if __name__ == "__main__":
    print("✅ Configuração do uniBot Backend")
    print(f"  DEBUG: {DEBUG}")
    print(f"  LOG_LEVEL: {LOG_LEVEL}")
    print(f"  CHROMA_DIR: {CHROMA_DIR}")
    print(f"  EMBEDDING_MODEL: {EMBEDDING_MODEL}")
    print(f"  GEMINI_MODEL: {GEMINI_MODEL}")
    print(f"  SIG_BASE_URL: {SIG_BASE_URL}")
    print(f"  Ferramentas: MCPTool, HTTPTool, SIGTool")
    print()
    validate_config()
