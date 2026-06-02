"""
Ferramenta para consulta do cardápio do Restaurante Universitário (RU) da UFLA.
Realiza scraping da página pública do SIG ou simula acesso autenticado.
"""

import httpx
import logging
import re
from typing import Any, Dict, Optional
from .http_tool import HTTPTool

logger = logging.getLogger(__name__)

class RUTool(HTTPTool):
    """
    Ferramenta para consultar o cardápio do RU via scraping.
    """

    def __init__(self, name: str = "ru_tool"):
        # URL pública do cardápio no SIG
        base_url = "https://sig.ufla.br/modulos/publico/praec/consultar_cardapios.php"
        super().__init__(base_url=base_url, name=name)
        self.description = "Consulta o cardápio diário do Restaurante Universitário (RU) da UFLA"

    def call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consulta o cardápio real ou identifica necessidade de autenticação.
        """
        action = params.get("action", "cardapio")
        
        if action in ["saldo", "extrato", "creditos"]:
            return self.format_result(
                success=False, 
                error="AUTH_REQUIRED",
                data={"message": "Para consultar saldo ou créditos, é necessário identificar-se (autenticação necessária)."}
            )

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            resp = httpx.get(self.base_url, headers=headers, timeout=15, follow_redirects=True)
            resp.raise_for_status()
            
            html = resp.text
            
            # Extrair o cardápio da tabela (versão simplificada via Regex)
            # Procuramos por linhas da tabela que contêm os pratos
            menu_data = {}
            rows = re.findall(r'<tr><th[^>]*>(.*?)</th><td[^>]*>(.*?)</td><td[^>]*>(.*?)</td></tr>', html, re.DOTALL)
            
            if rows:
                for label, almoco, jantar in rows:
                    label = self._clean_html(label)
                    almoco = self._clean_html(almoco)
                    jantar = self._clean_html(jantar)
                    if label:
                        menu_data[label] = {"almoco": almoco, "jantar": jantar}

            if not menu_data:
                return self.format_result(
                    success=True,
                    data={
                        "info": "Não foi possível extrair o cardápio detalhado, mas você pode acessar o link.",
                        "url": self.base_url
                    }
                )

            return self.format_result(
                success=True,
                data={
                    "info": "Cardápio do dia recuperado com sucesso.",
                    "cardapio": menu_data,
                    "url": self.base_url
                }
            )
        except Exception as e:
            logger.error(f"[RUTool] Erro no scraping: {str(e)}")
            return self.format_result(success=False, error=f"Erro ao acessar cardápio: {str(e)}")

    def _clean_html(self, text: str) -> str:
        """Remove tags HTML e limpa entidades comuns."""
        text = re.sub(r'<[^>]+>', ' ', text)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&aacute;', 'á').replace('&eacute;', 'é').replace('&iacute;', 'í').replace('&oacute;', 'ó').replace('&uacute;', 'ú')
        text = text.replace('&atilde;', 'ã').replace('&otilde;', 'õ').replace('&ccedil;', 'ç')
        text = text.replace('&Agrave;', 'À').replace('&Egrave;', 'È')
        # Limpar espaços extras
        text = re.sub(r'\s+', ' ', text).strip()
        return text
