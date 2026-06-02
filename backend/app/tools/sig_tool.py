"""
Ferramenta para integração com o SIG (Sistema Integrado de Gestão) da UFLA.

Endpoints disponíveis (a serem documentados e preenchidos):
- Usuários (alunos, professores, servidores)
- Documentos / Resoluções
- Horários / Calendário
- Notas / Desempenho
- Disciplinas
- Matrículas

Template pronto para ser atualizado assim que a documentação do SIG estiver disponível.
"""

from typing import Any, Dict, Optional
import logging
from .http_tool import HTTPTool

logger = logging.getLogger(__name__)


class SIGTool(HTTPTool):
    """
    Ferramenta especializada para consultar dados do SIG da UFLA.

    Endpoints devem ser preenchidos em config.py ou via .env quando a
    documentação do SIG estiver disponível.
    """

    def __init__(self, base_url: str = "https://sig.ufla.br", name: str = "sig_tool"):
        """
        Inicializa ferramenta SIG.

        Args:
            base_url: URL base do SIG (padrão: UFLA)
            name: Nome da ferramenta
        """
        super().__init__(base_url=base_url, name=name)
        self.description = "Consulta dados do SIG (Sistema Integrado de Gestão) da UFLA"

        # Endpoints conhecidos (a serem preenchidos)
        self.endpoints = {
            "usuarios": "/api/usuarios",
            "documentos": "/api/documentos",
            "resolucoes": "/api/resolucoes",
            "horarios": "/api/horarios",
            "notas": "/api/notas",
            "disciplinas": "/api/disciplinas",
            "matriculas": "/api/matriculas",
        }

    def call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chamada genérica ao SIG.

        Args:
            params: {
                "endpoint": "usuarios", "documentos", "resolucoes", etc,
                "query": "termo de busca",
                "filters": {...},
                ...
            }

        Returns:
            Resultado da chamada ao SIG
        """
        endpoint = params.get("endpoint")

        if not endpoint:
            return self.format_result(
                success=False,
                error="Parâmetro 'endpoint' é obrigatório"
            )

        if endpoint not in self.endpoints:
            return self.format_result(
                success=False,
                error=f"Endpoint desconhecido: {endpoint}. Disponíveis: {list(self.endpoints.keys())}"
            )

        # Preparar URL
        url = self.endpoints[endpoint]

        # Se há query, adicionar como parâmetro
        query_params = {}
        if "query" in params:
            query_params["q"] = params["query"]

        if "filters" in params:
            query_params.update(params["filters"])

        logger.info(f"[{self.name}] Consultando {endpoint} com query={query_params}")

        # Delegar para HTTPTool
        return super().call({
            "method": "GET",
            "url": url,
            "params": query_params,
        })

    def search_usuarios(self, query: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Buscar usuários no SIG (alunos, professores, servidores).

        Args:
            query: Termo de busca (nome, matrícula, email)
            filters: Filtros adicionais (tipo: "aluno", "professor", etc)

        Returns:
            Resultado da busca
        """
        return self.call({
            "endpoint": "usuarios",
            "query": query,
            "filters": filters or {}
        })

    def search_resolucoes(self, query: str) -> Dict[str, Any]:
        """
        Buscar resoluções no SIG.

        Args:
            query: Termo de busca (ex: "473", "CEPE")

        Returns:
            Resultado da busca
        """
        return self.call({
            "endpoint": "resolucoes",
            "query": query,
        })

    def search_documentos(self, query: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Buscar documentos no SIG.

        Args:
            query: Termo de busca
            filters: Filtros adicionais (tipo, data, etc)

        Returns:
            Resultado da busca
        """
        return self.call({
            "endpoint": "documentos",
            "query": query,
            "filters": filters or {}
        })

    def get_horarios(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Obter horários / calendário acadêmico.

        Args:
            filters: Filtros (semestre, curso, turma, etc)

        Returns:
            Resultado
        """
        return self.call({
            "endpoint": "horarios",
            "filters": filters or {}
        })

    def get_notas(self, matricula: str) -> Dict[str, Any]:
        """
        Obter notas de um aluno.

        Args:
            matricula: Matrícula do aluno

        Returns:
            Resultado
        """
        return self.call({
            "endpoint": "notas",
            "filters": {"matricula": matricula}
        })

    def configure_endpoints(self, endpoints: Dict[str, str]):
        """
        Atualiza endpoints dinamicamente.

        Args:
            endpoints: Dicionário com novos endpoints
        """
        self.endpoints.update(endpoints)
        logger.info(f"[{self.name}] Endpoints atualizados: {self.endpoints}")

    def __repr__(self):
        return f"<SIGTool at {self.base_url}>"
