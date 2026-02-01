# -*- coding: utf-8 -*-
"""Tools exclusivas do Assistente de Recursos Humanos."""
import logging

logger = logging.getLogger(__name__)


def analyze_hr_metrics(metric_type: str, description: str = "") -> str:
    """
    Analisa métricas e indicadores de Recursos Humanos.
    
    Args:
        metric_type: Tipo de métrica a analisar
        description: Descrição das métricas fornecidas
    
    Returns:
        Análise das métricas de RH
    """
    return f"Análise de métricas de RH ({metric_type}): {description}. Esta funcionalidade está em desenvolvimento e em breve permitirá análise detalhada de indicadores de Recursos Humanos."


TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "analyze_hr_metrics",
            "description": """Analisa métricas e indicadores de Recursos Humanos.
            Use esta ferramenta quando o usuário pedir análise de:
            - Taxa de turnover
            - Absenteísmo
            - Satisfação e engajamento dos funcionários
            - Tempo médio de recrutamento
            - Custo por contratação
            - Performance de equipes
            - Análise de clima organizacional
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "metric_type": {
                        "type": "string",
                        "description": "Tipo de métrica a analisar (ex: 'turnover', 'satisfaction', 'recruitment', 'performance')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Descrição das métricas ou dados fornecidos pelo usuário"
                    }
                },
                "required": ["metric_type"]
            }
        }
    },
]