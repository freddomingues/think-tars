---
name: backend-services-demos
description: Serviços da API de demos do think-tars — list_assistants, create_conversation, send_message, upload_pdf_and_create_vector_store, cleanup_conversation. Use ao alterar lógica de negócio das demos. Triggers: "services demos", "create_conversation", "send_message", "run_turn", "allowed_tool_names".
---

# Skill: Serviços de demos

Lógica de negócio da API de demos em `backend/services.py`: listar assistentes, criar conversa (com ou sem PDF), enviar mensagem com isolamento de tools, limpar conversa.

---

## 1. Módulo e dependências

- **Arquivo:** `backend/services.py`
- **Imports principais:** `ai.agents` (AGENTS_REGISTRY, get_agent_tool_names), `ai.assistant_manager` (create_or_get_assistant_from_registry), `ai.assistant_run` (run_turn), `data_ingestion.pdf_processor` (create_vector_store_from_pdf), `config.settings` (OPENAI_API_KEY, LLM_MODEL).

---

## 2. Funções principais

| Função | Retorno | Descrição |
|--------|---------|-----------|
| `list_assistants()` | `[{ "id", "name" }]` | Lista a partir de `AGENTS_REGISTRY`. |
| `create_conversation(agent_id=None, vector_store_id=None)` | `{ conversation_id, thread_id, agent_id, ... }` ou `None` | Se `vector_store_id`: cria assistente OpenAI com file_search; senão usa assistente do registry. Cria thread, guarda em `_conversations`. |
| `send_message(conversation_id, content)` | `{ "message": str }` ou `{ "error": str }` ou `None` (404) | Obtém `agent_id` da conversa; calcula `allowed_tool_names = get_agent_tool_names(agent_id)`; chama `run_turn(..., allowed_tool_names=allowed_tool_names)`. |
| `upload_pdf_and_create_vector_store(pdf_bytes, filename, conversation_id)` | `vector_store_id` ou `None` | Processa PDF via `create_vector_store_from_pdf`, retorna ID do vector store. |
| `cleanup_conversation(conversation_id)` | `bool` | Remove conversa; se assistente customizado/vector store, tenta deletar na OpenAI. |

---

## 3. Estado em memória

- **`_conversations`:** `conversation_id` → `{ thread_id, assistant_id, agent_id, vector_store_id?, is_custom? }`.
- **`_agent_id_to_assistant_id`:** cache de agent_id → assistant_id (registry).

---

## 4. Isolamento de tools

- `send_message` obtém `agent_id` da conversa e chama `get_agent_tool_names(agent_id)`.
- Passa `allowed_tool_names` para `run_turn`; o dispatch em `ai/tools/dispatch.py` bloqueia tools não permitidas.
- Ver skill **assistant-engineer** (isolamento) e **architecture-demos-flow** (fluxo run_turn → dispatch).

---

## 5. Onde alterar

- **Nova ação de demos:** nova função em `services.py`; rota em `backend/routes.py` (skill **backend-api-demos**).
- **Mudar fluxo de conversa/PDF:** `create_conversation`, `upload_pdf_and_create_vector_store`.
- **Mudar envio de mensagem:** `send_message`, `run_turn` em `ai/assistant_run.py`.

---

## 6. Referências

- **Endpoints:** skill **backend-api-demos**.
- **Fluxo run_turn e dispatch:** skill **architecture-demos-flow**, **assistant-engineer**.

---

## 7. Respostas

Responder em **português** ao usuário.
