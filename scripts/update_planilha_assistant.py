#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar o assistente de planilhas com as novas instruções.
"""
import os
import sys

# Garante que a raiz do projeto está no PYTHONPATH
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from openai import OpenAI
from config.settings import OPENAI_API_KEY
from ai.agents import load_agent_instructions, load_agent_tools

# Carrega variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=OPENAI_API_KEY)

def update_planilha_assistant():
    """Atualiza o assistente de planilhas com novas instruções."""
    print("🔄 Atualizando assistente de planilhas...")
    
    # Carrega instruções e tools do agente planilha
    instructions = load_agent_instructions("planilha")
    tools = load_agent_tools("planilha")
    
    if not instructions or not tools:
        print("❌ Não foi possível carregar instruções ou tools do agente planilha.")
        return
    
    # Adiciona code_interpreter às tools
    tools_with_code = list(tools) if tools else []
    has_code = any(t.get("type") == "code_interpreter" if isinstance(t, dict) else getattr(t, "type", None) == "code_interpreter" for t in tools_with_code)
    if not has_code:
        tools_with_code.append({"type": "code_interpreter"})
    
    # Busca o assistente de planilhas
    assistants = client.beta.assistants.list(order="desc", limit=100)
    planilha_assistant = None
    
    for a in assistants.data:
        if "planilha" in a.name.lower() or "excel" in a.name.lower() or "dados" in a.name.lower():
            planilha_assistant = a
            break
    
    if not planilha_assistant:
        print("❌ Assistente de planilhas não encontrado!")
        return
    
    print(f"📝 Encontrado: {planilha_assistant.name} (ID: {planilha_assistant.id})")
    
    try:
        # Atualiza o assistente
        client.beta.assistants.update(
            assistant_id=planilha_assistant.id,
            instructions=instructions,
            tools=tools_with_code
        )
        print("✅ Assistente de planilhas atualizado com sucesso!")
        print("   - Instruções atualizadas")
        print("   - code_interpreter habilitado")
        print("\n💡 O agente agora pode analisar arquivos Excel anexados às mensagens!")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar assistente: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        update_planilha_assistant()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
