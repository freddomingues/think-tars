---
name: assistant-creator
description: Desenvolver novos assistentes de IA (OpenAI Assistant API) no projeto think-tars, seguindo os padrões em ai/. Use ao criar assistente, adicionar tools, alterar instruções. Triggers: "criar assistente", "novo assistente", "adicionar tool", "instruções do assistente", "Assistant API".
---

# Skill: Criar novos assistentes de IA

Guia para desenvolver novos assistentes no repositório, com base nos exemplos em `ai/` e na integração em `app/main.py`. Para **isolamento e escopo** (allowed_tool_names, prompts, tools por agente), use a skill **assistant-engineer**.

---

## 1. Processo (resumo)

1. **Registry** — Adicionar entrada em `ai/agents.py` (AGENTS_REGISTRY) com `id`, `name`, `instructions_module`, `instructions_attr`, `tools_module`, `tools_attr` (módulos em `ai.prompts.*`, `ai.tools.*`).
2. **Instruções** — Criar ou editar módulo em `ai/prompts/` (ex.: `templates.py`, `investment.py`, `planilha.py`).
3. **Tools** — Definir TOOLS_DEFINITION em módulo em `ai/tools/` (ex.: `juridico.py`, `investment.py`, `planilha.py`); implementações em `ai/tools/base.py` (AVAILABLE_FUNCTIONS); assinaturas especiais em `ai/tools/dispatch.py` se necessário.
4. **Assistente** — Usar `create_or_get_assistant_from_registry(agent_id)` via `ai/assistant_manager.py`. O app e o backend já usam o registry; cada conversa usa o assistente do agente selecionado com isolamento de tools.

---

## 2. Estrutura no repositório

```
ai/
├── agents.py              # AGENTS_REGISTRY, get_agent_config, load_agent_*, get_agent_tool_names
├── assistant_manager.py   # create_or_get_assistant_from_registry, update_assistant_*, list_all_assistants
├── assistant_run.py       # run_turn (allowed_tool_names)
├── clients.py              # helpers OpenAI / embedding
├── pinecone_client.py      # busca vetorial (opcional)
├── prompts/                # Instruções por agente (system prompts)
│   ├── templates.py       # Jurídico (Tars): DEFAULT_ASSISTANT_INSTRUCTIONS
│   ├── investment.py      # CryptoAnalyst: INVESTMENT_ASSISTANT_INSTRUCTIONS
│   └── planilha.py         # Analista planilha: PLANILHA_ASSISTANT_INSTRUCTIONS
└── tools/                  # Ferramentas por agente + dispatch
    ├── base.py             # AVAILABLE_FUNCTIONS (nome → função)
    ├── dispatch.py         # dispatch_tool_call(name, args, allowed_tool_names)
    ├── juridico.py         # TOOLS_DEFINITION: search_contracts, search_faqs
    ├── investment.py       # TOOLS_DEFINITION: Binance/trading
    └── planilha.py         # TOOLS_DEFINITION + query_spreadsheet_data

app/main.py                 # Flask, register_demo_routes, ASSISTANT_ID (inicialização)
config/settings              # OPENAI_API_KEY, LLM_MODEL
config/agents.py            # Re-export de ai.agents (compatibilidade)
```

- **Instruções:** string em Markdown (Persona, Objetivo, Regras, Ferramentas).
- **Tools:** lista OpenAI `{"type": "function", "function": { "name", "description", "parameters" }}`; implementações em AVAILABLE_FUNCTIONS.
- **Config:** sempre `config.settings`; nada hardcoded.

---

## 3. Exemplos de assistentes existentes

### 3.1 Assistente Jurídico (Tars)

- **id:** `juridico`. **Nome:** "Assistente Jurídico de Contratos".
- **Instruções:** `ai/prompts/templates.py` (DEFAULT_ASSISTANT_INSTRUCTIONS).
- **Tools:** `ai/tools/juridico.py` (search_contracts, search_faqs).
- **Uso:** assistente padrão (DEFAULT_AGENT_ID); usado na inicialização em `app/main.py`.

### 3.2 Assistente de Investimento (CryptoAnalyst)

- **id:** `investment`. **Nome:** CryptoAnalyst - Análise de Investimento.
- **Instruções:** `ai/prompts/investment.py`.
- **Tools:** `ai/tools/investment.py` (Binance/trading: analyze_bitcoin_market, get_bitcoin_price, buy_bitcoin, sell_bitcoin, etc.).

### 3.3 Analista de Planilha

- **id:** `planilha`. **Nome:** Analista de Dados - Planilha Excel.
- **Instruções:** `ai/prompts/planilha.py`.
- **Tools:** `ai/tools/planilha.py` (query_spreadsheet).

---

## 4. Definir instruções (prompts)

- **Persona:** nome, papel, tom (ex.: direto, empático, conservador).
- **Objetivo principal:** o que o assistente deve fazer e quando usar cada tool.
- **Regras de resposta:** concisão, quando dizer "não encontrei", uso de emojis, etc.
- **Ferramentas:** lista das tools e quando usar cada uma.
- **Fluxo (opcional):** passos sugeridos (ex.: "ao pedir análise, use X depois Y").

Manter em português quando for conteúdo de produto/usuário. Ver skill **assistant-engineer** para isolamento e escopo.

---

## 5. Definir e implementar tools

1. **TOOLS_DEFINITION:** em módulo em `ai/tools/` (ex.: `juridico.py`), formato OpenAI (name, description, parameters JSON Schema). Descrições em português quando expostas ao usuário.
2. **AVAILABLE_FUNCTIONS:** em `ai/tools/base.py`, dicionário `nome → função`. Implementações podem estar em `ingest/`, `ai/trading/`, ou no próprio `ai/tools/`.
3. **Dispatch:** `ai/tools/dispatch.py` — `dispatch_tool_call(name, args, allowed_tool_names=...)`. O dispatch já aplica assinaturas específicas (search_*, query_spreadsheet, buy/sell_bitcoin, etc.). Se uma tool tiver parâmetros especiais, adicionar branch no dispatch e manter AVAILABLE_FUNCTIONS atualizado.
4. **Isolamento:** cada agente tem sua lista de tools em `ai/agents.py`; `get_agent_tool_names(agent_id)` é usado no run_turn; o dispatch bloqueia tools não permitidas. Ver **assistant-engineer**.

---

## 6. Manager e atualização

- **Criar/obter:** `create_or_get_assistant_from_registry(agent_id)` — usa o registry para instruções e tools.
- **Atualizar:** `update_assistant_instructions(assistant_id, new_instructions, new_tools)` — troca instruções e/ou tools.
- **Listar:** `list_all_assistants()`.
- **Deletar:** `delete_assistant(assistant_id)`.
- **Tools do assistente:** `get_assistant_tools(assistant_id)`.

Para um **novo** assistente: adicionar entrada em AGENTS_REGISTRY; criar módulos em `ai/prompts/` e `ai/tools/`. O script `scripts/update_assistant.py` atualiza o assistente do agente padrão com instruções e tools do registry.

---

## 7. Integração com o app

- Na inicialização, `app/main.py` chama `create_or_get_assistant_from_registry(DEFAULT_AGENT_ID)` e guarda em ASSISTANT_ID.
- A API de demos (`backend/services.py`) cria conversas por `agent_id` e envia mensagens com `run_turn(..., allowed_tool_names=get_agent_tool_names(agent_id))`.
- Para mais de um assistente, o frontend já permite selecionar o agente; cada conversa usa o assistente e as tools daquele agente (isolamento).

---

## 8. Convenções

- Config em `config.settings`; uso de `config.logging_config` e logs estruturados onde fizer sentido.
- Tratar ausência de Pinecone (ou de outras deps opcionais) com imports try/except e fallbacks.
- Manter descrições de tools e instruções em português quando forem voltadas ao usuário.
- Responder em **português** ao usuário.

---

## 9. Referências rápidas

- **Registry e isolamento:** `ai/agents.py`, skill **assistant-engineer**.
- **Instruções:** `ai/prompts/templates.py`, `ai/prompts/investment.py`, `ai/prompts/planilha.py`.
- **Tools e dispatch:** `ai/tools/base.py`, `ai/tools/dispatch.py`, módulos em `ai/tools/*.py`.
- **Manager:** `ai/assistant_manager.py`.
- **Atualizar assistente:** `scripts/update_assistant.py`.

Para trechos expandidos de instruções e tools, ver `references/` nesta skill.
