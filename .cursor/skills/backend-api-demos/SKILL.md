---
name: backend-api-demos
description: Endpoints da API de demos do think-tars — GET assistants, POST conversations, POST messages, POST upload-pdf, DELETE conversation. Use ao consultar ou alterar contratos da API de demos. Triggers: "API demos", "endpoint", "rota demos", "upload-pdf", "conversations", "messages".
---

# Skill: API de demos (endpoints)

Referência dos **endpoints** da API de demos: Blueprint em `/api/demos`, rotas em `backend/routes.py`.

---

## 1. Base e Blueprint

- **Base URL:** `/api/demos`
- **Blueprint:** `backend/routes.py` — `bp = Blueprint("demos", __name__, url_prefix="/api/demos")`
- **Registro:** `register_demo_routes(app)` em `app/main.py`; CORS em `/api/demos/*` quando flask_cors disponível.

---

## 2. Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/assistants` | Lista assistentes (registry). Resposta: `{ "assistants": [ { "id", "name" } ] }`. |
| `POST` | `/upload-pdf` | Upload de PDF + criação de vector store + conversa. Form: `file`, `agent_id` (opcional). Resposta (201): `{ conversation_id, vector_store_id, agent_id, ... }`. Erros: 400 (sem arquivo/nome vazio/não-PDF), 500. |
| `POST` | `/conversations` | Cria conversa. Body: `{ "agent_id"?: string, "vector_store_id"?: string }`. Resposta (201): `{ conversation_id, thread_id, agent_id, vector_store_id? }`. Erro 500. |
| `POST` | `/conversations/<conversation_id>/messages` | Envia mensagem. Body: `{ "content": string }`. Resposta (200): `{ "message": string }` ou `{ "error": string }` (502). Erros: 400 (content vazio), 404 (conversa não encontrada). |
| `DELETE` | `/conversations/<conversation_id>` | Deleta conversa e recursos (assistente customizado, vector store). Resposta (200): `{ "message": "..." }`. Erro 404. |

---

## 3. Onde alterar

- **Novo endpoint de demos:** adicionar `@bp.route(...)` em `backend/routes.py`; lógica em `backend/services.py`.
- **Contrato (body/query/response):** documentar aqui e em `backend-developer/references/api-demos.md`; frontend em `frontend-api-demos`.

---

## 4. Referências

- **Serviços:** skill **backend-services-demos**.
- **Registrar no Flask:** skill **backend-flask-app**.
- **Resumo API:** `.cursor/skills/backend-developer/references/api-demos.md`.

---

## 5. Respostas

Responder em **português** ao usuário.
