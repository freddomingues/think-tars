# -*- coding: utf-8 -*-
"""
Registry de automações (compatibilidade).
O projeto não executa mais jobs automatizados por cron; o registry fica vazio.
"""
from typing import Any, Callable

AUTOMATIONS_REGISTRY: list[dict[str, Any]] = []


def get_automation(automation_id: str) -> dict[str, Any] | None:
    """Retorna configuração da automação por id."""
    for a in AUTOMATIONS_REGISTRY:
        if a["id"] == automation_id:
            return a
    return None


def get_automation_handler(automation_id: str) -> Callable | None:
    """Resolve e retorna o callable handler da automação."""
    cfg = get_automation(automation_id)
    if not cfg:
        return None
    import importlib
    mod = importlib.import_module(cfg["handler_module"])
    fn = getattr(mod, cfg["handler_attr"], None)
    if not callable(fn):
        return None
    kwargs = cfg.get("handler_kwargs") or {}

    def _run(*args: Any, **kw: Any) -> Any:
        return fn(*args, **{**kwargs, **kw})

    return _run
