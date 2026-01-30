#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração de logging para produção.
Centraliza todas as configurações de log da aplicação.
"""

import logging
import sys
from colorama import init as colorama_init, Fore, Style

colorama_init(autoreset=True)

def setup_logging():
    """Configura o sistema de logging para produção com cores e ícones."""
    
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Configura níveis de módulos específicos
    loggers = [
        'app.main',
        'ingest.pinecone_search',
        'data_store.thread_store',
        'ai.assistant_manager'
    ]
    for logger_name in loggers:
        logging.getLogger(logger_name).setLevel(logging.INFO)
    
    main_logger = logging.getLogger(__name__)
    main_logger.info(f"{Fore.GREEN}🔧 Sistema de logging configurado com sucesso!{Style.RESET_ALL}")
    return main_logger


# Funções de logging aprimoradas
def log_webhook_received(phone_number: str, message: str, event_type: str):
    logger = logging.getLogger('app.main')
    logger.info(f"{Fore.CYAN}📨 [WEBHOOK] Recebido - WhatsApp: {phone_number} | Event: {event_type}{Style.RESET_ALL}")
    logger.info(f"{Fore.CYAN}💬 [WEBHOOK] Mensagem: '{message[:100]}{'...' if len(message) > 100 else ''}'{Style.RESET_ALL}")

def log_tool_call(tool_name: str, query: str, results_count: int):
    logger = logging.getLogger('app.main')
    logger.info(f"{Fore.MAGENTA}🔧 [TOOL] {tool_name} - Query: '{query}' | Resultados: {results_count}{Style.RESET_ALL}")

def log_ai_response(phone_number: str, response: str):
    logger = logging.getLogger('app.main')
    logger.info(f"{Fore.YELLOW}🤖 [AI] Resposta para {phone_number}: '{response[:100]}{'...' if len(response) > 100 else ''}'{Style.RESET_ALL}")

def log_error(module: str, error: str, phone_number: str = None):
    logger = logging.getLogger(module)
    context = f" | WhatsApp: {phone_number}" if phone_number else ""
    logger.error(f"{Fore.RED}❌ [ERROR] {error}{context}{Style.RESET_ALL}")

def log_success(module: str, message: str, phone_number: str = None):
    logger = logging.getLogger(module)
    context = f" | WhatsApp: {phone_number}" if phone_number else ""
    logger.info(f"{Fore.GREEN}✅ [SUCCESS] {message}{context}{Style.RESET_ALL}")
