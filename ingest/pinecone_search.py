# -*- coding: utf-8 -*-
"""
Busca em documentos indexados no Pinecone (contratos e FAQs).
Os dados vêm dos arquivos que os clientes fazem upload na aplicação.
"""
from __future__ import annotations

import logging
from ai.pinecone_client import pinecone_client

logger = logging.getLogger(__name__)


def search_contracts(query: str, k: int = 5) -> str:
    """Busca trechos de contratos via Pinecone."""
    try:
        results = pinecone_client.search(query=query, k=k, namespace="contracts")
        docs = results.get("documents", [[]])[0]
        return "\n".join(docs) if docs else "Nenhum trecho relevante de contrato encontrado."
    except Exception as e:
        logger.warning("Busca em contratos: %s", e)
        return "Nenhum trecho relevante de contrato encontrado."


def search_faqs(query: str, k: int = 5) -> str:
    """Busca trechos de FAQs via Pinecone."""
    try:
        results = pinecone_client.search(query=query, k=k, namespace="faqs")
        docs = results.get("documents", [[]])[0]
        return "\n".join(docs) if docs else "Nenhum trecho relevante de FAQ encontrado."
    except Exception as e:
        logger.warning("Busca em FAQs: %s", e)
        return "Nenhum trecho relevante de FAQ encontrado."
