"""
Testes para o framework MCP do uniBot.
"""

import pytest
from app.mcp_tools import MCPTool
from app.tools import BaseTool, HTTPTool, SIGTool


class DummyTool(BaseTool):
    """Ferramenta dummy para testes."""

    def __init__(self):
        super().__init__(name="dummy", description="Ferramenta de teste")

    def call(self, params):
        if "error" in params:
            return self.format_result(success=False, error=params["error"])
        return self.format_result(success=True, data={"result": "ok"})


class TestMCPRegistry:
    """Testes do registry de ferramentas MCP."""

    def test_register_tool(self):
        """Deve registrar uma ferramenta com sucesso."""
        mcp = MCPTool()
        tool = DummyTool()
        mcp.register("test", tool)

        assert "test" in mcp.list_tools()
        assert mcp.get_tool("test") == tool

    def test_register_non_basetool_raises_error(self):
        """Deve falhar ao registrar algo que não é BaseTool."""
        mcp = MCPTool()
        with pytest.raises(TypeError):
            mcp.register("invalid", "not a tool")

    def test_unregister_tool(self):
        """Deve remover uma ferramenta."""
        mcp = MCPTool()
        tool = DummyTool()
        mcp.register("test", tool)

        assert mcp.unregister("test") == True
        assert "test" not in mcp.list_tools()

    def test_unregister_nonexistent_tool(self):
        """Deve retornar False ao remover ferramenta inexistente."""
        mcp = MCPTool()
        assert mcp.unregister("nonexistent") == False

    def test_list_tools(self):
        """Deve listar ferramentas registradas."""
        mcp = MCPTool()
        tool1 = DummyTool()
        tool2 = DummyTool()

        mcp.register("tool1", tool1)
        mcp.register("tool2", tool2)

        tools = mcp.list_tools()
        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools

    def test_get_nonexistent_tool(self):
        """Deve retornar None para ferramenta inexistente."""
        mcp = MCPTool()
        assert mcp.get_tool("nonexistent") is None


class TestMCPCalling:
    """Testes de execução de ferramentas."""

    def test_call_registered_tool(self):
        """Deve chamar uma ferramenta registrada."""
        mcp = MCPTool()
        tool = DummyTool()
        mcp.register("test", tool)

        result = mcp.call("test", {})
        assert result["success"] == True
        assert result["tool"] == "dummy"

    def test_call_nonexistent_tool(self):
        """Deve retornar erro ao chamar ferramenta inexistente."""
        mcp = MCPTool()
        result = mcp.call("nonexistent", {})

        assert result["success"] == False
        assert "não registrada" in result["error"]

    def test_call_tool_with_error(self):
        """Deve passar erro da ferramenta."""
        mcp = MCPTool()
        tool = DummyTool()
        mcp.register("test", tool)

        result = mcp.call("test", {"error": "test error"})
        assert result["success"] == False
        assert result["error"] == "test error"

    def test_call_tool_exception_handling(self):
        """Deve tratar exceções de ferramentas."""
        class BrokenTool(BaseTool):
            def __init__(self):
                super().__init__(name="broken", description="Ferramenta quebrada")

            def call(self, params):
                raise RuntimeError("Algo deu errado")

        mcp = MCPTool()
        mcp.register("broken", BrokenTool())

        result = mcp.call("broken", {})
        assert result["success"] == False
        assert "Erro ao executar" in result["error"]


class TestBaseTool:
    """Testes da classe base BaseTool."""

    def test_validate_params_success(self):
        """Deve validar parâmetros com sucesso."""
        tool = DummyTool()
        assert tool.validate_params({"a": 1, "b": 2}, required=["a", "b"]) == True

    def test_validate_params_missing(self):
        """Deve falhar se parâmetros obrigatórios faltam."""
        tool = DummyTool()
        assert tool.validate_params({"a": 1}, required=["a", "b"]) == False

    def test_validate_params_no_required(self):
        """Deve retornar True se nenhum parâmetro é obrigatório."""
        tool = DummyTool()
        assert tool.validate_params({}) == True

    def test_format_result_success(self):
        """Deve formatar resultado com sucesso."""
        tool = DummyTool()
        result = tool.format_result(success=True, data={"x": 1})

        assert result["success"] == True
        assert result["tool"] == "dummy"
        assert result["data"] == {"x": 1}
        assert result["error"] is None

    def test_format_result_error(self):
        """Deve formatar resultado com erro."""
        tool = DummyTool()
        result = tool.format_result(success=False, error="Algo deu errado")

        assert result["success"] == False
        assert result["error"] == "Algo deu errado"
        assert result["data"] is None


class TestHTTPTool:
    """Testes da ferramenta HTTP."""

    def test_http_tool_initialization(self):
        """Deve inicializar HTTPTool."""
        tool = HTTPTool(base_url="https://api.example.com")
        assert tool.base_url == "https://api.example.com"
        assert tool.timeout == 30.0

    def test_http_tool_missing_params(self):
        """Deve falhar se faltam parâmetros obrigatórios."""
        tool = HTTPTool()
        result = tool.call({})

        assert result["success"] == False
        assert "obrigatório" in result["error"]

    def test_http_tool_set_base_url(self):
        """Deve atualizar URL base."""
        tool = HTTPTool()
        tool.set_base_url("https://new-api.com")
        assert tool.base_url == "https://new-api.com"


class TestSIGTool:
    """Testes da ferramenta SIG."""

    def test_sig_tool_initialization(self):
        """Deve inicializar SIGTool."""
        tool = SIGTool(base_url="https://sig.ufla.br")
        assert tool.base_url == "https://sig.ufla.br"
        assert "resolucoes" in tool.endpoints

    def test_sig_tool_endpoints(self):
        """Deve ter endpoints pré-configurados."""
        tool = SIGTool()
        endpoints = tool.endpoints

        assert "usuarios" in endpoints
        assert "documentos" in endpoints
        assert "resolucoes" in endpoints
        assert "horarios" in endpoints

    def test_sig_tool_missing_endpoint(self):
        """Deve retornar erro para endpoint desconhecido."""
        tool = SIGTool()
        result = tool.call({"endpoint": "desconhecido"})

        assert result["success"] == False
        assert "desconhecido" in result["error"]

    def test_sig_tool_configure_endpoints(self):
        """Deve atualizar endpoints dinamicamente."""
        tool = SIGTool()
        new_endpoints = {"usuarios": "/v2/users"}
        tool.configure_endpoints(new_endpoints)

        assert tool.endpoints["usuarios"] == "/v2/users"

    def test_sig_tool_search_methods(self):
        """Deve ter métodos de busca específicos."""
        tool = SIGTool()

        assert callable(tool.search_usuarios)
        assert callable(tool.search_resolucoes)
        assert callable(tool.search_documentos)


class TestIntegration:
    """Testes de integração."""

    def test_multiple_tools_registry(self):
        """Deve gerenciar múltiplas ferramentas."""
        mcp = MCPTool()

        tools = [DummyTool() for _ in range(3)]
        for i, tool in enumerate(tools):
            mcp.register(f"tool_{i}", tool)

        assert len(mcp.list_tools()) == 3

    def test_tool_replacement(self):
        """Deve permitir substituir uma ferramenta registrada."""
        mcp = MCPTool()

        tool1 = DummyTool()
        mcp.register("test", tool1)

        tool2 = DummyTool()
        mcp.register("test", tool2)

        assert mcp.get_tool("test") == tool2


# Executar testes
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
