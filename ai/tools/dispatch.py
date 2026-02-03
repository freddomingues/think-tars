# -*- coding: utf-8 -*-
"""
Dispatch centralizado de tool calls do Assistant API.

Executa funções a partir de nome e argumentos, com tratamentos específicos
por tool. Novas tools: implementar em ai.tools (base + módulo do agente) e adicionar branch aqui se a assinatura for especial.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from ai.tools.base import AVAILABLE_FUNCTIONS
except (ImportError, ValueError):
    AVAILABLE_FUNCTIONS = {}


def dispatch_tool_call(
    function_name: str,
    arguments: dict[str, Any],
    *,
    allowed_tool_names: set[str] | None = None,
) -> str:
    """
    Executa a tool indicada e retorna o output como string.

    Args:
        function_name: Nome da função (ex.: search_contracts, buy_bitcoin).
        arguments: Dict com argumentos (ex.: {"query": "...", "k": 5}).
        allowed_tool_names: Se informado, só executa tools cujo nome está neste conjunto
            (isolamento por assistente). Se None, permite qualquer tool em AVAILABLE_FUNCTIONS.

    Returns:
        String com resultado ou mensagem de erro.
    """
    if allowed_tool_names is not None and function_name not in allowed_tool_names:
        logger.warning("Tool '%s' não permitida para este assistente (allowed: %s)", function_name, allowed_tool_names)
        return f"Função '{function_name}' não está disponível para este assistente."

    if function_name not in AVAILABLE_FUNCTIONS:
        logger.warning("Tool não encontrada: %s", function_name)
        return f"Função '{function_name}' não disponível."

    fn = AVAILABLE_FUNCTIONS[function_name]
    args = arguments or {}

    try:
        if function_name in ("search_contracts", "search_faqs"):
            result = fn(args.get("query", ""), args.get("k", 5))
        elif function_name == "query_spreadsheet":
            result = fn(args.get("query", ""))
        elif function_name in ("buy_bitcoin", "sell_bitcoin"):
            q = args.get("quantity")
            result = fn(quantity=q) if q is not None else fn()
        elif function_name in (
            "analyze_bitcoin_market",
            "get_bitcoin_price",
            "get_portfolio_status",
            "get_tomorrow_events",
        ):
            result = fn()
        elif function_name == "create_calendar_event":
            # Intercepta create_calendar_event para garantir envio sistemático de WhatsApp
            logger.info(f"🔔 Tool create_calendar_event chamada com args: {args}")
            result = fn(**args)
            # Verifica se o resultado indica que o evento foi criado
            if result and "✅ Evento criado" in result:
                logger.info("✅ Evento criado com sucesso, notificação WhatsApp deve ter sido enviada")
            elif result and "❌ Erro" not in result:
                logger.warning(f"⚠️ create_calendar_event retornou: {result[:200]}")
        elif function_name in (
            "check_available_slots",
            "cancel_calendar_event",
            "get_events_by_date",
            "confirm_tomorrow_agenda",
        ):
            result = fn(**args)
        else:
            result = fn(**args)

        if isinstance(result, str):
            return result
        return str(result)
    except Exception as e:
        logger.exception("Erro ao executar tool %s: %s", function_name, e)
        return f"Erro ao executar tool: {e}"
