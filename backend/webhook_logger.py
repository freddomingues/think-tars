# -*- coding: utf-8 -*-
"""
Log persistente de todas as mensagens recebidas no webhook Z-API (SDR).

Registra em logs/zapi_webhook.log: cada POST recebido (payload completo),
resultado do parse (phone, text) e envio da resposta (ok/falha).
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

# Diretório de logs na raiz do projeto
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOG_DIR = os.path.join(_PROJECT_ROOT, "logs")
_LOG_FILE = os.path.join(_LOG_DIR, "zapi_webhook.log")


def _ensure_log_dir() -> None:
    os.makedirs(_LOG_DIR, exist_ok=True)


def _write_line(record: dict[str, Any]) -> None:
    _ensure_log_dir()
    try:
        line = json.dumps(
            {"ts": datetime.utcnow().isoformat() + "Z", **record},
            ensure_ascii=False,
            default=str,
        ) + "\n"
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass  # não quebrar o fluxo se o log falhar


def log_webhook_received(payload: dict[str, Any], raw_body: str | None = None) -> None:
    """Registra que um POST foi recebido no webhook (payload completo)."""
    _write_line({
        "event": "webhook_received",
        "payload": payload,
        "payload_keys": list(payload.keys()) if payload else [],
        "raw_body_preview": (raw_body or "")[:500] if raw_body else None,
    })


def log_webhook_parsed(phone: str, text: str) -> None:
    """Registra que o payload foi parseado com sucesso."""
    _write_line({
        "event": "webhook_parsed",
        "phone": phone,
        "text_preview": text[:300] + ("..." if len(text) > 300 else ""),
    })


def log_webhook_parse_failed(payload: dict[str, Any], reason: str) -> None:
    """Registra que o parse falhou."""
    _write_line({
        "event": "webhook_parse_failed",
        "reason": reason,
        "payload": payload,
        "payload_keys": list(payload.keys()) if payload else [],
    })


def log_webhook_reply(phone: str, reply_preview: str, sent: bool, error: str | None = None) -> None:
    """Registra envio da resposta (sucesso ou falha)."""
    _write_line({
        "event": "webhook_reply",
        "phone": phone,
        "reply_preview": reply_preview[:300] + ("..." if len(reply_preview) > 300 else ""),
        "sent": sent,
        "error": error,
    })


def get_webhook_log_path() -> str:
    """Retorna o caminho do arquivo de log (para exibir na doc/scripts)."""
    return _LOG_FILE
