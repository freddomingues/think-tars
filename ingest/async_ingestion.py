#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script assíncrono para ingestão de documentos do S3.
Permite processar contratos e FAQs de forma independente e em background.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from ingest.ingest_contracts import index_all_contracts
from ingest.ingest_faqs import index_all_faqs

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def ingest_contracts_async():
    """Processa contratos de forma assíncrona."""
    try:
        logger.info("Iniciando ingestão de contratos...")
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, index_all_contracts)
        logger.info("Ingestão de contratos concluída!")
    except Exception as e:
        logger.error(f"Erro na ingestão de contratos: {e}")

async def ingest_faqs_async():
    """Processa FAQs de forma assíncrona."""
    try:
        logger.info("Iniciando ingestão de FAQs...")
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, index_all_faqs)
        logger.info("Ingestão de FAQs concluída!")
    except Exception as e:
        logger.error(f"Erro na ingestão de FAQs: {e}")

async def ingest_all_documents():
    """Processa todos os documentos em paralelo."""
    logger.info("Iniciando ingestão completa de documentos...")
    
    # Executa contratos e FAQs em paralelo
    await asyncio.gather(
        ingest_contracts_async(),
        ingest_faqs_async(),
        return_exceptions=True
    )
    
    logger.info("Ingestão completa finalizada!")

if __name__ == "__main__":
    asyncio.run(ingest_all_documents())
