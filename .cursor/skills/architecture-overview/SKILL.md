---
name: architecture-overview
description: Visão geral da arquitetura do think-tars — princípios, mapa de camadas, tabela "onde mudar o quê", convenções. Use quando precisar saber ONDE fazer uma mudança ou entender o projeto como um todo. Triggers: "onde mudar", "onde fica", "estrutura do projeto", "arquitetura geral", "mapa do projeto".
---

# Skill: Visão geral da arquitetura

Referência rápida para **localizar** onde fazer mudanças no projeto think-tars. Para detalhes por área, use as skills específicas (architecture-registries, architecture-layers, architecture-demos-flow, backend-*, frontend-*).

---

## 1. Princípios

- **Config centralizada:** `config/settings.py` (env), `config/agents.py` (re-export de ai.agents), `config/automations.py`. Nada hardcoded.
- **Agentes em `ai/`:** Registry, prompts, tools, manager, run, Pinecone, trading, sentimento. Um assistente = um prompt + um conjunto de tools (isolamento obrigatório).
- **Demos:** Backend em `backend/` (rotas `/api/demos`), frontend em `frontend/` (React/Vite), servido em `/demos` pelo Flask.
- **Convenções:** Logging `config.logging_config`, scripts em `scripts/`, comentários em português quando for negócio.

---

## 2. Onde mudar o quê (tabela)

| Objetivo | Onde | Skill detalhada |
|----------|------|------------------|
| Novo agente (prompt + tools) | `ai/agents.py` + `ai/prompts/` + `ai/tools/` | assistant-engineer, assistant-creator |
| Nova tool de um agente | `ai/tools/<agente>.py` + `ai/tools/base.py` + opcionalmente `dispatch.py` | assistant-engineer |
| Nova rota ou endpoint de demos | `backend/routes.py` + `backend/services.py` | backend-api-demos, backend-services-demos |
| Registrar blueprint no Flask | `app/main.py` | backend-flask-app |
| Nova tela ou componente de demos | `frontend/src/` (ex.: App.jsx) | frontend-demos-structure, frontend-ui-chat |
| Nova chamada à API no frontend | `frontend/src/App.jsx` (ou camada de API) | frontend-api-demos |
| Config / variáveis de ambiente | `config/settings.py` e `.env` | architecture-registries |
| Fluxo demos (run_turn, dispatch) | `ai/assistant_run.py`, `ai/tools/dispatch.py`, `backend/services.py` | architecture-demos-flow |
| Build e servir frontend | `frontend/` (npm run build), `app/main.py` (/demos) | frontend-build-serve |

---

## 3. Mapa de camadas (resumido)

| Camada | Diretório | Responsabilidade |
|--------|-----------|------------------|
| Entrypoints | `app/main.py`, `scripts/` | HTTP, API de demos, CLI. |
| Backend demos | `backend/` | Rotas e serviços `/api/demos`. |
| Frontend demos | `frontend/` | SPA React+Vite em `/demos`. |
| Config | `config/` | Settings, re-export agents, automations. |
| Agentes | `ai/` | Registry, prompts, tools, manager, run, Pinecone, trading, sentimento. |
| Ingestão | `ingest/`, `data_ingestion/` | Busca Pinecone, PDFs (vector store). |
| Dados | `data_store/` | Conversas/threads em memória. |
| Externos | `external_services/` | Binance, etc. |

Detalhes: skill **architecture-layers**.

---

## 4. Documentação

- **AGENTS.md** — Mapa completo do repositório para IAs; consultar primeiro.
- **docs/ARCHITECTURE.md** — Arquitetura detalhada, fluxos.
- **docs/COMO_USAR_DEMOS.md** — Uso da interface de demos.

---

## 5. Respostas

- Responder em **português** ao usuário.
