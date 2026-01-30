# -*- coding: utf-8 -*-
"""
Webhook Z-API para receber mensagens WhatsApp e responder com o assistente SDR.

Configure na Z-API a URL: https://seu-dominio/api/zapi/webhook
Evento: Ao receber mensagem (on-message-received).

Todas as mensagens recebidas são registradas em logs/zapi_webhook.log.
"""
import json
import logging
from flask import Blueprint, request, jsonify

from backend.sdr_services import run_sdr_turn
from backend.webhook_logger import (
    log_webhook_received,
    log_webhook_parsed,
    log_webhook_parse_failed,
    log_webhook_reply,
)
from external_services.zapi_client import parse_webhook_message, send_text

logger = logging.getLogger(__name__)

bp = Blueprint("zapi", __name__, url_prefix="/api/zapi")


def _log_payload(payload: dict, prefix: str = "Webhook Z-API") -> None:
    """Loga payload truncado no console para debug."""
    try:
        safe = json.dumps(payload, ensure_ascii=False, default=str)[:800]
        logger.info("%s payload (truncado): %s", prefix, safe)
    except Exception:
        logger.info("%s payload keys: %s", prefix, list(payload.keys()))


@bp.route("/webhook", methods=["POST"])
def webhook():
    """
    Recebe callback da Z-API quando uma mensagem é recebida.
    Processa com o agente SDR e envia a resposta de volta via Z-API.
    Todas as mensagens são registradas em logs/zapi_webhook.log.
    """
    raw_body = None
    try:
        raw_body = request.get_data(as_text=True) or ""
        payload = request.get_json(force=True, silent=True) or {}
    except Exception as e:
        logger.exception("Webhook Z-API: erro ao ler JSON: %s", e)
        payload = {}

    # Log persistente: toda mensagem recebida (payload completo)
    log_webhook_received(payload, raw_body)
    _log_payload(payload, "Webhook Z-API [received]")

    parsed = parse_webhook_message(payload)
    if not parsed:
        log_webhook_parse_failed(payload, "telefone ou texto não encontrado")
        _log_payload(payload, "Webhook Z-API (parse falhou)")
        logger.warning("Webhook Z-API: payload sem telefone/texto válido. Ver logs/zapi_webhook.log e ajuste parse_webhook_message.")
        return jsonify({"ok": True}), 200  # 200 para Z-API não reenviar

    phone, text = parsed
    if not text:
        return jsonify({"ok": True}), 200

    log_webhook_parsed(phone, text)
    logger.info("SDR: mensagem de %s: %s", phone, text[:80])

    reply = run_sdr_turn(phone, text)
    if reply:
        logger.info("SDR: resposta gerada (%s chars), enviando via Z-API", len(reply))
        ok = send_text(phone, reply)
        if not ok:
            logger.error("SDR: falha ao enviar resposta via Z-API para %s", phone)
        log_webhook_reply(phone, reply, sent=ok, error=None if ok else "Z-API send_text retornou False")
    else:
        logger.warning("SDR: run_sdr_turn retornou None, enviando fallback")
        fallback = "Obrigado pela mensagem. Em instantes nossa equipe retorna o contato."
        ok = send_text(phone, fallback)
        log_webhook_reply(phone, fallback, sent=ok, error="run_sdr_turn retornou None")

    return jsonify({"ok": True}), 200


@bp.route("/test-webhook", methods=["POST"])
def test_webhook():
    """
    Endpoint de teste local: simula uma mensagem recebida (sem Z-API chamar o servidor).

    Body: { "phone": "5541999999999", "message": "Olá, quero saber sobre IA" }
    - Processa com o SDR e envia a resposta via Z-API para o phone informado.
    - Use para testar o fluxo localmente: curl -X POST http://localhost:5004/api/zapi/test-webhook -H "Content-Type: application/json" -d '{"phone":"554187497364","message":"teste"}'
    """
    try:
        body = request.get_json(force=True, silent=True) or {}
    except Exception:
        body = {}
    phone = (body.get("phone") or "").strip()
    message = (body.get("message") or "").strip()
    if not phone or not message:
        return jsonify({"error": "Envie phone e message no body"}), 400

    logger.info("Test-webhook: phone=%s message=%s", phone, message[:80])
    reply = run_sdr_turn(phone, message)
    if not reply:
        return jsonify({"error": "run_sdr_turn retornou None", "phone": phone}), 502
    ok = send_text(phone, reply)
    return jsonify({
        "ok": ok,
        "phone": phone,
        "reply_preview": reply[:200] + ("..." if len(reply) > 200 else ""),
        "sent_via_zapi": ok,
    }), 200
