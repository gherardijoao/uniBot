"""
Classe base para todas as ferramentas MCP.
Define a interface padrão que cada ferramenta deve implementar.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Classe abstrata para ferramentas que podem ser chamadas pelo RAGService."""

    def __init__(self, name: str, description: str = ""):
        """
        Inicializa a ferramenta.

        Args:
            name: Nome único da ferramenta
            description: Descrição do que a ferramenta faz
        """
        self.name = name
        self.description = description
        logger.info(f"[{self.name}] Ferramenta inicializada: {self.description}")

    @abstractmethod
    def call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa a ferramenta com os parâmetros fornecidos.

        Args:
            params: Dicionário com parâmetros da ferramenta

        Returns:
            Dicionário com resultado {"success": bool, "data": ..., "error": ...}
        """
        pass

    def validate_params(self, params: Dict[str, Any], required: Optional[list] = None) -> bool:
        """
        Valida se os parâmetros necessários foram fornecidos.

        Args:
            params: Parâmetros a validar
            required: Lista de chaves obrigatórias

        Returns:
            True se válido, False caso contrário
        """
        if not required:
            return True

        for key in required:
            if key not in params:
                logger.warning(f"[{self.name}] Parâmetro obrigatório faltando: {key}")
                return False
        return True

    def format_result(self, success: bool, data: Any = None, error: Optional[str] = None) -> Dict[str, Any]:
        """
        Formata resultado padrão para consistência.

        Args:
            success: Se a operação foi bem-sucedida
            data: Dados retornados
            error: Mensagem de erro, se houver

        Returns:
            Dicionário com formato padrão
        """
        return {
            "success": success,
            "tool": self.name,
            "data": data,
            "error": error,
        }

    def __str__(self):
        return f"<{self.name}: {self.description}>"
