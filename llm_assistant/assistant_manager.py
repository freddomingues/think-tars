# llm_assistant/assistant_manager.py
from openai import OpenAI
from config.settings import OPENAI_API_KEY, LLM_MODEL
from llm_assistant.prompt_templates import DEFAULT_ASSISTANT_INSTRUCTIONS

# Importação opcional de TOOLS_DEFINITION para evitar dependências do Pinecone
try:
    from llm_assistant.tools import TOOLS_DEFINITION
except (ImportError, ValueError):
    # Se houver erro (ex: Pinecone não configurado), usa lista vazia
    TOOLS_DEFINITION = []

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def create_or_get_assistant(assistant_name: str = "Assistente Jurídico de Contratos") -> str:
    """
    Cria um novo assistente ou recupera um existente com base no nome.
    Retorna o ID do assistente.
    """
    try:
        # Tenta listar assistentes e encontrar um com o nome
        my_assistants = openai_client.beta.assistants.list(order="desc", limit="100")
        for existing_assistant in my_assistants.data:
            if existing_assistant.name == assistant_name:
                #print(f"Assistente '{assistant_name}' já existe! ID: {existing_assistant.id}")
                return existing_assistant.id

        # Se não encontrou, cria um novo
        assistant = openai_client.beta.assistants.create(
            name=assistant_name,
            instructions=DEFAULT_ASSISTANT_INSTRUCTIONS,
            model=LLM_MODEL,
            tools=TOOLS_DEFINITION
        )
        #print(f"Assistente '{assistant_name}' criado com sucesso! ID: {assistant.id}")
        return assistant.id

    except Exception as e:
        #print(f"Erro ao criar/obter o Assistente: {e}")
        return None

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
        #print(f"Assistente '{updated_assistant.name}' (ID: {updated_assistant.id}) atualizado com sucesso!")
        #print(f"Novas instruções: {updated_assistant.instructions[:100]}...") # Printa apenas um trecho
    except Exception as e:
        print(f"Erro ao atualizar as instruções do Assistente: {e}")

def list_all_assistants():
    """Lista todos os assistentes criados."""
    try:
        my_assistants = openai_client.beta.assistants.list(order="desc", limit="100")
        #print("\nAssistentes existentes:")
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
                # Adicione mais detalhes para outros tipos de ferramentas, se necessário
    except Exception as e:
        print(f"Erro ao recuperar o assistente ou suas ferramentas: {e}")