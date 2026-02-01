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
    
    NOTA: Esta função é mantida para compatibilidade, mas o agente de planilhas agora usa
    code_interpreter diretamente para analisar arquivos Excel anexados às mensagens.
    
    Quando um arquivo Excel é anexado, o code_interpreter pode ler e analisar usando pandas.
    """
    return (
        "Para analisar uma planilha Excel, anexe o arquivo (.xlsx, .xls ou .csv) à sua mensagem. "
        "Eu usarei o code_interpreter para ler e analisar os dados diretamente. "
        "Você pode pedir análises como: estatísticas descritivas, filtros, agrupamentos, visualizações e muito mais."
    )


TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "query_spreadsheet",
            "description": """Informa ao usuário como anexar arquivos Excel para análise.
            
            IMPORTANTE: O agente de planilhas usa code_interpreter para analisar arquivos Excel diretamente.
            Quando o usuário anexar um arquivo Excel (.xlsx, .xls ou .csv) à mensagem, você pode usar
            code_interpreter com Python/pandas para ler e analisar os dados.
            
            Use esta ferramenta apenas para orientar o usuário sobre como anexar arquivos.
            Para análises reais, use code_interpreter quando um arquivo for anexado.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Descrição da consulta ou análise desejada pelo usuário."
                    }
                },
                "required": ["query"]
            }
        }
    },
]
