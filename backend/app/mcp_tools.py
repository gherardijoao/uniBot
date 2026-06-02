"""
Coordenador de ferramentas MCP (Model Context Protocol).
Gerencia registro e execução de ferramentas externas que podem ser chamadas pelo RAG.

Exemplo de uso:
    mcp = MCPTool()
    mcp.register("buscar_sig", SIGTool(base_url="https://sig.ufla.br"))
    result = mcp.call("buscar_sig", {"endpoint": "resolucoes", "query": "473"})
"""

import logging
from typing import Dict, Any, Optional
from .tools import BaseTool, HTTPTool, SIGTool

logger = logging.getLogger(__name__)


class MCPTool:
    """Coordenador de ferramentas MCP."""

    def __init__(self):
        """Inicializa o registry de ferramentas."""
        self._tools: Dict[str, BaseTool] = {}
        logger.info("[MCPTool] Registry inicializado")

    def register(self, name: str, tool: BaseTool) -> None:
        """
        Registra uma nova ferramenta.

        Args:
            name: Nome único da ferramenta
            tool: Instância de BaseTool ou subclasse
        """
        if not isinstance(tool, BaseTool):
            raise TypeError(f"Ferramenta deve ser instância de BaseTool, recebido: {type(tool)}")

        self._tools[name] = tool
        logger.info(f"[MCPTool] Ferramenta registrada: {name} ({tool.description})")

    def unregister(self, name: str) -> bool:
        """
        Remove uma ferramenta registrada.

        Args:
            name: Nome da ferramenta

        Returns:
            True se removida, False se não encontrada
        """
        if name in self._tools:
            del self._tools[name]
            logger.info(f"[MCPTool] Ferramenta removida: {name}")
            return True
        return False

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        Obtém uma ferramenta registrada.

        Args:
            name: Nome da ferramenta

        Returns:
            Instância da ferramenta ou None
        """
        return self._tools.get(name)

    def list_tools(self) -> Dict[str, str]:
        """
        Lista todas as ferramentas registradas.

        Returns:
            Dicionário {nome: descrição}
        """
        return {name: tool.description for name, tool in self._tools.items()}

    def call(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma ferramenta registrada.

        Args:
            tool_name: Nome da ferramenta
            params: Parâmetros para a ferramenta

        Returns:
            Resultado da execução {success: bool, data: ..., error: ...}
        """
        if tool_name not in self._tools:
            logger.warning(f"[MCPTool] Ferramenta não encontrada: {tool_name}")
            return {
                "success": False,
                "tool": tool_name,
                "data": None,
                "error": f"Ferramenta '{tool_name}' não registrada. Disponíveis: {list(self._tools.keys())}"
            }

        try:
            logger.info(f"[MCPTool] Chamando {tool_name} com params={params}")
            tool = self._tools[tool_name]
            result = tool.call(params)
            logger.info(f"[MCPTool] {tool_name} retornou: success={result.get('success')}")
            return result
        except Exception as e:
            logger.error(f"[MCPTool] Erro ao chamar {tool_name}: {str(e)}")
            return {
                "success": False,
                "tool": tool_name,
                "data": None,
                "error": f"Erro ao executar ferramenta: {str(e)}"
            }

    def __repr__(self):
        tools_count = len(self._tools)
        return f"<MCPTool with {tools_count} registered tools>"
