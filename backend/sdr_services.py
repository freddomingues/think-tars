# -*- coding: utf-8 -*-
"""
Serviços do assistente SDR (WhatsApp — uso interno).

Mantém thread por telefone e executa run_turn com o agente SDR.
Não exposto no Playground.
"""
from __future__ import annotations

import logging
from typing import Any

from openai import OpenAI

from ai.agents import get_agent_tool_names, get_internal_agent_config
from ai.assistant_manager import create_or_get_assistant_from_registry
from ai.assistant_run import run_turn
from config.settings import OPENAI_API_KEY

logger = logging.getLogger(__name__)

SDR_AGENT_ID = "sdr"

_openai_client: OpenAI | None = None
_sdr_thread_by_phone: dict[str, str] = {}  # phone -> thread_id
_sdr_assistant_id: str | None = None


def _client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def _get_sdr_assistant_id() -> str | None:
    global _sdr_assistant_id
    if _sdr_assistant_id is None:
        cfg = get_internal_agent_config(SDR_AGENT_ID)
        if not cfg:
            logger.error("Agente SDR não encontrado no INTERNAL_AGENTS_REGISTRY")
            return None
        a_id = create_or_get_assistant_from_registry(SDR_AGENT_ID)
        if a_id:
            _sdr_assistant_id = a_id
    return _sdr_assistant_id


def get_or_create_sdr_thread(phone: str) -> str | None:
    """Obtém ou cria thread OpenAI para o telefone (conversa SDR)."""
    if phone in _sdr_thread_by_phone:
        return _sdr_thread_by_phone[phone]
    if not _get_sdr_assistant_id():
        return None
    try:
        thread = _client().beta.threads.create()
        _sdr_thread_by_phone[phone] = thread.id
        return thread.id
    except Exception as e:
        logger.exception("Erro ao criar thread SDR para %s: %s", phone, e)
        return None


def run_sdr_turn(phone: str, user_message: str) -> str | None:
    """
    Executa um turno do assistente SDR para o telefone e retorna a resposta em texto.

    Args:
        phone: Número do lead (formato normalizado).
        user_message: Mensagem recebida do lead.

    Returns:
        Texto da resposta do SDR ou None em caso de erro.
    """
    thread_id = get_or_create_sdr_thread(phone)
    if not thread_id:
        logger.error("SDR: get_or_create_sdr_thread retornou None para phone=%s (verifique OPENAI_API_KEY e INTERNAL_AGENTS_REGISTRY)", phone)
        return None
    assistant_id = _get_sdr_assistant_id()
    if not assistant_id:
        logger.error("SDR: _get_sdr_assistant_id retornou None (agente SDR não encontrado ou falha ao criar assistente)")
        return None
    allowed_tool_names = get_agent_tool_names(SDR_AGENT_ID)
    try:
        reply = run_turn(
            client=_client(),
            thread_id=thread_id,
            assistant_id=assistant_id,
            user_message=user_message,
            allowed_tool_names=allowed_tool_names,
        )
        if not reply:
            logger.warning("SDR: run_turn retornou None (verifique no log: run status ou 'nenhuma mensagem do assistente')")
        return reply
    except Exception as e:
        logger.exception("Erro ao executar run_turn SDR: %s", e)
        return None
