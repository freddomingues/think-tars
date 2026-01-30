# -*- coding: utf-8 -*-
"""Tools exclusivas do Assistente Jurídico: busca em contratos e FAQs (Pinecone)."""

TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "search_contracts",
            "description": "Busca trechos de contratos jurídicos relevantes.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "k": {"type": "integer", "default": 5}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_faqs",
            "description": "Busca trechos de FAQs relevantes.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "k": {"type": "integer", "default": 5}},
                "required": ["query"]
            }
        }
    },
]
