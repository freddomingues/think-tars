# Isolamento e escopo por assistente

## Regra

Cada assistente usa **apenas**:
- Suas **instruções** (módulo em `ai.prompts.*`).
- Suas **tools** (módulo em `ai.tools.*` → nomes em `get_agent_tool_names(agent_id)`).

O backend e o dispatch garantem que, em uma conversa, **só as tools do agente da conversa** sejam executadas.

## Código envolvido

1. **`ai/agents.py`**
   - `get_agent_tool_names(agent_id)` → `set[str]` com os nomes das tools do agente (extraídos de TOOLS_DEFINITION).

2. **`backend/services.py`**
   - `send_message(conversation_id, content)`:
     - Lê `agent_id` da conversa.
     - `allowed_tool_names = get_agent_tool_names(agent_id)`.
     - Chama `run_turn(..., allowed_tool_names=allowed_tool_names)`.

3. **`ai/assistant_run.py`**
   - `run_turn(..., allowed_tool_names=...)`:
     - Em cada `requires_action`, chama `dispatch_tool_call(name, args, allowed_tool_names=allowed_tool_names)`.

4. **`ai/tools/dispatch.py`**
   - `dispatch_tool_call(function_name, arguments, allowed_tool_names=...)`:
     - Se `allowed_tool_names` não for None e `function_name` não estiver em `allowed_tool_names`, retorna mensagem de "não disponível para este assistente" **sem executar**.
     - Caso contrário, segue o fluxo normal (AVAILABLE_FUNCTIONS + assinaturas específicas).

## Assistente customizado (PDF/vector store)

Conversas com upload de PDF criam um assistente customizado com as **mesmas** instruções e tools do agente escolhido + tool `file_search`. O `agent_id` continua na conversa; `get_agent_tool_names(agent_id)` continua sendo usado. O isolamento é mantido.
