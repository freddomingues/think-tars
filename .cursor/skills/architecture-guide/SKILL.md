---
name: architecture-guide
description: Índice do guia de arquitetura do think-tars. Use para orientar onde encontrar detalhes: visão geral, registries, camadas, fluxo demos. Triggers: "arquitetura", "escalar agentes", "novo agente", "backend", "frontend", "demos", "registry", "tool dispatch", "config agents".
---

# Skill: Guia de arquitetura (índice)

Referência para **manter e escalar** a arquitetura do think-tars. Esta skill funciona como **índice**: para detalhes, use as skills específicas listadas abaixo.

---

## 1. Princípios (resumo)

- **Config centralizada:** `config/settings.py` (env), `config/agents.py` (re-export de `ai.agents`), `config/automations.py`. Nada hardcoded.
- **Agentes em `ai/`:** Registry, prompts, tools, manager, run, Pinecone, trading, sentimento. Um assistente = um prompt + um conjunto de tools (isolamento obrigatório).
- **Demos:** Backend em `backend/` (rotas `/api/demos`), frontend em `frontend/` (React/Vite), servido em `/demos` pelo Flask.
- **Convenções:** Logging `config.logging_config`, scripts em `scripts/`, comentários em português quando for negócio.

---

## 2. Skills de arquitetura (use conforme o cenário)

| Cenário | Skill |
|---------|--------|
| Onde mudar o quê / mapa do projeto / estrutura geral | **architecture-overview** |
| Registry de agentes, config, settings, automations | **architecture-registries** |
| Camadas e fronteiras (entrypoints, backend, frontend, ai, ingest, dados) | **architecture-layers** |
| Fluxo das demos (run_turn, send_message, allowed_tool_names, tool dispatch) | **architecture-demos-flow** |

---

## 3. Skills de backend

| Cenário | Skill |
|---------|--------|
| Endpoints da API de demos (GET/POST/DELETE) | **backend-api-demos** |
| Serviços (list_assistants, create_conversation, send_message, upload PDF, cleanup) | **backend-services-demos** |
| App Flask, registro de blueprints, servir /demos | **backend-flask-app** |
| Adicionar nova rota ou serviço | **backend-new-route** |

Ver também **backend-developer** (visão geral do backend).

---

## 4. Skills de frontend

| Cenário | Skill |
|---------|--------|
| Estrutura de pastas, App.jsx, index.css | **frontend-demos-structure** |
| Chamadas fetch à API de demos | **frontend-api-demos** |
| UI do chat (sidebar, mensagens, input, upload PDF) | **frontend-ui-chat** |
| Build (npm run build) e servir (Flask /demos, Vite dev) | **frontend-build-serve** |

Ver também **frontend-developer** (visão geral do frontend).

---

## 5. Agentes e tools

| Cenário | Skill |
|---------|--------|
| Isolamento, prompts, tools, registry (ai/) | **assistant-engineer** |
| Criar novo assistente (instruções, tools, registry) | **assistant-creator** |
| SDR WhatsApp (Z-API, webhook, agente interno) | **sdr-zapi** |
| Testes locais do backend (webhook SDR, Playground) | **testing-local-backend** |

---

## 6. Documentação

- **AGENTS.md** — Mapa completo do repositório para IAs; consultar primeiro.
- **docs/ARCHITECTURE.md** — Arquitetura detalhada, fluxos.
- **docs/COMO_USAR_DEMOS.md** — Uso da interface de demos.

---

## 7. Respostas

Responder em **português** ao usuário.
