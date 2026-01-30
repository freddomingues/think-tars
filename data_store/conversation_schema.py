# -*- coding: utf-8 -*-
"""
Armazenamento in-memory de conversas e mensagens (compatibilidade).
O projeto não usa mais AWS DynamoDB; dados ficam em memória apenas.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Armazenamento em memória (apenas para compatibilidade com o webhook)
_messages: list[dict[str, Any]] = []
_sentiments: list[dict[str, Any]] = []


class ConversationManager:
    """Gerenciador de conversas em memória (sem persistência)."""

    def _load_tables(self) -> None:
        """Não faz nada; mantido para compatibilidade."""
        pass

    def create_tables(self) -> None:
        """Não faz nada; mantido para compatibilidade."""
        pass

    def save_message(
        self,
        conversation_id: str,
        phone_number: str,
        message: str,
        sender: str,
    ) -> Optional[str]:
        """Salva mensagem em memória e retorna um ID."""
        message_id = str(uuid.uuid4())
        _messages.append({
            "message_id": message_id,
            "conversation_id": conversation_id,
            "phone_number": phone_number,
            "message": message,
            "sender": sender,
        })
        logger.debug(f"Mensagem salva em memória: {message_id}")
        return message_id

    def save_sentiment_analysis(
        self,
        message_id: str,
        conversation_id: str,
        sentiment_data: dict[str, Any],
    ) -> None:
        """Registra análise de sentimento em memória."""
        _sentiments.append({
            "message_id": message_id,
            "conversation_id": conversation_id,
            "sentiment_data": sentiment_data,
        })
        logger.debug(f"Análise de sentimento salva para mensagem {message_id}")


conversation_manager = ConversationManager()
