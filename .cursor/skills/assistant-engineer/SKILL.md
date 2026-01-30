---
name: assistant-engineer
description: Engenheiro de IA / Engenheiro de prompts para organizar, criar e ajustar assistentes no generative-ai. Estrutura ai/, isolamento por assistente (prompt + tools), registry, boas práticas de prompt e tools. Use ao criar/alterar assistentes, instruções, tools ou garantir que cada assistente use apenas seu escopo. Triggers: "engenheiro de IA", "engenheiro de prompt", "organizar assistentes", "ajustar assistente", "isolamento de tools", "prompt do agente", "tools do agente".
---

# Skill: Engenheiro de Assistentes de IA

Guia para **organizar, criar e ajustar** assistentes de IA no projeto como engenheiro de IA / engenheiro de prompts. Garante **isolamento por assistente**: cada assistente usa **apenas** seu próprio prompt e suas próprias tools.

---

## 1. Princípio de isolamento (obrigatório)

- **Um assistente = um prompt + um conjunto de tools.**
- O assistente selecionado pelo usuário no app deve considerar **somente**:
  - Suas **instruções** (system prompt) carregadas do módulo em `ai/prompts/`.
  - Suas **tools** (definidas no módulo em `ai/tools/` do agente).
- **Nunca** um assistente deve ter acesso a tools ou contexto de outro assistente.
- O **dispatch** de tool calls (`ai/tools/dispatch.py`) recebe `allowed_tool_names` por conversa e **só executa** tools desse conjunto; chamadas a outras tools retornam mensagem de "não disponível para este assistente".

---

## 2. Estrutura no repositório

```
ai/
├── agents.py              # Registry: AGENTS_REGISTRY, get_agent_config, load_agent_*, get_agent_tool_names
├── assistant_manager.py   # create_or_get_assistant_from_registry, update_assistant_*
├── assistant_run.py       # run_turn(..., allowed_tool_names=...) → dispatch com escopo
├── prompts/               # Instruções por agente (um módulo por agente)
│   ├── templates.py       # Jurídico (Tars)
│   ├── investment.py       # CryptoAnalyst
│   └── planilha.py        # Analista planilha
└── tools/                 # Tools por agente + dispatch
    ├── base.py             # AVAILABLE_FUNCTIONS (todas as implementações)
    ├── dispatch.py         # dispatch_tool_call(..., allowed_tool_names=...) → isolamento
    ├── juridico.py         # TOOLS_DEFINITION: search_contracts, search_faqs
    ├── investment.py       # TOOLS_DEFINITION: Binance/trading
    └── planilha.py         # TOOLS_DEFINITION: query_spreadsheet
```

- **Registry** (`ai/agents.py`): cada agente tem `id`, `name`, `instructions_module`, `instructions_attr`, `tools_module`, `tools_attr`.
- **Prompts**: um arquivo por agente em `ai/prompts/`; uma constante por arquivo (ex.: `DEFAULT_ASSISTANT_INSTRUCTIONS`, `INVESTMENT_ASSISTANT_INSTRUCTIONS`).
- **Tools**: um arquivo por agente em `ai/tools/` com `TOOLS_DEFINITION`; implementações reunidas em `ai/tools/base.py` (`AVAILABLE_FUNCTIONS`). O dispatch usa `get_agent_tool_names(agent_id)` para restringir quais tools podem ser executadas naquela conversa.

---

## 3. Fluxo de isolamento (demos)

1. Usuário seleciona assistente no app → `agent_id` (ex.: `juridico`, `investment`, `planilha`).
2. Backend cria conversa com `agent_id`; assistente OpenAI é criado/obtido com **instruções e tools desse agente**.
3. Ao enviar mensagem, `send_message` obtém `allowed_tool_names = get_agent_tool_names(agent_id)` e chama `run_turn(..., allowed_tool_names=allowed_tool_names)`.
4. Em `run_turn`, cada tool call é despachada com `dispatch_tool_call(name, args, allowed_tool_names=allowed_tool_names)`. Se `name` não estiver em `allowed_tool_names`, a tool **não é executada** e retorna mensagem de indisponibilidade.

---

## 4. Como adicionar um novo assistente

1. **Registry** (`ai/agents.py`): adicionar entrada em `AGENTS_REGISTRY` com `id`, `name`, `instructions_module`, `instructions_attr`, `tools_module`, `tools_attr` (ex.: `ai.prompts.meu_agente`, `ai.tools.meu_agente`).
2. **Prompt** (`ai/prompts/meu_agente.py`): criar módulo com uma constante de instruções (string Markdown). Incluir persona, objetivo, regras e **lista apenas das tools desse agente**.
3. **Tools** (`ai/tools/meu_agente.py`): criar módulo com `TOOLS_DEFINITION` (lista no formato OpenAI). Se houver implementação nova, adicionar em `ai/tools/base.py` em `AVAILABLE_FUNCTIONS` e, se a assinatura for especial, tratar em `ai/tools/dispatch.py`.
4. **Nada mais**: o app de demos lista assistentes pelo registry e já aplica isolamento via `get_agent_tool_names` e `allowed_tool_names`.

---

## 5. Boas práticas de prompt (instruções)

- **Persona:** nome, papel, tom (objetivo, empático, conservador, etc.).
- **Objetivo principal:** o que o assistente deve fazer e **quando usar cada tool** (só as tools dele).
- **Regras de resposta:** concisão, quando dizer "não encontrei", uso de emojis (se desejado).
- **Ferramentas:** listar **apenas** as tools desse assistente e quando usar cada uma.
- **Idioma:** português para conteúdo de produto/usuário.
- **Não** mencionar ou sugerir tools de outros assistentes nas instruções.

Ver `ai/prompts/templates.py`, `ai/prompts/investment.py`, `ai/prompts/planilha.py` como referência.

---

## 6. Boas práticas de tools

- **TOOLS_DEFINITION:** formato OpenAI (`type: "function"`, `function.name`, `function.description`, `function.parameters`). Descrições claras em português.
- **Implementação:** em `ai/tools/base.py` (ou módulo do agente se for específica); mapear em `AVAILABLE_FUNCTIONS`.
- **Dispatch:** se a assinatura da função for diferente dos padrões já tratados, adicionar branch em `ai/tools/dispatch.py` (mantendo o parâmetro `allowed_tool_names` em todas as chamadas).
- **Isolamento:** não depender de "o modelo não vai chamar" — o backend **sempre** restringe por `allowed_tool_names`; tools de outro agente retornam mensagem de indisponibilidade.

---

## 7. O que NUNCA fazer

- **Nunca** dar a um assistente instruções que mencionem ou incentivem o uso de tools de outro agente.
- **Nunca** usar um único assistente com todas as tools para "escolher" por prompt; manter um agente = um conjunto de tools no registry e no dispatch.
- **Nunca** remover o parâmetro `allowed_tool_names` do fluxo de demos (run_turn + dispatch_tool_call) para "simplificar"; isso quebra o isolamento.
- **Nunca** hardcodar credenciais ou config; usar `config.settings` e variáveis de ambiente.

---

## 8. Referências rápidas

| Onde | O quê |
|------|--------|
| `ai/agents.py` | Registry, `get_agent_tool_names(agent_id)` |
| `ai/prompts/` | Instruções por agente |
| `ai/tools/` | TOOLS_DEFINITION por agente, dispatch, AVAILABLE_FUNCTIONS |
| `backend/services.py` | `send_message` passa `allowed_tool_names` para `run_turn` |
| `docs/ARCHITECTURE.md` | Arquitetura geral |
| `AGENTS.md` | Mapa do repositório para IAs |

Ver também a skill **assistant-creator** para exemplos de instruções e tools (atualizar paths para `ai/` quando usar). Ver **architecture-guide** para camadas e registries.
