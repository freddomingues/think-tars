---
name: architecture-demos-flow
description: Fluxo das demos no generative-ai — run_turn, send_message, allowed_tool_names, tool dispatch, criação de conversa. Use ao debugar ou alterar o fluxo mensagem → assistente → tools → resposta. Triggers: "fluxo demos", "run_turn", "send_message", "tool dispatch", "requires_action", "allowed_tool_names".
---

# Skill: Fluxo das demos

Como uma **mensagem do usuário** vira **resposta do assistente** nas demos: criação de conversa, envio de mensagem, run do assistant, tool calls com isolamento.

---

## 1. Criação de conversa

1. Frontend chama `POST /api/demos/conversations` (ou `POST /api/demos/upload-pdf` se houver PDF).
2. **backend/services.create_conversation(agent_id, vector_store_id):**
   - Se `vector_store_id`: cria assistente OpenAI customizado (instruções + tools do agente + file_search) e associa ao vector store.
   - Senão: obtém `assistant_id` via `create_or_get_assistant_from_registry(agent_id)`.
   - Cria thread OpenAI (`client.beta.threads.create()`).
   - Guarda em memória: `conversation_id` → `{ thread_id, assistant_id, agent_id, vector_store_id?, is_custom? }`.
   - Retorna `{ conversation_id, thread_id, agent_id, vector_store_id? }`.

---

## 2. Envio de mensagem

1. Frontend chama `POST /api/demos/conversations/:id/messages` com `{ content }`.
2. **backend/services.send_message(conversation_id, content):**
   - Recupera conversa (thread_id, assistant_id, **agent_id**).
   - Calcula **allowed_tool_names = get_agent_tool_names(agent_id)** (isolamento).
   - Chama **ai.assistant_run.run_turn(client, thread_id, assistant_id, user_message=content, allowed_tool_names=allowed_tool_names)**.
   - Retorna `{ message }` (texto da resposta) ou `{ error }`.

---

## 3. Run do assistant (`ai/assistant_run.run_turn`)

1. Adiciona mensagem do usuário na thread (`client.beta.threads.messages.create`).
2. Cria run (`client.beta.threads.runs.create`).
3. Loop enquanto status in (`queued`, `in_progress`, `requires_action`):
   - Se **requires_action:** para cada tool call, chama **dispatch_tool_call(name, args, allowed_tool_names=allowed_tool_names)**; envia outputs com `submit_tool_outputs`; atualiza run.
   - Senão: aguarda 1s e recupera run.
4. Quando status == `completed`, busca última mensagem do assistente e retorna o texto.

---

## 4. Tool dispatch (`ai/tools/dispatch.dispatch_tool_call`)

- Se **allowed_tool_names** não for None e **function_name** não estiver em allowed_tool_names → retorna mensagem "Função X não está disponível para este assistente" (não executa).
- Senão: resolve função em **AVAILABLE_FUNCTIONS** (`ai/tools/base.py`), aplica assinaturas específicas (search_*, query_spreadsheet, buy/sell_bitcoin, etc.) e retorna o resultado como string.

Isolamento: cada assistente só pode executar as tools do seu agente (lista em ai/agents via get_agent_tool_names).

---

## 5. Referências

- **Isolamento:** `.cursor/skills/assistant-engineer/references/isolamento-e-escopo.md`.
- **Backend:** skills **backend-api-demos**, **backend-services-demos**.

---

## 6. Respostas

- Responder em **português** ao usuário.
