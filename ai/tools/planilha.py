# -*- coding: utf-8 -*-
"""
Tools exclusivas do Assistente de Análise de Dados em Planilhas Excel.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def query_spreadsheet_data(query: str) -> str | dict[str, Any]:
    """
    Consulta/análise em planilha Excel.
    Por enquanto retorna mensagem informativa; futuramente aceitará upload de Excel na aplicação.
    """
    # Stub: quando houver upload de Excel na demo, aqui pode-se usar dados em memória ou path
    return (
        "Análise de planilha Excel: envie um arquivo Excel na aplicação (upload) para habilitar esta função. "
        "Em breve você poderá fazer upload de planilhas e consultar dados, KPIs, estatísticas e métricas em linguagem natural."
    )


TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "query_spreadsheet",
            "description": """Realiza consultas e análises em planilhas Excel.
            Use esta ferramenta para:
            - Obter informações sobre a estrutura da planilha (colunas, linhas, tipos de dados)
            - Calcular estatísticas descritivas (média, mediana, soma, máximo, mínimo)
            - Analisar KPIs e indicadores
            - Contar valores únicos ou totais
            - Filtrar e visualizar dados
            O usuário pode enviar uma planilha Excel na aplicação para você analisar.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Descrição da consulta ou análise desejada (ex.: 'mostrar informações da planilha', 'calcular média da coluna vendas')."
                    }
                },
                "required": ["query"]
            }
        }
    },
]
