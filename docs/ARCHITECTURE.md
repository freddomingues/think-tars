# Arquitetura do Projeto generative-ai

Este documento descreve a arquitetura do repositório para **escalar agentes de IA e automações** mantendo padrões claros e acoplamento baixo.

---

## 1. Princípios

- **Config centralizada:** `config/settings.py` (env), `config/automations.py` (automações). Registry de agentes em `ai/agents.py`.
- **Agentes:** Conversacionais (Assistant API + tools). Nenhuma automação agendada (cron) no projeto por enquanto.
- **Registros (registry):** Novos agentes em `ai/agents.py`; automações em config; o app consome esses registros em vez de hardcodar.
- **Dispatch centralizado:** Tool calls do Assistant API passam por `ai/tools/dispatch.py`; novas tools em `ai/tools/` e, se preciso, com branch no dispatch.
- **Sem config hardcoded:** Credenciais e parâmetros vêm de variáveis de ambiente ou do config.

---

## 2. Camadas e responsabilidades

| Camada | Diretório | Responsabilidade |
|--------|-----------|------------------|
| **Entrypoints** | `app/main.py`, `scripts/` | HTTP, API de demos, CLI (update_assistant, setup_database, start_system). |
| **Backend (demos)** | `backend/` | API de demos: listar assistentes, criar conversa, enviar mensagem. Blueprint em `/api/demos`. |
| **Frontend (demos)** | `frontend/` | SPA (React + Vite) para demos dos assistentes. Build em `frontend/dist`; servido em `/demos`. |
| **Config** | `config/` | Settings, registry de automações. |
| **Agentes** | `ai/` | Assistentes OpenAI: registry (`agents.py`), prompts (`prompts/`), tools (`tools/`), manager, run, clients, Pinecone; trading (`trading/`); sentimento (`sentiment_analyses/`). |
| **Ingestão** | `ingest/`, `data_ingestion/` | Busca no Pinecone; PDFs enviados pelos clientes na aplicação. |
| **Dados** | `data_store/` | Armazenamento em memória (threads, conversas). |
| **Serviços externos** | `external_services/` | Binance, etc. |

---

## 3. Agentes (OpenAI Assistant API)

### 3.1 Registry: `ai/agents.py`

- **`AGENTS_REGISTRY`:** Lista de agentes. Cada um define `id`, `name`, módulo de instruções e de tools (`ai.prompts.*`, `ai.tools.*`).
- **`DEFAULT_AGENT_ID`:** Agente usado na inicialização (ex.: `juridico`).
- **`get_agent_config`**, **`load_agent_instructions`**, **`load_agent_tools`:** Resolvem config e carregam instruções/tools dinamicamente.

### 3.2 Manager: `ai/assistant_manager.py`

- **`create_or_get_assistant`:** Cria/obtém por nome, com instruções e tools padrão (retrocompat).
- **`create_or_get_assistant_from_registry(agent_id)`:** Cria/obtém usando o registry.
- **`update_assistant_instructions`**, **`list_all_assistants`**, **`delete_assistant`**, **`get_assistant_tools`:** CRUD e inspeção.

### 3.3 Isolamento por assistente

- Cada assistente usa **apenas** suas instruções (`ai/prompts/*`) e suas tools (`ai/tools/*` do agente).
- Em cada conversa, o backend obtém `allowed_tool_names = get_agent_tool_names(agent_id)` e passa para `run_turn(..., allowed_tool_names=...)`. O dispatch **só executa** tools desse conjunto; chamadas a tools de outro agente retornam mensagem de indisponibilidade.

### 3.4 Prompts e tools

- **`ai/prompts/`:** Instruções por agente (`templates.py` jurídico, `investment.py`, `planilha.py`).
- **`ai/tools/`:** Por agente: `juridico.py`, `investment.py`, `planilha.py` (TOOLS_DEFINITION). `base.py`: `AVAILABLE_FUNCTIONS` (implementações). `dispatch.py`: `dispatch_tool_call(name, args, allowed_tool_names=...)` — executa apenas tools permitidas para o assistente.
- Novas tools: implementar em `ai/tools/`; branch em `ai/tools/dispatch.py` se a assinatura for especial.

### 3.5 Como adicionar um novo agente

1. Incluir entrada em `AGENTS_REGISTRY` (`ai/agents.py`) com `id`, `name`, `instructions_module`, `instructions_attr`, `tools_module`, `tools_attr` (ex.: `ai.prompts.*`, `ai.tools.*`).
2. Criar ou reutilizar módulo em `ai/prompts/` e em `ai/tools/`.
3. Usar `create_or_get_assistant_from_registry(agent_id)` na inicialização ou em roteamento. Ver também a skill **assistant-creator**.

---

## 4. Trading

- **`ai/trading/`:** Lógica de trading (estratégia, investment_agent, trading_tools). Por enquanto não há execução automatizada via cron; o projeto não registra endpoints de cron.
- **`ai/sentiment_analyses/`:** Análise de sentimento (VADER, TextBlob, avançada).

---

## 5. Backend e frontend (demos)

### 5.1 Backend (`backend/`)

- **`backend/routes.py`:** Blueprint `demos` em `/api/demos`. Rotas: `GET /assistants`, `POST /upload-pdf`, `POST /conversations`, `POST /conversations/<id>/messages`, `DELETE /conversations/<id>`.
- **`backend/services.py`:** `list_assistants()`, `create_conversation(agent_id, vector_store_id)`, `send_message(conversation_id, content)`, `upload_pdf_and_create_vector_store(...)`, `cleanup_conversation(conversation_id)`. Usa `ai.agents` (incl. `get_agent_tool_names`), `ai.assistant_run.run_turn(..., allowed_tool_names=...)`, armazenamento in-memory de conversas.
- **`register_demo_routes(app)`:** Registra o blueprint e CORS para `/api/demos`.

### 5.2 Frontend (`frontend/`)

- **Stack:** React 18, Vite. Build: `npm run build` → `frontend/dist`.
- **Base URL:** `/demos/`. Em dev, Vite proxy `/api` para o Flask.
- **App:** Seletor de assistente, criar/iniciar conversa, chat (mensagens + input), enviar mensagem.
- **Servido por Flask:** `app/main.py` serve `frontend/dist` em `/demos` e `/demos/<path>` quando `frontend/dist` existe.

### 5.3 Run do assistant (demos)

- **`ai/assistant_run.py`:** `run_turn(client, thread_id, assistant_id, user_message, allowed_tool_names=...)` — sync; adiciona mensagem, cria run, trata `requires_action` com `dispatch_tool_call(..., allowed_tool_names=...)`, retorna texto da resposta. Reutilizável pela API de demos (sync). Isolamento: apenas tools em `allowed_tool_names` são executadas.

---

## 6. App, Playground e webhook Z-API

- **`app/main.py`:** Cria o Flask app, inicializa o agente via registry, rotas de tools, **API de demos (Playground)** e **frontend em /demos**. Registra webhook Z-API em `/api/zapi/webhook`.
- **Tools HTTP:** `/api/tools/search_contracts`, `search_faqs` — buscam no Pinecone; o Assistant usa as funções em `ai/tools/` via dispatch.
- **SDR (uso interno):** Agente SDR em `INTERNAL_AGENTS_REGISTRY`; atendimento WhatsApp via Z-API. Webhook recebe mensagens, `backend/sdr_services.run_sdr_turn` processa com o SDR, resposta enviada via `external_services/zapi_client.send_text`. Ver skill **sdr-zapi**.

---

## 7. Fluxo de dados (resumido)

1. **Base de conhecimento:** Arquivos enviados pelos clientes na aplicação (upload de PDF) + Pinecone.
2. **Playground (site):** Frontend `/demos` → `GET /api/demos/assistants` (só agentes com playground=True), `POST /api/demos/conversations`, `POST /api/demos/conversations/<id>/messages` → `run_turn` → resposta no chat.
3. **SDR WhatsApp:** Z-API envia `POST /api/zapi/webhook` → `run_sdr_turn(phone, text)` → resposta enviada via Z-API.
4. **Contato comercial:** +55 41 8749-7364 (não há link para site antigo).

---

## 8. Onde mudar o quê

| Objetivo | Onde |
|----------|------|
| Novo agente | `ai/agents.py` + módulos em `ai/prompts/` e `ai/tools/`; `assistant_manager` já suporta registry. |
| Nova tool do assistente | `ai/tools/` (módulo do agente + `base.py`) + `ai/tools/dispatch.py` (se assinatura especial). |
| Lógica de trading | `ai/trading/` (execução manual; sem cron no projeto). |
| Nova rota ou serviço de demos | `backend/routes.py`, `backend/services.py`; registrar em `app/main.py` via `register_demo_routes`. |
| Mudar UI do site / Playground | `frontend/` (React, Vite); build com `npm run build` em `frontend`. |
| SDR / Z-API (WhatsApp) | `ai/prompts/sdr.py`, `ai/tools/sdr.py`, `backend/sdr_services.py`, `backend/zapi_webhook.py`, `external_services/zapi_client.py`. Skill **sdr-zapi**. |
| Nova config / env | `config/settings.py` e `.env` (incl. ZAPI_INSTANCE_ID, ZAPI_TOKEN_INSTANCE para Z-API). |
| Novos skills (Cursor) | `.cursor/skills/<nome>/` e `SKILL.md` na raiz; ver meta-skill e **architecture-guide**. |

---

## 9. Referências

- **Skills (Cursor):** `.cursor/skills/` — **architecture-guide** (índice) → architecture-overview, architecture-registries, architecture-layers, architecture-demos-flow; **backend-developer** → backend-api-demos, backend-services-demos, backend-flask-app, backend-new-route; **frontend-developer** → frontend-demos-structure, frontend-api-demos, frontend-ui-chat, frontend-build-serve; **assistant-engineer**, **assistant-creator**, **pull-request-creator**; **sdr-zapi** (SDR WhatsApp via Z-API). Ver `AGENTS.md` para lista completa.
- **README:** Visão geral, subprojetos, deploy, configuração.
