---
name: backend-developer
description: Visão geral do backend do think-tars — Flask, API de demos, serviços. Use para contexto geral; para cenários específicos use as skills granulares. Triggers: "backend", "API", "endpoint", "rota", "Flask", "demos API", "services", "backend developer".
---

# Skill: Backend Developer (visão geral)

Guia de **visão geral** do backend do think-tars. Para tarefas específicas, use as skills granulares listadas abaixo.

---

## 1. Stack e estrutura

- **Runtime:** Python 3.12+
- **Web:** Flask. App principal em `app/main.py`; blueprint de demos em `backend/routes.py`.
- **API de demos:** Blueprint em `/api/demos`. Registro via `register_demo_routes(app)` em `app/main.py`.

```
backend/
├── __init__.py      # expõe register_demo_routes
├── routes.py        # Blueprint, rotas /api/demos/*
└── services.py      # list_assistants, create_conversation, send_message, upload_pdf, cleanup
```

- **Config:** `config/settings.py`, `config/agents.py` (re-export de `ai.agents`).
- **Agentes:** `ai/` (manager, tools, dispatch, assistant_run). Serviços chamam `ai.assistant_manager`, `ai.assistant_run`, `ai.agents`.

---

## 2. Skills granulares (use conforme o cenário)

| Cenário | Skill |
|---------|--------|
| Endpoints da API de demos (contratos, métodos, rotas) | **backend-api-demos** |
| Lógica de negócio (create_conversation, send_message, upload PDF, cleanup) | **backend-services-demos** |
| App Flask, registro de blueprints, servir frontend em /demos | **backend-flask-app** |
| Adicionar nova rota ou novo blueprint | **backend-new-route** |

---

## 3. API de demos (resumo)

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/demos/assistants` | Lista assistentes (registry). |
| `POST` | `/api/demos/upload-pdf` | Upload PDF + vector store + conversa. |
| `POST` | `/api/demos/conversations` | Cria conversa. Body opcional: `{ "agent_id", "vector_store_id" }`. |
| `POST` | `/api/demos/conversations/<id>/messages` | Envia mensagem. Body: `{ "content": "..." }`. |
| `DELETE` | `/api/demos/conversations/<id>` | Deleta conversa e recursos. |

Respostas JSON. Erros: 400 (validação), 404 (conversa não encontrada), 502 (erro no run).

---

## 4. Referências

- **Detalhes da API:** `.cursor/skills/backend-developer/references/api-demos.md`.
- **Arquitetura:** skill **architecture-guide**, **architecture-overview**.
- **Agentes:** skill **assistant-creator**, **assistant-engineer**; `ai/agents.py`, `ai/`.

---

## 5. Respostas

Responder em **português** ao usuário.
