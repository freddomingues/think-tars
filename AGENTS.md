# Instruções para Agentes de IA

Repositório **think-tars**: site Think TARS (nova versão), Playground de assistentes de IA (OpenAI Assistant API), SDR no WhatsApp (Z-API), trading, ingestão (Pinecone, PDFs). Toda a lógica de agentes está na pasta **`ai/`**. Contato comercial: **+55 41 8749-7364**.

## Comando de Validação / Execução

```bash
# Subir aplicação (Flask + API de demos)
python app/main.py

# Atualizar assistente com instruções e tools do agente padrão (juridico)
python scripts/update_assistant.py

# Setup (informação; projeto não usa DB externo)
python scripts/setup_database.py

# Iniciar sistema (wrapper que sobe o app)
python scripts/start_system.py
```

Não há suite de testes automatizada; validar manualmente via app e demos.

---

## Estrutura do Repositório

```
ai/                                    # Agentes de IA (registry, prompts, tools, core)
├── agents.py                          # AGENTS_REGISTRY (Playground), INTERNAL_AGENTS_REGISTRY (SDR)
├── assistant_manager.py               # create_or_get_assistant_from_registry, update_assistant_*
├── assistant_run.py                   # run_turn (um turno de conversa)
├── clients.py                         # get_chroma_client_*, get_embedding_model (compat)
├── pinecone_client.py                 # Cliente Pinecone e embeddings
├── prompts/                           # Instruções por agente (system prompts)
│   ├── templates.py                   # Jurídico (Tars): DEFAULT_ASSISTANT_INSTRUCTIONS
│   ├── investment.py                  # CryptoAnalyst: INVESTMENT_ASSISTANT_INSTRUCTIONS
│   ├── planilha.py                    # Analista planilha: PLANILHA_ASSISTANT_INSTRUCTIONS
│   └── sdr.py                         # SDR (uso interno WhatsApp): SDR_ASSISTANT_INSTRUCTIONS
└── tools/                             # Ferramentas por agente + dispatch
    ├── base.py                        # AVAILABLE_FUNCTIONS (nome → função)
    ├── dispatch.py                    # dispatch_tool_call(name, args)
    ├── juridico.py                    # TOOLS_DEFINITION: search_contracts, search_faqs
    ├── investment.py                  # TOOLS_DEFINITION: Binance/trading
    ├── planilha.py                    # TOOLS_DEFINITION + query_spreadsheet_data (stub)
    └── sdr.py                         # TOOLS_DEFINITION: schedule_meeting (uso interno)
├── sentiment_analyses/                # Análise de sentimento (VADER, TextBlob)
│   ├── sentiment.py                   # analisar_sentimento
│   └── advanced_sentiment.py          # AdvancedSentimentAnalyzer
└── trading/                           # Trading (execução manual; sem cron)
    ├── strategy.py                    # ConservativeStrategy, TradingSignal
    ├── investment_agent.py            # InvestmentAgent (Binance)
    ├── trading_tools.py               # analyze_bitcoin_market, get_bitcoin_price, buy/sell_bitcoin
    ├── trading_tools_definition.py   # TRADING_TOOLS_DEFINITION
    ├── email_notifier.py              # Notificações por email
    ├── diagnostico_email.py            # Script diagnóstico email
    └── verificar_credenciais.py        # Script verificação Binance

app/                                   # Entrypoint HTTP
├── main.py                            # Flask, register_demo_routes, frontend /demos

backend/                               # API Playground + webhook Z-API
├── routes.py                          # Blueprint /api/demos (assistants, conversations, messages)
├── services.py                        # list_assistants (só Playground), create_conversation, send_message
├── sdr_services.py                    # run_sdr_turn, get_or_create_sdr_thread (SDR WhatsApp)
└── zapi_webhook.py                    # POST /api/zapi/webhook (Z-API → SDR)

frontend/                              # SPA site + Playground (React + Vite)
├── src/App.jsx                        # Site Think TARS, Playground (assistentes, chat, upload PDF)
└── vite.config.js                     # Proxy /api → Flask

config/
├── settings.py                        # OPENAI_API_KEY, PINECONE_*, ZAPI_INSTANCE_ID, ZAPI_TOKEN_INSTANCE, etc.
├── logging_config.py                  # setup_logging, log_tool_call, log_error
├── agents.py                          # Re-export de ai.agents (compatibilidade)
└── automations.py                     # Registry de automações (vazio; sem cron)

scripts/                                # Scripts executáveis (raiz do projeto no PYTHONPATH)
├── update_assistant.py                # Atualiza assistente com instruções/tools do agente padrão
├── setup_database.py                  # Mensagem de setup (sem DB externo)
└── start_system.py                    # Inicia o app Flask

ingest/                                # Busca e ingestão
├── pinecone_search.py                 # search_contracts, search_faqs (Pinecone)

data_ingestion/                        # PDFs
└── pdf_processor.py                   # create_vector_store_from_pdf (OpenAI File Search)

data_store/                            # Armazenamento em memória
├── thread_store.py                    # thread_id por telefone
└── conversation_schema.py             # Stub conversas

external_services/
├── binance_client.py                  # Cliente Binance
└── zapi_client.py                     # Z-API: send_text, parse_webhook_message (WhatsApp)

docs/                                  # Documentação
├── ARCHITECTURE.md                    # Arquitetura detalhada, camadas, onde mudar o quê
└── COMO_USAR_DEMOS.md                 # Guia de uso da interface de demos

.cursor/skills/                        # Skills Cursor (referência para IA)
├── architecture-guide/                # Índice arquitetura → overview, registries, layers, demos-flow
├── architecture-overview/             # Onde mudar o quê, mapa de camadas
├── architecture-registries/           # Registry agentes, config, automations
├── architecture-layers/               # Camadas e fronteiras (entrypoints, backend, ai, ingest)
├── architecture-demos-flow/            # Fluxo run_turn, send_message, tool dispatch
├── assistant-creator/                 # Criar novo assistente, prompts, tools (ai/)
├── assistant-engineer/                # Isolamento, escopo, boas práticas prompts/tools
├── ai-agents-maintenance/             # Manutenção completa de agentes (criar/editar, prompts, tools, debug)
├── backend-developer/                 # Visão geral backend → skills granulares
├── backend-api-demos/                 # Endpoints API de demos
├── backend-services-demos/            # Serviços (create_conversation, send_message, upload PDF)
├── backend-flask-app/                 # App Flask, registro blueprints, servir /demos
├── backend-new-route/                 # Como adicionar nova rota ou blueprint
├── backend-maintenance/               # Manutenção do backend (rotas, serviços, error handling, logging)
├── frontend-developer/                # Visão geral frontend → skills granulares
├── frontend-demos-structure/          # Estrutura pastas, App.jsx, index.css
├── frontend-api-demos/                # Chamadas fetch à API de demos
├── frontend-ui-chat/                  # UI do chat (sidebar, mensagens, upload PDF)
├── frontend-build-serve/              # Build (npm run build) e servir (Flask /demos)
├── frontend-maintenance/              # Manutenção do frontend (React, CSS, responsividade, debug)
├── render-deploy/                     # Deploy e manutenção no Render (build, Procfile, troubleshooting)
├── general-maintenance/               # Manutenção geral (estrutura, debugging, testes, troubleshooting)
├── pull-request-creator/              # Template de PR
├── sdr-zapi/                          # SDR WhatsApp (Z-API, webhook, agente interno)
└── testing-local-backend/             # Testes locais do backend (webhook SDR, Playground, curl)
```

---

## Regras Globais Obrigatórias

### Onde está cada coisa

| Objetivo | Onde |
|----------|------|
| **Registry de agentes** | `ai/agents.py` (AGENTS_REGISTRY, DEFAULT_AGENT_ID, load_agent_instructions, load_agent_tools). `config/agents.py` só re-exporta. |
| **Instruções (prompts) do agente** | `ai/prompts/` — um módulo por agente: `templates.py`, `investment.py`, `planilha.py`. |
| **Definição de tools (OpenAI)** | `ai/tools/` — por agente: `juridico.py`, `investment.py`, `planilha.py` (TOOLS_DEFINITION). |
| **Implementações de tools** | `ai/tools/base.py` (AVAILABLE_FUNCTIONS). Implementações reais em `ingest/pinecone_search.py`, `ai/trading/trading_tools.py`, `ai/tools/planilha.py`. |
| **Dispatch de tool calls** | `ai/tools/dispatch.py` — `dispatch_tool_call(name, args)`. Adicionar branch só se a assinatura da tool for especial. |
| **Criar/obter assistente** | `ai/assistant_manager.py` — `create_or_get_assistant_from_registry(agent_id)`. |
| **Executar um turno** | `ai/assistant_run.py` — `run_turn(client, thread_id, assistant_id, user_message)`. |
| **Config e env** | `config/settings.py` e `.env`. Nada hardcoded. |
| **Rotas e serviços de demos** | `backend/routes.py`, `backend/services.py`; registrar em `app/main.py` com `register_demo_routes(app)`. |

### Skills recomendadas (Cursor)

#### Manutenção de Agentes de IA
- **Organizar/criar/ajustar assistentes (engenheiro de IA/prompt):** `assistant-engineer` — isolamento, prompts, tools, registry.
- **Criar novo assistente ou tool:** `assistant-creator`
- **Manutenção de agentes:** `ai-agents-maintenance` — criar/editar agentes, ajustar prompts, adicionar tools, debugging, isolamento, code_interpreter.

#### Arquitetura e Estrutura
- **Arquitetura / onde mudar o quê:** `architecture-guide` (índice) → `architecture-overview`, `architecture-registries`, `architecture-layers`, `architecture-demos-flow`.
- **Manutenção geral:** `general-maintenance` — estrutura geral, debugging, testes, troubleshooting.

#### Backend
- **Backend / API de demos:** `backend-developer` (índice) → `backend-api-demos`, `backend-services-demos`, `backend-flask-app`, `backend-new-route`.
- **Manutenção do backend:** `backend-maintenance` — rotas, serviços, blueprints, error handling, logging, servir frontend.

#### Frontend
- **Frontend demos:** `frontend-developer` (índice) → `frontend-demos-structure`, `frontend-api-demos`, `frontend-ui-chat`, `frontend-build-serve`.
- **Manutenção do frontend:** `frontend-maintenance` — componentes React, estado, API calls, CSS, responsividade, debugging.

#### Deploy e Infraestrutura
- **Deploy no Render:** `render-deploy` — build commands, Procfile, variáveis de ambiente, troubleshooting, logs, domínio customizado.

#### Outros
- **Criar PR:** `pull-request-creator`
- **SDR WhatsApp (Z-API, webhook, agente interno):** `sdr-zapi`
- **Testes locais do backend (após novas implementações):** `testing-local-backend`

### Restrições de arquitetura

1. **Isolamento por assistente (obrigatório):** Cada assistente usa **apenas** seu prompt e suas tools. O dispatch recebe `allowed_tool_names` (via `get_agent_tool_names(agent_id)`) e **só executa** tools desse conjunto; chamadas a tools de outro agente retornam "não disponível para este assistente". Ver `ai/agents.get_agent_tool_names`, `ai/assistant_run.run_turn(..., allowed_tool_names=...)`, `ai/tools/dispatch.dispatch_tool_call(..., allowed_tool_names=...)`, `backend/services.send_message`.
2. **Novo agente:** SEMPRE adicionar entrada em `AGENTS_REGISTRY` em `ai/agents.py` com `instructions_module` e `tools_module` apontando para módulos em `ai.prompts.*` e `ai.tools.*`.
3. **Nova tool:** SEMPRE definir em um módulo em `ai/tools/` (TOOLS_DEFINITION) e registrar a implementação em `ai/tools/base.py` (AVAILABLE_FUNCTIONS). Se a assinatura for diferente das já tratadas, adicionar branch em `ai/tools/dispatch.py`.
4. **Prompts:** SEMPRE em `ai/prompts/`; cada agente tem seu próprio módulo e constante; **nunca** mencionar tools de outro assistente nas instruções.
5. **Credenciais:** NUNCA hardcodar; usar `config/settings.py` e variáveis de ambiente.
6. **Projeto não usa:** AWS (S3, DynamoDB), Zatten, cron. Dados em memória (`data_store/`); busca via Pinecone e OpenAI File Search (PDFs).

### Restrições de workflow

1. NUNCA criar commits automaticamente — aguardar comando do usuário.
2. Responder em **português** ao usuário quando for o caso.
3. Ao duplicar comportamento, verificar se já existe em `ai/`, `backend/` ou `ingest/`.

---

## Documentação Detalhada

### Arquitetura e uso

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Princípios, camadas, registry, manager, prompts e tools, backend/frontend demos, onde mudar o quê.
- **[docs/COMO_USAR_DEMOS.md](docs/COMO_USAR_DEMOS.md)** — Como usar a interface de demos (assistentes, upload de PDF, conversa).

### Referência rápida (camadas e isolamento)

- **[.cursor/skills/architecture-guide/references/camadas-e-registries.md](.cursor/skills/architecture-guide/references/camadas-e-registries.md)** — Camadas, registry de agentes (`ai/agents.py`), tool dispatch (`ai/tools/dispatch.py`).
- **[.cursor/skills/assistant-engineer/references/isolamento-e-escopo.md](.cursor/skills/assistant-engineer/references/isolamento-e-escopo.md)** — Isolamento por assistente (allowed_tool_names, get_agent_tool_names).

### Skills (conteúdo em .cursor/skills/)

#### Manutenção de Agentes de IA
- **assistant-engineer** — Isolamento, escopo, boas práticas de prompts e tools (ai/).
- **assistant-creator** — Criar novo assistente: registry em `ai/agents.py`, instruções em `ai/prompts/`, tools em `ai/tools/`.
- **ai-agents-maintenance** — Manutenção completa de agentes: criar/editar agentes, ajustar prompts, adicionar tools, debugging, isolamento, code_interpreter.

#### Arquitetura e Estrutura
- **architecture-guide** — Índice: overview, registries, layers, demos-flow.
- **architecture-overview** — Onde mudar o quê, mapa de camadas.
- **architecture-registries** — Registry de agentes, config, automations.
- **architecture-layers** — Camadas e fronteiras (entrypoints, backend, frontend, ai, ingest).
- **architecture-demos-flow** — Fluxo run_turn, send_message, tool dispatch, allowed_tool_names.
- **general-maintenance** — Manutenção geral: estrutura, debugging, testes, troubleshooting.

#### Backend
- **backend-developer** — Visão geral backend; use **backend-api-demos**, **backend-services-demos**, **backend-flask-app**, **backend-new-route** para cenários específicos.
- **backend-maintenance** — Manutenção do backend: rotas, serviços, blueprints, error handling, logging, servir frontend.

#### Frontend
- **frontend-developer** — Visão geral frontend; use **frontend-demos-structure**, **frontend-api-demos**, **frontend-ui-chat**, **frontend-build-serve** para cenários específicos.
- **frontend-maintenance** — Manutenção do frontend: componentes React, estado, API calls, CSS, responsividade, debugging.

#### Deploy e Infraestrutura
- **render-deploy** — Deploy e manutenção no Render: build commands, Procfile, variáveis de ambiente, troubleshooting, logs, domínio customizado.

#### Outros
- **pull-request-creator** — Template e fluxo de PR.
- **sdr-zapi** — SDR no WhatsApp via Z-API: webhook, envio de mensagem, agente interno (schedule_meeting).
- **testing-local-backend** — Testes locais: subir Flask, testar /api/zapi/test-webhook, Playground, checklist pós-implementação.

---

## Agentes existentes (registry)

### Playground (listados no site para o cliente testar)

| id | Nome | Instruções | Tools |
|----|------|------------|-------|
| `juridico` | Assistente Jurídico de Contratos | `ai.prompts.templates` | `ai.tools.juridico` (search_contracts, search_faqs) |
| `investment` | CryptoAnalyst - Análise de Investimento | `ai.prompts.investment` | `ai.tools.investment` (analyze_bitcoin_market) |
| `planilha` | Analista de Dados - Planilha Excel | `ai.prompts.planilha` | `ai.tools.planilha` (query_spreadsheet) + code_interpreter |
| `marketing` | MarketingPro - Marketing Digital | `ai.prompts.marketing` | `ai.tools.marketing` (analyze_marketing_metrics) |
| `rh` | HRExpert - Recursos Humanos | `ai.prompts.rh` | `ai.tools.rh` (analyze_hr_metrics) |
| `suporte` | TechSupport - Suporte Técnico | `ai.prompts.suporte` | `ai.tools.suporte` (search_knowledge_base) |
| `vendas` | SalesPro - Vendas | `ai.prompts.vendas` | `ai.tools.vendas` (analyze_sales_funnel) |
| `redacao` | ContentWriter - Redação e Conteúdo | `ai.prompts.redacao` | `ai.tools.redacao` (analyze_content) |

**Nota:** Todos os agentes do Playground têm `code_interpreter` habilitado para análise de arquivos (PDF, Excel, CSV).

### Uso interno (não aparecem no Playground)

| id | Nome | Uso | Tools |
|----|------|-----|-------|
| `sdr` | SDR - Atendimento e Qualificação | WhatsApp via Z-API (leads do site) | `ai.tools.sdr` (schedule_meeting) |

---

## Regras Gerais

- EVITAR overengineering — preferir simplicidade.
- Antes de criar novo módulo ou rota, verificar se já existe em `ai/`, `backend/`, `ingest/`.
- Ao alterar agente ou tools, consultar `ai/agents.py` e `docs/ARCHITECTURE.md` para manter consistência.
- Para localizar instruções ou tools rapidamente: **registry** → `ai/agents.py`; **prompts** → `ai/prompts/`; **tools (definição + dispatch)** → `ai/tools/`.
