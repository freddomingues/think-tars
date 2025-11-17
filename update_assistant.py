#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar o assistente com instruções mais concisas.
"""

import os
from dotenv import load_dotenv
from llm_assistant.assistant_manager import update_assistant_instructions, list_all_assistants
from llm_assistant.prompt_templates import DEFAULT_ASSISTANT_INSTRUCTIONS
from llm_assistant.tools import TOOLS_DEFINITION

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
    
    # Atualiza o assistente
    try:
        update_assistant_instructions(
            assistant_id=assistant_id,
            new_instructions=DEFAULT_ASSISTANT_INSTRUCTIONS,
            new_tools=TOOLS_DEFINITION
        )
        print("✅ Assistente atualizado com sucesso!")
        print("\n📝 Novas instruções:")
        print(DEFAULT_ASSISTANT_INSTRUCTIONS)
        
    except Exception as e:
        print(f"❌ Erro ao atualizar assistente: {e}")

if __name__ == "__main__":
    main()
