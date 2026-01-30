---
name: architecture-registries
description: Registries e config do think-tars — agents (ai/agents.py), automations (config/automations.py), settings. Use ao alterar registry de agentes, config ou automações. Triggers: "registry", "AGENTS_REGISTRY", "config agents", "config settings", "automations", "variáveis de ambiente".
---

# Skill: Registries e config

Onde ficam os **registries** (agentes, automações) e a **config** (settings, env) do projeto.

---

## 1. Registry de agentes (`ai/agents.py`)

- **AGENTS_REGISTRY:** Agentes do **Playground** (listados no site para o cliente testar). Cada entrada: `id`, `name`, `instructions_module`, `instructions_attr`, `tools_module`, `tools_attr`, `playground`: True.
- **INTERNAL_AGENTS_REGISTRY:** Agentes de **uso interno** (ex.: SDR no WhatsApp). Não listados no Playground. Mesma estrutura, `playground`: False.
- **DEFAULT_AGENT_ID:** Ex.: `"juridico"`.
- **Funções:** `get_agent_config(agent_id)` (busca em ambos os registries), `get_internal_agent_config(agent_id)` (só interno), `load_agent_instructions`, `load_agent_tools`, **`get_agent_tool_names(agent_id)`** (para isolamento no dispatch).

**Re-export:** `config/agents.py` re-exporta `ai.agents` para compatibilidade. A fonte da verdade é `ai/agents.py`.

**Adicionar agente Playground:** Incluir entrada em AGENTS_REGISTRY com `playground`: True; criar módulos em `ai/prompts/` e `ai/tools/`. Ver skill **assistant-engineer** ou **assistant-creator**.

**Adicionar agente interno (ex.: SDR):** Incluir em INTERNAL_AGENTS_REGISTRY; criar prompts e tools; integrar via webhook ou serviço interno. Ver skill **sdr-zapi**.

---

## 2. Config de aplicação (`config/settings.py`)

- Variáveis de ambiente (OPENAI_API_KEY, PINECONE_*, LLM_MODEL, etc.).
- **Nunca** hardcodar credenciais; usar `.env` e `config.settings`.

---

## 3. Registry de automações (`config/automations.py`)

- **AUTOMATIONS_REGISTRY:** Lista de automações (id, name, route, methods, handler_module, handler_attr, handler_kwargs).
- **Funções:** `get_automation`, `get_automation_handler`.
- Projeto atual: registry vazio; sem cron/automações agendadas.

---

## 4. Referência

- **Camadas e registries (resumo):** `.cursor/skills/architecture-guide/references/camadas-e-registries.md`.

---

## 5. Respostas

- Responder em **português** ao usuário.
