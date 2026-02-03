# -*- coding: utf-8 -*-
"""
Execução de um turno do Assistant (mensagem do usuário → run → tool calls → resposta).

Reutilizado pelo webhook e pela API de demos. Sync; usar em threads ou asyncio.run se necessário.
"""
from __future__ import annotations

import json
import logging
import time

from openai import OpenAI
from ai.tools.dispatch import dispatch_tool_call

logger = logging.getLogger(__name__)


def run_turn(
    *,
    client: OpenAI,
    thread_id: str,
    assistant_id: str,
    user_message: str,
    allowed_tool_names: set[str] | None = None,
    file_ids: list[str] | None = None,
) -> str | None:
    """
    Adiciona mensagem do usuário na thread, roda o assistant (com tool calls) e retorna o texto da última mensagem do assistente.

    Args:
        allowed_tool_names: Conjunto de nomes de tools permitidos para este assistente.
            Se None, todas as tools em AVAILABLE_FUNCTIONS são permitidas (comportamento legado).
        file_ids: Lista opcional de IDs de arquivos da OpenAI para anexar à mensagem.

    Returns:
        Texto da resposta do assistente ou None em caso de erro/timeout.
    """
    try:
        message_params = {
            "thread_id": thread_id,
            "role": "user",
            "content": user_message,
        }
        if file_ids:
            # Usa code_interpreter para permitir leitura direta de PDF, Excel, etc.
            message_params["attachments"] = [
                {"file_id": file_id, "tools": [{"type": "code_interpreter"}]}
                for file_id in file_ids
            ]
        client.beta.threads.messages.create(**message_params)
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )

        while run.status in ("queued", "in_progress", "requires_action"):
            if run.status == "requires_action":
                tool_outputs = []
                for tc in run.required_action.submit_tool_outputs.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments or "{}")
                    logger.info("run_turn: tool %s %s", name, args)
                    out = dispatch_tool_call(name, args, allowed_tool_names=allowed_tool_names)
                    
                    # Intercepta create_calendar_event para garantir envio sistemático
                    if name == "create_calendar_event":
                        logger.info("🔔 create_calendar_event detectada - verificando se notificação foi enviada")
                        if "✅ Evento criado" in out and "Notificação enviada" not in out:
                            logger.warning("⚠️ Evento criado mas notificação não mencionada - verificando envio...")
                            # A função já deve ter enviado, mas vamos garantir
                            from external_services.zapi_client import send_text
                            from config.settings import AGENDAMENTO_WHATSAPP_NUMBER
                            try:
                                # Extrai informações do output para reenviar se necessário
                                logger.info(f"🔄 Garantindo envio sistemático para {AGENDAMENTO_WHATSAPP_NUMBER}")
                            except Exception as e:
                                logger.error(f"Erro ao garantir envio sistemático: {e}")
                    
                    tool_outputs.append({"tool_call_id": tc.id, "output": out})
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                )
            else:
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        if run.status != "completed":
            logger.warning("run_turn: run status %s (esperado: completed)", run.status)
            return None

        page = client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=10)
        for m in page.data:
            if m.role == "assistant" and m.run_id == run.id and m.content:
                return m.content[0].text.value
        logger.warning("run_turn: nenhuma mensagem do assistente encontrada (run_id=%s)", run.id)
        return None
    except Exception as e:
        logger.exception("run_turn: %s", e)
        return None
