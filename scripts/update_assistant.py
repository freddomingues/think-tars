#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar o assistente com instruções mais concisas.
Execute na raiz do projeto: python scripts/update_assistant.py
"""

import os
import sys

# Garante que a raiz do projeto está no PYTHONPATH
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from dotenv import load_dotenv
from ai.assistant_manager import update_assistant_instructions, list_all_assistants
from ai.agents import load_agent_instructions, load_agent_tools, DEFAULT_AGENT_ID

# Carrega variáveis de ambiente
load_dotenv()

def main():
    print("🔄 Atualizando assistente com instruções mais concisas...")
    
    # Lista assistentes existentes
    print("\n📋 Assistentes existentes:")
    list_all_assistants()
    
    # Usa automaticamente o primeiro assistente encontrado
    from openai import OpenAI
    from config.settings import OPENAI_API_KEY
    
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    assistants = openai_client.beta.assistants.list(order="desc", limit=1)
    
    if assistants.data:
        assistant_id = assistants.data[0].id
        print(f"✅ Usando assistente: {assistants.data[0].name} (ID: {assistant_id})")
    else:
        print("❌ Nenhum assistente encontrado!")
        return
    
    # Atualiza o assistente (usa tools e instruções do agente juridico)
    instructions = load_agent_instructions(DEFAULT_AGENT_ID)
    tools = load_agent_tools(DEFAULT_AGENT_ID)
    if not instructions or not tools:
        print("❌ Não foi possível carregar instruções ou tools do agente juridico.")
        return
    try:
        update_assistant_instructions(
            assistant_id=assistant_id,
            new_instructions=instructions,
            new_tools=tools
        )
        print("✅ Assistente atualizado com sucesso!")
        print("\n📝 Instruções do agente juridico aplicadas.")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar assistente: {e}")

if __name__ == "__main__":
    main()
