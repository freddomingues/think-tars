# Camadas e registries (resumo)

## Camadas

```
Entrypoints (app, dashboard, scripts)
    ↓
Backend (demos) ────────────────────→ /api/demos
Frontend (demos) ───────────────────→ /demos (SPA)
    ↓
Config (settings, agents, automations)
    ↓
Agentes (ai/) / Trading (trading; sem cron)
    ↓
Ingestão, Dados, Externos, Sentimento
```

## Agents registry (`ai/agents.py`)

- `AGENTS_REGISTRY`: lista de `{ id, name, instructions_module, instructions_attr, tools_module, tools_attr }` (módulos em `ai.prompts.*`, `ai.tools.*`).
- `DEFAULT_AGENT_ID`: ex. `"juridico"`.
- Funções: `get_agent_config`, `load_agent_instructions`, `load_agent_tools`.

## Automations registry (`config/automations.py`)

- `AUTOMATIONS_REGISTRY`: lista de `{ id, name, route, methods, handler_module, handler_attr, handler_kwargs }`.
- Funções: `get_automation`, `get_automation_handler`.

## Tool dispatch (`ai/tools/dispatch.py`)

- `dispatch_tool_call(function_name, arguments)` → `str`.
- Usa `AVAILABLE_FUNCTIONS` de `ai/tools/base.py`. Novas tools: implementar em `ai/tools/` e, se necessário, branch no dispatch.
