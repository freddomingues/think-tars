# API de demos — resumo

## Base URL

`/api/demos`

## Endpoints

### GET /assistants

Retorna lista de assistentes disponíveis.

**Resposta:** `{ "assistants": [ { "id": "juridico", "name": "..." }, ... ] }`

---

### POST /upload-pdf

Upload de PDF + criação de vector store + criação de conversa. Multipart/form-data: `file` (PDF), `agent_id` (opcional).

**Resposta (201):** `{ "conversation_id": "...", "vector_store_id": "...", "agent_id": "...", ... }`

**Erros:** 400 (sem arquivo / nome vazio / não-PDF), 500.

---

### POST /conversations

Cria nova conversa (thread) para um assistente.

**Body (opcional):** `{ "agent_id": "juridico", "vector_store_id": "vs_xxx" }` — default agent: `juridico`.

**Resposta (201):** `{ "conversation_id": "...", "thread_id": "...", "agent_id": "...", "vector_store_id"?: "..." }`

**Erro (500):** `{ "error": "..." }`

---

### POST /conversations/:id/messages

Envia mensagem na conversa e retorna resposta do assistente.

**Body:** `{ "content": "sua mensagem aqui" }`

**Resposta (200):** `{ "message": "resposta do assistente" }` ou `{ "error": "..." }` (502)

**Erros:**
- 400: `{ "error": "Campo 'content' é obrigatório." }`
- 404: `{ "error": "Conversa não encontrada." }`
- 502: `{ "error": "..." }` (falha no run)

---

### DELETE /conversations/:id

Deleta uma conversa e seus recursos (assistente customizado, vector store, se houver).

**Resposta (200):** `{ "message": "Conversa deletada com sucesso." }`

**Erro (404):** `{ "error": "Conversa não encontrada ou erro ao limpar recursos." }`
