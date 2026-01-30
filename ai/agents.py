# -*- coding: utf-8 -*-
"""
Registry de agentes de IA (OpenAI Assistant API).

- AGENTS_REGISTRY: agentes expostos no Playground (site). Cada um tem "playground": True.
- INTERNAL_AGENTS_REGISTRY: agentes de uso interno (ex.: SDR WhatsApp). Não aparecem no Playground.
"""
import importlib
from typing import Any

DEFAULT_AGENT_ID = "juridico"

# Agentes do Playground (listados na interface do site para o cliente testar)
AGENTS_REGISTRY = [
    {
        "id": "juridico",
        "name": "Assistente Jurídico de Contratos",
        "instructions_module": "ai.prompts.templates",
        "instructions_attr": "DEFAULT_ASSISTANT_INSTRUCTIONS",
        "tools_module": "ai.tools.juridico",
        "tools_attr": "TOOLS_DEFINITION",
        "playground": True,
    },
    {
        "id": "investment",
        "name": "CryptoAnalyst - Análise de Investimento",
        "instructions_module": "ai.prompts.investment",
        "instructions_attr": "INVESTMENT_ASSISTANT_INSTRUCTIONS",
        "tools_module": "ai.tools.investment",
        "tools_attr": "TOOLS_DEFINITION",
        "playground": True,
    },
    {
        "id": "planilha",
        "name": "Analista de Dados - Planilha Excel",
        "instructions_module": "ai.prompts.planilha",
        "instructions_attr": "PLANILHA_ASSISTANT_INSTRUCTIONS",
        "tools_module": "ai.tools.planilha",
        "tools_attr": "TOOLS_DEFINITION",
        "playground": True,
    },
]

# Agentes de uso interno (ex.: SDR no WhatsApp via Z-API). Não listados no Playground.
INTERNAL_AGENTS_REGISTRY = [
    {
        "id": "sdr",
        "name": "SDR - Atendimento e Qualificação",
        "instructions_module": "ai.prompts.sdr",
        "instructions_attr": "SDR_ASSISTANT_INSTRUCTIONS",
        "tools_module": "ai.tools.sdr",
        "tools_attr": "TOOLS_DEFINITION",
        "playground": False,
    },
]


def get_agent_config(agent_id: str) -> dict[str, Any] | None:
    """Retorna configuração do agente por id (Playground ou interno)."""
    for a in AGENTS_REGISTRY + INTERNAL_AGENTS_REGISTRY:
        if a["id"] == agent_id:
            return a
    return None


def get_internal_agent_config(agent_id: str) -> dict[str, Any] | None:
    """Retorna configuração de agente interno por id."""
    for a in INTERNAL_AGENTS_REGISTRY:
        if a["id"] == agent_id:
            return a
    return None


def get_default_agent() -> dict[str, Any]:
    """Retorna o agente padrão (juridico)."""
    out = get_agent_config(DEFAULT_AGENT_ID)
    if out:
        return out
    return AGENTS_REGISTRY[0]


def load_agent_instructions(agent_id: str) -> str | None:
    """Carrega instruções (prompt) do agente a partir do registry."""
    cfg = get_agent_config(agent_id)
    if not cfg:
        return None
    mod = importlib.import_module(cfg["instructions_module"])
    return getattr(mod, cfg["instructions_attr"], None)


def load_agent_tools(agent_id: str) -> list | None:
    """Carrega TOOLS_DEFINITION do agente a partir do registry."""
    cfg = get_agent_config(agent_id)
    if not cfg:
        return None
    mod = importlib.import_module(cfg["tools_module"])
    return getattr(mod, cfg["tools_attr"], None)


def get_agent_tool_names(agent_id: str) -> set[str]:
    """
    Retorna o conjunto de nomes de tools permitidos para o agente.
    Usado para isolar o dispatch: só executa tools desse agente.
    """
    tools = load_agent_tools(agent_id)
    if not tools:
        return set()
    return {t["function"]["name"] for t in tools if t.get("type") == "function" and t.get("function", {}).get("name")}
