---
name: architecture-layers
description: Camadas e fronteiras do generative-ai — entrypoints, backend, frontend, ai, ingest, data, externos. Use ao decidir ONDE colocar um novo módulo, rota ou feature. Triggers: "camadas", "fronteiras", "onde colocar", "responsabilidade", "backend vs frontend", "ai vs ingest".
---

# Skill: Camadas e fronteiras

Definição das **camadas** do projeto e suas **responsabilidades**. Respeitar essas fronteiras ao adicionar código.

---

## 1. Entrypoints

- **Onde:** `app/main.py`, `scripts/` (update_assistant, setup_database, start_system).
- **Responsabilidade:** HTTP (Flask), registro de blueprints, servir frontend em `/demos`, scripts CLI. Não conter lógica de negócio pesada; delegar a backend/ ou ai/.

---

## 2. Backend (demos)

- **Onde:** `backend/routes.py`, `backend/services.py`.
- **Responsabilidade:** API REST em `/api/demos` (listar assistentes, criar conversa, enviar mensagem, upload PDF, deletar conversa). Serviços chamam `ai.assistant_manager`, `ai.assistant_run`, `ai.agents`. Conversas em memória por conversation_id.
- **Não:** Lógica de prompts/tools (fica em ai/); config hardcoded (fica em config/).

---

## 3. Frontend (demos)

- **Onde:** `frontend/` (React, Vite, `src/App.jsx`, `src/index.css`).
- **Responsabilidade:** UI de demos (seletor de assistente, upload PDF, chat, mensagens). Chamadas fetch para `/api/demos/*`. Build → `frontend/dist`; Flask serve em `/demos`.
- **Não:** Lógica de backend; definição de agentes (fica em ai/).

---

## 4. Agentes (`ai/`)

- **Onde:** `ai/agents.py`, `ai/prompts/`, `ai/tools/`, `ai/assistant_manager.py`, `ai/assistant_run.py`, `ai/clients.py`, `ai/pinecone_client.py`, `ai/sentiment_analyses/`, `ai/trading/`.
- **Responsabilidade:** Registry de agentes, instruções (prompts), definição e implementação de tools, dispatch com isolamento (allowed_tool_names), criação/obtenção de assistentes OpenAI, run_turn, Pinecone, trading, sentimento.
- **Fronteira:** Backend e app usam ai.*; ai não importa backend ou app.

---

## 5. Ingestão

- **Onde:** `ingest/pinecone_search.py`, `data_ingestion/pdf_processor.py`.
- **Responsabilidade:** Busca no Pinecone (search_contracts, search_faqs), criação de vector store a partir de PDF (OpenAI File Search). Usado por ai/tools (base) e backend (upload PDF).
- **Fronteira:** ai e backend podem usar ingest e data_ingestion; ingest pode usar ai.pinecone_client.

---

## 6. Dados

- **Onde:** `data_store/` (thread_store, conversation_schema).
- **Responsabilidade:** Armazenamento em memória (threads, conversas). Sem persistência em DB externo no projeto atual.

---

## 7. Serviços externos

- **Onde:** `external_services/` (ex.: binance_client).
- **Responsabilidade:** Clientes de APIs externas (Binance, etc.). Usados por ai/trading.

---

## 8. Diagrama (resumo)

```
app/main.py, scripts/
    ↓
backend/ (API /api/demos)  ←→  frontend/ (SPA /demos)
    ↓
config/ (settings, agents re-export, automations)
    ↓
ai/ (agents, prompts, tools, manager, run, pinecone, trading, sentiment)
    ↓
ingest/, data_ingestion/, data_store/, external_services/
```

---

## 9. Respostas

- Responder em **português** ao usuário.
