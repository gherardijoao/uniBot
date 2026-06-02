"""
Ferramenta genérica para chamadas HTTP.
Permite que o RAG faça requisições a APIs externas.
"""

from typing import Any, Dict, Optional
import httpx
import logging

from .base_tool import BaseTool

logger = logging.getLogger(__name__)


class HTTPTool(BaseTool):
    """Ferramenta para fazer requisições HTTP genéricas."""

    def __init__(self, base_url: str = "", name: str = "http_tool"):
        """
        Inicializa ferramenta HTTP.

        Args:
            base_url: URL base para requisições (opcional)
            name: Nome da ferramenta
        """
        super().__init__(
            name=name,
            description="Faz requisições HTTP (GET, POST) para APIs externas"
        )
        self.base_url = base_url
        self.timeout = 30.0

    def call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Faz uma requisição HTTP.

        Args:
            params: {
                "method": "GET" ou "POST",
                "url": "https://api.example.com/...",
                "headers": {...},
                "data": {...},
                "params": {...}
            }

        Returns:
            Resultado da requisição
        """
        if not self.validate_params(params, required=["method", "url"]):
            return self.format_result(
                success=False,
                error="Parâmetros obrigatórios: 'method' e 'url'"
            )

        method = params.get("method", "GET").upper()
        url = params.get("url", "")
        headers = params.get("headers", {})
        data = params.get("data")
        query_params = params.get("params")

        # Se há base_url, concatenar
        if self.base_url and url and not url.startswith("http"):
            url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"

        try:
            logger.info(f"[{self.name}] Chamando {method} {url}")

            with httpx.Client(timeout=self.timeout) as client:
                if method == "GET":
                    response = client.get(url, headers=headers, params=query_params)  # type: ignore
                elif method == "POST":
                    response = client.post(url, headers=headers, json=data, params=query_params)  # type: ignore
                else:
                    return self.format_result(
                        success=False,
                        error=f"Método HTTP não suportado: {method}"
                    )

                response.raise_for_status()

                return self.format_result(
                    success=True,
                    data={
                        "status": response.status_code,
                        "body": response.json() if response.text else None,
                    }
                )

        except httpx.HTTPStatusError as e:
            logger.error(f"[{self.name}] HTTP {e.response.status_code}: {e.response.text}")
            return self.format_result(
                success=False,
                error=f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            )
        except Exception as e:
            logger.error(f"[{self.name}] Erro: {str(e)}")
            return self.format_result(
                success=False,
                error=str(e)
            )

    def set_base_url(self, base_url: str):
        """Atualiza a URL base."""
        self.base_url = base_url
        logger.info(f"[{self.name}] URL base atualizada: {base_url}")
