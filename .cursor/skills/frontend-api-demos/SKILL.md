---
name: frontend-api-demos
description: Chamadas à API de demos no frontend do think-tars — fetch assistants, conversations, messages, upload-pdf. Use ao alterar contratos ou adicionar novas chamadas à API. Triggers: "fetch demos", "API frontend", "upload-pdf", "conversations", "messages".
---

# Skill: Chamadas à API de demos (frontend)

Como o frontend chama a API de demos: base URL, endpoints usados, tratamento de erros e loading.

---

## 1. Base URL

- **Constante:** `const API = '/api/demos'` (em `App.jsx`).
- Em produção o frontend é servido em `/demos`; chamadas são relativas (`/api/demos/...`).
- Em dev (Vite), configurar proxy em `vite.config.js`: `/api` → Flask (ex.: `http://127.0.0.1:5004`).

---

## 2. Endpoints usados

| Uso | Método e URL | Body / Form | Resposta / Erro |
|-----|--------------|-------------|-----------------|
| Listar assistentes | `GET ${API}/assistants` | — | `{ assistants: [ { id, name } ] }` |
| Criar conversa | `POST ${API}/conversations` | `{ agent_id? }` | `{ conversation_id, thread_id, agent_id, ... }` |
| Upload PDF e criar conversa | `POST ${API}/upload-pdf` | FormData: `file`, `agent_id?` | `{ conversation_id, vector_store_id, agent_id, ... }` |
| Enviar mensagem | `POST ${API}/conversations/:id/messages` | `{ content }` | `{ message }` ou `{ error }` |
| Deletar conversa | `DELETE ${API}/conversations/:id` | — | `{ message }` ou `{ error }` |

---

## 3. Onde está no código (App.jsx)

- **Assistants:** `useEffect` com `fetch(\`${API}/assistants\`)`; `setAssistants(d.assistants || [])`.
- **Iniciar conversa (sem PDF):** `fetch(\`${API}/conversations\`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ agent_id: selected }) })`.
- **Upload PDF:** `FormData` com `file` e `agent_id`; `fetch(\`${API}/upload-pdf\`, { method: 'POST', body: formData })`.
- **Enviar mensagem:** `fetch(\`${API}/conversations/${conversationId}/messages\`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content: text }) })`.
- **Deletar conversa:** (se implementado) `fetch(\`${API}/conversations/${conversationId}\`, { method: 'DELETE' })`.

---

## 4. Tratamento de erros e loading

- Antes de cada chamada: `setLoading(true)`, `setError(null)`.
- Após resposta: `await res.json()`; se `!res.ok` ou `d.error`, tratar com `setError(...)` ou `setMessages(..., isError: true)`.
- No `finally`: `setLoading(false)`.

---

## 5. Adicionar nova chamada à API

1. Definir contrato (método, URL, body, resposta) em acordo com **backend-api-demos**.
2. Em `App.jsx` (ou camada de API/hooks): `fetch(\`${API}/...\`, { ... })`, tratar resposta e erros.
3. Atualizar estado (ex.: `setConversationId`, `setMessages`) conforme necessário.

---

## 6. Referências

- **Contrato da API:** skill **backend-api-demos**, `.cursor/skills/backend-developer/references/api-demos.md`.
- **Estrutura do App:** skill **frontend-demos-structure**.

---

## 7. Respostas

Responder em **português** ao usuário.
