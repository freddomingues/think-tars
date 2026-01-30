# -*- coding: utf-8 -*-
"""
Pacote AI: agentes, prompts, tools e core (assistente, clientes, Pinecone).
"""
from ai.assistant_manager import (
    create_or_get_assistant,
    create_or_get_assistant_from_registry,
    update_assistant_instructions,
    list_all_assistants,
    delete_assistant,
    get_assistant_tools,
)
from ai.assistant_run import run_turn
from ai.tools.dispatch import dispatch_tool_call
from ai.clients import (
    get_chroma_client_contract,
    get_chroma_client_faqs,
    get_embedding_model,
)

__all__ = [
    "create_or_get_assistant",
    "create_or_get_assistant_from_registry",
    "update_assistant_instructions",
    "list_all_assistants",
    "delete_assistant",
    "get_assistant_tools",
    "run_turn",
    "dispatch_tool_call",
    "get_chroma_client_contract",
    "get_chroma_client_faqs",
    "get_embedding_model",
]
