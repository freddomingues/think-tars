# -*- coding: utf-8 -*-
"""
Serviços da API de demos: listar assistentes, criar conversa, enviar mensagem.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from openai import OpenAI

from ai.agents import AGENTS_REGISTRY, get_agent_tool_names
from config.settings import OPENAI_API_KEY, LLM_MODEL
from ai.assistant_manager import create_or_get_assistant_from_registry
from ai.assistant_run import run_turn
from data_ingestion.pdf_processor import create_vector_store_from_pdf

logger = logging.getLogger(__name__)

_openai_client: OpenAI | None = None
_agent_id_to_assistant_id: dict[str, str] = {}
_conversations: dict[str, dict[str, Any]] = {}  # conversation_id -> { thread_id, assistant_id, vector_store_id, agent_id }


def _client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def _assistant_id_for_agent(agent_id: str) -> str | None:
    if agent_id not in _agent_id_to_assistant_id:
        a_id = create_or_get_assistant_from_registry(agent_id)
        if not a_id:
            return None
        _agent_id_to_assistant_id[agent_id] = a_id
    return _agent_id_to_assistant_id[agent_id]


def list_assistants() -> list[dict[str, str]]:
    """Lista assistentes disponíveis no Playground (apenas agentes com playground=True)."""
    assistants = [
        {"id": a["id"], "name": a["name"]}
        for a in AGENTS_REGISTRY
        if a.get("playground", True)
    ]
    logger.info(f"📋 Listando {len(assistants)} assistentes do Playground: {[a['id'] for a in assistants]}")
    return assistants


def create_conversation(agent_id: str | None = None, vector_store_id: str | None = None) -> dict[str, Any] | None:
    """
    Cria uma nova conversa (thread) para o agente indicado.
    Se agent_id for None, usa o agente padrão (juridico).
    Se vector_store_id for fornecido, cria um assistente específico com esse vector store.
    """
    from ai.agents import DEFAULT_AGENT_ID, get_agent_config, load_agent_instructions, load_agent_tools

    aid = agent_id or DEFAULT_AGENT_ID
    
    # Se houver vector store, cria assistente específico para esta conversa
    if vector_store_id:
        cfg = get_agent_config(aid)
        if not cfg:
            return None
        instructions = load_agent_instructions(aid)
        tools = load_agent_tools(aid)
        if instructions is None or tools is None:
            return None
        
        # Adiciona file_search tool se ainda não estiver presente
        tools_with_search = list(tools)
        has_file_search = any(t.get("type") == "file_search" for t in tools_with_search)
        if not has_file_search:
            tools_with_search.append({"type": "file_search"})
        
        # Cria assistente específico com vector store
        try:
            assistant = _client().beta.assistants.create(
                name=f"{cfg['name']} (Custom)",
                instructions=instructions,
                model=LLM_MODEL,
                tools=tools_with_search,
                tool_resources={
                    "file_search": {
                        "vector_store_ids": [vector_store_id]
                    }
                }
            )
            assistant_id = assistant.id
            logger.info(f"Assistente customizado criado: {assistant_id} com vector store {vector_store_id}")
        except Exception as e:
            logger.error(f"Erro ao criar assistente customizado: {e}")
            return None
    else:
        # Usa assistente padrão do registry
        assistant_id = _assistant_id_for_agent(aid)
        if not assistant_id:
            return None
    
    thread = _client().beta.threads.create()
    cid = str(uuid.uuid4())
    _conversations[cid] = {
        "thread_id": thread.id,
        "assistant_id": assistant_id,
        "agent_id": aid,
        "vector_store_id": vector_store_id,
        "is_custom": vector_store_id is not None
    }
    return {
        "conversation_id": cid,
        "thread_id": thread.id,
        "agent_id": aid,
        "vector_store_id": vector_store_id
    }


def send_message(conversation_id: str, content: str, file_ids: list[str] | None = None) -> dict[str, Any] | None:
    """
    Envia mensagem na conversa, executa o assistant e retorna a resposta.
    Só são executadas as tools do agente da conversa (isolamento por assistente).
    
    Args:
        conversation_id: ID da conversa
        content: Conteúdo da mensagem
        file_ids: Lista opcional de IDs de arquivos da OpenAI para anexar à mensagem
    """
    conv = _conversations.get(conversation_id)
    if not conv:
        return None
    agent_id = conv.get("agent_id")
    allowed_tool_names = get_agent_tool_names(agent_id) if agent_id else None
    text = run_turn(
        client=_client(),
        thread_id=conv["thread_id"],
        assistant_id=conv["assistant_id"],
        user_message=content,
        allowed_tool_names=allowed_tool_names,
        file_ids=file_ids,
    )
    if text is None:
        return {"error": "Não foi possível obter resposta do assistente."}
    return {"message": text}


def upload_pdf_and_create_vector_store(pdf_bytes: bytes, filename: str, conversation_id: str) -> str | None:
    """
    Faz upload de um PDF e cria um vector store.
    
    Args:
        pdf_bytes: Bytes do arquivo PDF
        filename: Nome do arquivo
        conversation_id: ID da conversa
    
    Returns:
        ID do vector store criado ou None em caso de erro
    """
    return create_vector_store_from_pdf(_client(), pdf_bytes, filename, conversation_id)


def cleanup_conversation(conversation_id: str) -> bool:
    """
    Limpa recursos de uma conversa (assistente customizado e vector store).
    
    Args:
        conversation_id: ID da conversa
    
    Returns:
        True se limpeza foi bem sucedida, False caso contrário
    """
    conv = _conversations.get(conversation_id)
    if not conv:
        return False
    
    try:
        # Se for assistente customizado, deleta
        if conv.get("is_custom"):
            try:
                _client().beta.assistants.delete(conv["assistant_id"])
                logger.info(f"Assistente customizado deletado: {conv['assistant_id']}")
            except Exception as e:
                logger.warning(f"Erro ao deletar assistente: {e}")
        
        # Se houver vector store, deleta
        if conv.get("vector_store_id"):
            try:
                _client().beta.vector_stores.delete(conv["vector_store_id"])
                logger.info(f"Vector store deletado: {conv['vector_store_id']}")
            except Exception as e:
                logger.warning(f"Erro ao deletar vector store: {e}")
        
        # Remove da memória
        del _conversations[conversation_id]
        return True
    except Exception as e:
        logger.error(f"Erro ao limpar conversa: {e}")
        return False


def get_client() -> OpenAI:
    """Retorna o cliente OpenAI (para uso pelo blueprint)."""
    return _client()
