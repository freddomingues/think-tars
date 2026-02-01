# -*- coding: utf-8 -*-
"""Tools exclusivas do Assistente de Suporte Técnico."""
import logging

logger = logging.getLogger(__name__)


def search_knowledge_base(query: str, category: str = None) -> str:
    """
    Busca na base de conhecimento de suporte técnico.
    
    Args:
        query: Consulta sobre o problema técnico
        category: Categoria do problema (opcional)
    
    Returns:
        Solução ou documentação encontrada
    """
    category_info = f" (categoria: {category})" if category else ""
    return f"Busca na base de conhecimento{category_info}: {query}. Esta funcionalidade está em desenvolvimento e em breve permitirá busca em base de conhecimento técnica completa."


TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": """Busca na base de conhecimento de suporte técnico.
            Use esta ferramenta quando o usuário:
            - Relatar um problema técnico específico
            - Pedir instruções de configuração
            - Solicitar solução para erro ou bug
            - Pedir documentação técnica
            - Buscar troubleshooting
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Consulta sobre o problema técnico, configuração ou documentação desejada"
                    },
                    "category": {
                        "type": "string",
                        "description": "Categoria do problema (ex: 'software', 'hardware', 'configuration', 'error', 'documentation')"
                    }
                },
                "required": ["query"]
            }
        }
    },
]