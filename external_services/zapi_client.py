# -*- coding: utf-8 -*-
"""
Cliente Z-API para envio de mensagens WhatsApp (SDR interno).

Documentação: https://developer.z-api.io/
Enviar texto: POST /instances/{instanceId}/token/{token}/send-text
"""
from __future__ import annotations

import logging
import re
from typing import Any

import requests

from config.settings import ZAPI_BASE_URL, ZAPI_INSTANCE_ID, ZAPI_TOKEN_INSTANCE, ZAPI_CLIENT_TOKEN

logger = logging.getLogger(__name__)


def _normalize_phone(phone: str) -> str:
    """Normaliza telefone para formato Z-API: apenas dígitos (DDI + DDD + número)."""
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("0"):
        digits = digits[1:]
    if len(digits) >= 10 and not digits.startswith("55"):
        digits = "55" + digits
    return digits


def send_text(phone: str, message: str) -> bool:
    """
    Envia mensagem de texto via Z-API para o número indicado.

    Args:
        phone: Número no formato 5541999999999 ou +55 41 99999-9999.
        message: Texto da mensagem.

    Returns:
        True se enviado com sucesso, False caso contrário.
    """
    if not ZAPI_INSTANCE_ID or not ZAPI_TOKEN_INSTANCE:
        logger.warning("Z-API não configurada (ZAPI_INSTANCE_ID ou ZAPI_TOKEN_INSTANCE vazios). Mensagem não enviada.")
        return False

    phone_norm = _normalize_phone(phone)
    if len(phone_norm) < 10:
        logger.warning("Número de telefone inválido: %s", phone)
        return False

    url = f"{ZAPI_BASE_URL.rstrip('/')}/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN_INSTANCE}/send-text"
    payload = {"phone": phone_norm, "message": message}
    headers = {"Content-Type": "application/json"}
    if ZAPI_CLIENT_TOKEN:
        headers["Client-Token"] = ZAPI_CLIENT_TOKEN.strip()

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        if resp.ok:
            logger.info("Z-API: mensagem enviada para %s", phone_norm)
            return True
        logger.warning("Z-API: falha ao enviar (%s) %s", resp.status_code, resp.text[:200])
        return False
    except Exception as e:
        logger.exception("Z-API: erro ao enviar mensagem: %s", e)
        return False


def _extract_phone(data: dict, payload: dict) -> str:
    """Extrai telefone de data e payload (phoneId, phone, from, remoteJid, key.remoteJid)."""
    key_obj = data.get("key") or payload.get("key") or {}
    phone = (
        data.get("phoneId")
        or data.get("phone")
        or data.get("from")
        or data.get("participant")
        or data.get("sender")
        or data.get("remoteJid")
        or key_obj.get("remoteJid")
        or payload.get("phoneId")
        or payload.get("phone")
        or payload.get("from")
        or payload.get("participant")
        or payload.get("sender")
        or payload.get("remoteJid")
        or ""
    )
    if isinstance(phone, str) and "@" in phone:
        phone = phone.split("@")[0]
    return (phone or "").strip()


def _extract_text(data: dict, payload: dict) -> str:
    """Extrai texto da mensagem (message.conversation, message.extendedTextMessage.text, body, text, etc.)."""
    # String direta
    for k in ("message", "text", "body", "content"):
        v = data.get(k) or payload.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    # Objeto message (WhatsApp Web / Z-API)
    msg = data.get("message") or payload.get("message") or {}
    if isinstance(msg, str) and msg.strip():
        return msg.strip()
    if isinstance(msg, dict):
        # conversation (texto simples)
        conv = msg.get("conversation")
        if isinstance(conv, str) and conv.strip():
            return conv.strip()
        # extendedTextMessage
        ext = msg.get("extendedTextMessage") or msg.get("extendedTextMessageData")
        if isinstance(ext, dict) and ext.get("text"):
            return str(ext["text"]).strip()
        if isinstance(ext, dict) and ext.get("message"):
            return str(ext["message"]).strip()
        for k in ("text", "body", "content", "message"):
            v = msg.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
    # text/message como objeto
    text_obj = data.get("text") or data.get("message") or payload.get("text") or payload.get("message") or {}
    if isinstance(text_obj, str) and text_obj.strip():
        return text_obj.strip()
    if isinstance(text_obj, dict):
        for k in ("message", "body", "text", "content"):
            v = text_obj.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        if isinstance(text_obj.get("message"), dict):
            return (text_obj["message"].get("text") or text_obj["message"].get("body") or "").strip() or ""
    return ""


def parse_webhook_message(payload: dict[str, Any]) -> tuple[str, str] | None:
    """
    Extrai telefone e texto da mensagem recebida no webhook Z-API (on-message-received).

    Suporta: phoneId, phone, from, remoteJid, key.remoteJid; texto em message.conversation,
    message.extendedTextMessage.text, body, text, message (string/objeto).
    Doc: https://developer.z-api.io/webhooks/on-message-received

    Returns:
        (phone, text) ou None se não for mensagem de texto recebida.
    """
    if not payload:
        logger.debug("parse_webhook_message: payload vazio")
        return None

    data = payload.get("data") or payload
    if not isinstance(data, dict):
        data = payload

    # fromMe: ignorar mensagens enviadas por nós (pode estar em key ou root)
    key_obj = data.get("key") or payload.get("key") or {}
    from_me = data.get("fromMe") or payload.get("fromMe") or key_obj.get("fromMe")
    if from_me is True:
        logger.debug("parse_webhook_message: ignorando fromMe")
        return None

    phone = _extract_phone(data, payload)
    if not phone:
        logger.warning("parse_webhook_message: telefone não encontrado. Chaves: %s", list(payload.keys()))
        return None

    text = _extract_text(data, payload)
    if not text:
        logger.debug("parse_webhook_message: texto vazio (pode ser mídia). Chaves data: %s", list(data.keys()) if isinstance(data, dict) else data)
        return None
    return (phone, text)
