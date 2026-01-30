# -*- coding: utf-8 -*-
"""
Armazenamento in-memory de thread_id por usuário (telefone).
Substitui o antigo dynamodb_handler; o projeto não usa mais AWS.
"""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Armazenamento em memória: phone_number -> thread_id
_thread_store: dict[str, str] = {}


def get_user_thread_id(phone_number: str) -> Optional[str]:
    """
    Recupera o thread_id do usuário.
    Retorna o thread_id se encontrado, None caso contrário.
    """
    thread_id = _thread_store.get(phone_number)
    if thread_id:
        logger.info(f"Thread ID encontrado para {phone_number}")
    return thread_id


def save_user_thread_id(phone_number: str, thread_id: str) -> None:
    """Salva ou atualiza o thread_id do usuário."""
    _thread_store[phone_number] = thread_id
    logger.info(f"Thread ID {thread_id} salvo para {phone_number}")
