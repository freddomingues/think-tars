# -*- coding: utf-8 -*-
"""
Re-export do registry de agentes (implementação em ai/agents.py).

Mantenha referências em ai.agents; este módulo existe para compatibilidade.
"""
from ai.agents import (
    AGENTS_REGISTRY,
    DEFAULT_AGENT_ID,
    get_agent_config,
    get_agent_tool_names,
    get_default_agent,
    load_agent_instructions,
    load_agent_tools,
)

__all__ = [
    "AGENTS_REGISTRY",
    "DEFAULT_AGENT_ID",
    "get_agent_config",
    "get_agent_tool_names",
    "get_default_agent",
    "load_agent_instructions",
    "load_agent_tools",
]
