# ai/assistant_manager.py
import logging
from openai import OpenAI
from config.settings import OPENAI_API_KEY, LLM_MODEL

logger = logging.getLogger(__name__)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def _create_or_get(name: str, instructions: str, tools: list) -> str | None:
    """Cria ou recupera assistente por nome, com instruções e tools dados."""
    try:
        # Adiciona code_interpreter para permitir leitura de arquivos (PDF, Excel, etc.)
        tools_list = list(tools) if tools else []
        # Verifica se code_interpreter já está nas tools
        has_code_interpreter = False
        for t in tools_list:
            tool_type = t.get("type") if isinstance(t, dict) else (getattr(t, "type", None) if hasattr(t, "type") else None)
            if tool_type == "code_interpreter":
                has_code_interpreter = True
                break
        
        if not has_code_interpreter:
            tools_list.append({"type": "code_interpreter"})
        
        assistants = openai_client.beta.assistants.list(order="desc", limit=100)
        for a in assistants.data:
            if a.name == name:
                # Atualiza o assistente existente para incluir code_interpreter se necessário
                current_tools = []
                for t in (a.tools or []):
                    if hasattr(t, "type"):
                        tool_dict = {"type": t.type}
                        # Se for function tool, preserva o campo function completo
                        if t.type == "function" and hasattr(t, "function"):
                            tool_dict["function"] = {
                                "name": t.function.name,
                                "description": t.function.description,
                                "parameters": t.function.parameters
                            }
                        current_tools.append(tool_dict)
                    elif isinstance(t, dict):
                        current_tools.append(t)
                
                has_code = any(t.get("type") == "code_interpreter" for t in current_tools)
                if not has_code:
                    current_tools.append({"type": "code_interpreter"})
                    try:
                        openai_client.beta.assistants.update(
                            assistant_id=a.id,
                            tools=current_tools
                        )
                        logger.info(f"Assistente {a.id} atualizado com code_interpreter")
                    except Exception as e:
                        logger.warning(f"Não foi possível atualizar tools do assistente {a.id}: {e}")
                return a.id
        
        created = openai_client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=LLM_MODEL,
            tools=tools_list,
        )
        return created.id
    except Exception:
        return None


def create_or_get_assistant(assistant_name: str = "Assistente Jurídico de Contratos") -> str | None:
    """
    Cria ou recupera assistente por nome. Usa o agente padrão do registry (juridico).
    """
    from ai.agents import DEFAULT_AGENT_ID
    return create_or_get_assistant_from_registry(DEFAULT_AGENT_ID)


def create_or_get_assistant_from_registry(agent_id: str) -> str | None:
    """
    Cria ou recupera assistente via ai.agents (registry).
    Carrega instruções e tools do módulo indicado no registry.
    """
    from ai.agents import get_agent_config, load_agent_instructions, load_agent_tools

    cfg = get_agent_config(agent_id)
    if not cfg:
        return None
    instructions = load_agent_instructions(agent_id)
    tools = load_agent_tools(agent_id)
    if instructions is None or tools is None:
        return None
    return _create_or_get(cfg["name"], instructions, tools)

def update_assistant_instructions(assistant_id: str, new_instructions: str, new_tools: list = None):
    """Atualiza as instruções (system prompt) E as ferramentas de um assistente existente."""
    update_params = {"instructions": new_instructions}
    if new_tools is not None:
        update_params["tools"] = new_tools 

    try:
        updated_assistant = openai_client.beta.assistants.update(
            assistant_id=assistant_id,
            **update_params
        )
    except Exception as e:
        print(f"Erro ao atualizar as instruções do Assistente: {e}")

def list_all_assistants():
    """Lista todos os assistentes criados."""
    try:
        my_assistants = openai_client.beta.assistants.list(order="desc", limit="100")
        if not my_assistants.data:
            print("Nenhum assistente encontrado.")
        else:
            for assistant in my_assistants.data:
                print(f"- Nome: {assistant.name}, ID: {assistant.id}")
    except Exception as e:
        print(f"Erro ao listar os Assistentes: {e}")

def delete_assistant(assistant_id: str):
    """Deleta um assistente pelo ID."""
    try:
        response = openai_client.beta.assistants.delete(assistant_id)
        if response.deleted:
            print(f"Assistente com ID '{assistant_id}' removido com sucesso!")
        else:
            print(f"Falha ao remover o Assistente com ID '{assistant_id}'.")
    except Exception as e:
        print(f"Erro ao remover o Assistente: {e}")

def get_assistant_tools(assistant_id: str):
    """Lista as ferramentas configuradas para um assistente."""
    try:
        assistant = openai_client.beta.assistants.retrieve(assistant_id)
        print(f"\nFerramentas para o Assistente '{assistant.name}' (ID: {assistant.id}):")
        if not assistant.tools:
            print("  Nenhuma ferramenta configurada para este assistente.")
        else:
            for tool in assistant.tools:
                tool_type = tool.type
                print(f"  - Tipo de Ferramenta: {tool_type}")
                if tool_type == "function":
                    print(f"    Nome da Função: {tool.function.name}")
                    print(f"    Descrição da Função: {tool.function.description}")
    except Exception as e:
        print(f"Erro ao recuperar o assistente ou suas ferramentas: {e}")
