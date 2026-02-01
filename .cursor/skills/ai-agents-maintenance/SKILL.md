---
name: ai-agents-maintenance
description: Manutenção de agentes de IA — registry, prompts, tools, isolamento, code_interpreter. Use ao criar/editar agentes, ajustar prompts, adicionar tools ou debug. Triggers: "novo agente", "ajustar prompt", "nova tool", "agente não funciona", "isolamento", "code_interpreter".
---

# Skill: Manutenção de Agentes de IA

Como manter, criar e debugar agentes de IA do Playground.

---

## 1. Estrutura de Agentes

### Registry

- **Arquivo:** `ai/agents.py`
- **AGENTS_REGISTRY:** Agentes do Playground (aparecem no site)
- **INTERNAL_AGENTS_REGISTRY:** Agentes internos (ex: SDR)

### Componentes de um Agente

1. **Registry Entry** (`ai/agents.py`)
2. **Prompt/Instruções** (`ai/prompts/<agent_id>.py`)
3. **Tools Definition** (`ai/tools/<agent_id>.py`)
4. **Tool Implementation** (`ai/tools/base.py`)

---

## 2. Criar Novo Agente

### 1. Adicionar ao Registry

Em `ai/agents.py`, adicionar em `AGENTS_REGISTRY`:

```python
{
    "id": "novo_agente",
    "name": "Nome do Agente",
    "instructions_module": "ai.prompts.novo_agente",
    "instructions_attr": "NOVO_AGENTE_ASSISTANT_INSTRUCTIONS",
    "tools_module": "ai.tools.novo_agente",
    "tools_attr": "TOOLS_DEFINITION",
    "playground": True,
}
```

### 2. Criar Prompt

Criar `ai/prompts/novo_agente.py`:

```python
NOVO_AGENTE_ASSISTANT_INSTRUCTIONS = """
Você é um assistente especializado em [área].

Objetivos:
- [objetivo 1]
- [objetivo 2]

Regras:
- [regra 1]
- [regra 2]

Limitações:
- Não mencione outros agentes
- Use apenas suas próprias tools
"""
```

### 3. Criar Tools Definition

Criar `ai/tools/novo_agente.py`:

```python
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "nova_tool",
            "description": "Descrição da tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Descrição do parâmetro"
                    }
                },
                "required": ["param1"]
            }
        }
    }
]
```

### 4. Implementar Tool

Em `ai/tools/base.py`, adicionar função:

```python
def nova_tool(param1: str) -> dict:
    """Implementação da tool."""
    # Lógica aqui
    return {"result": "ok"}
```

E registrar em `AVAILABLE_FUNCTIONS`:

```python
AVAILABLE_FUNCTIONS = {
    # ... outras tools
    "nova_tool": nova_tool,
}
```

### 5. Adicionar Dispatch (se necessário)

Em `ai/tools/dispatch.py`, adicionar branch se a assinatura for especial:

```python
def dispatch_tool_call(name: str, args: dict, allowed_tool_names: set = None):
    # ... código existente
    if name == "nova_tool":
        return nova_tool(**args)
```

---

## 3. Editar Prompt de Agente Existente

### Localizar Prompt

1. Verificar `ai/agents.py` para encontrar `instructions_module`
2. Abrir arquivo em `ai/prompts/<agent_id>.py`
3. Editar a constante (ex: `JURIDICO_ASSISTANT_INSTRUCTIONS`)

### Atualizar Assistente

Após editar prompt, atualizar assistente existente:

```bash
python scripts/update_assistant.py
```

Ou criar script específico:

```python
from ai.assistant_manager import update_assistant_instructions
from ai.agents import load_agent_instructions, get_agent_config

agent_id = "juridico"
config = get_agent_config(agent_id)
instructions = load_agent_instructions(agent_id)
assistant_id = create_or_get_assistant_from_registry(agent_id)

update_assistant_instructions(assistant_id, instructions)
```

---

## 4. Adicionar Tool a Agente Existente

### 1. Adicionar Tool Definition

Em `ai/tools/<agent_id>.py`, adicionar à lista `TOOLS_DEFINITION`:

```python
TOOLS_DEFINITION = [
    # ... tools existentes
    {
        "type": "function",
        "function": {
            "name": "nova_tool",
            # ... definição
        }
    }
]
```

### 2. Implementar Tool

Seguir passos 4 e 5 da seção "Criar Novo Agente"

### 3. Atualizar Assistente

```bash
python scripts/update_assistant.py
```

---

## 5. Isolamento de Agentes

### Princípio

Cada agente usa **apenas** suas próprias tools. O dispatch verifica `allowed_tool_names` e bloqueia tools de outros agentes.

### Verificar Isolamento

```python
from ai.agents import get_agent_tool_names

# Obter tools permitidas para um agente
allowed = get_agent_tool_names("juridico")
# Retorna: {"search_contracts", "search_faqs"}

# Tentar usar tool de outro agente retorna erro
```

### Garantir Isolamento

1. **Prompts:** Nunca mencionar tools de outros agentes
2. **Tools:** Cada agente tem seu próprio módulo
3. **Dispatch:** Verifica `allowed_tool_names` antes de executar

---

## 6. Code Interpreter

### Habilitar para Agente

O `code_interpreter` é adicionado automaticamente em `ai/assistant_manager.py`:

```python
# Em _create_or_get
if {"type": "code_interpreter"} not in tools:
    tools.append({"type": "code_interpreter"})
```

### Usar Code Interpreter

Agentes podem analisar arquivos (PDF, Excel, CSV) usando `code_interpreter`:

1. Cliente faz upload de arquivo
2. Arquivo é enviado para OpenAI
3. `file_id` é anexado à mensagem com `tools=[{"type": "code_interpreter"}]`
4. Agente analisa arquivo usando Python

### Atualizar Todos os Agentes

```bash
python scripts/update_assistants_code_interpreter.py
```

---

## 7. Debugging

### Testar Carregamento de Agente

```bash
python scripts/test_agents.py
```

### Verificar Registry

```python
from ai.agents import AGENTS_REGISTRY, get_agent_config

# Listar todos os agentes
for agent in AGENTS_REGISTRY:
    print(f"{agent['id']}: {agent['name']}")

# Verificar agente específico
config = get_agent_config("juridico")
print(config)
```

### Verificar Prompt e Tools

```python
from ai.agents import load_agent_instructions, load_agent_tools

# Carregar instruções
instructions = load_agent_instructions("juridico")
print(instructions[:200])  # Primeiros 200 caracteres

# Carregar tools
tools = load_agent_tools("juridico")
print(tools)
```

### Logs

Verificar logs do backend para:
- "✅ Assistant ID obtido: ..."
- Erros ao carregar prompts/tools
- Erros ao criar/atualizar assistentes

---

## 8. Boas Práticas

1. **Isolamento:** Cada agente tem seu próprio contexto e tools
2. **Prompts claros:** Instruções específicas e objetivas
3. **Tools bem definidas:** Descrições claras dos parâmetros
4. **Error handling:** Tratar erros nas implementações de tools
5. **Logging:** Registrar uso de tools para debug
6. **Testes:** Testar agente após criar/editar

---

## 9. Referências

- **Registry:** `ai/agents.py`
- **Manager:** `ai/assistant_manager.py`
- **Run:** `ai/assistant_run.py`
- **Tools:** `ai/tools/`
- **Prompts:** `ai/prompts/`
- **Criar Agente:** `.cursor/skills/assistant-creator/`
- **Isolamento:** `.cursor/skills/assistant-engineer/`
