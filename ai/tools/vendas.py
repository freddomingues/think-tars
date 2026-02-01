# -*- coding: utf-8 -*-
"""Tools exclusivas do Assistente de Vendas."""
import logging

logger = logging.getLogger(__name__)


def analyze_sales_funnel(funnel_stage: str, description: str = "") -> str:
    """
    Analisa funil de vendas e performance.
    
    Args:
        funnel_stage: Etapa do funil a analisar
        description: Descrição dos dados fornecidos
    
    Returns:
        Análise do funil de vendas
    """
    return f"Análise de funil de vendas (etapa: {funnel_stage}): {description}. Esta funcionalidade está em desenvolvimento e em breve permitirá análise detalhada de funil de vendas e performance."


TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "analyze_sales_funnel",
            "description": """Analisa funil de vendas e performance.
            Use esta ferramenta quando o usuário pedir análise de:
            - Funil de vendas (leads, oportunidades, conversões)
            - Taxa de conversão por etapa
            - Tempo médio de ciclo de vendas
            - Performance de vendedores
            - Análise de pipeline
            - Identificação de gargalos no funil
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "funnel_stage": {
                        "type": "string",
                        "description": "Etapa do funil a analisar (ex: 'leads', 'qualification', 'proposal', 'closing', 'overall')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Descrição dos dados ou métricas fornecidas pelo usuário"
                    }
                },
                "required": ["funnel_stage"]
            }
        }
    },
]