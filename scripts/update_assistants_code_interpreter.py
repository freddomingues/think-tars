#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar todos os assistentes existentes para incluir code_interpreter.
Isso permite que os assistentes leiam arquivos PDF e Excel.
"""
import sys
import os

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from config.settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def update_all_assistants():
    """Atualiza todos os assistentes para incluir code_interpreter."""
    print("🔍 Buscando assistentes...")
    
    # Busca todos os assistentes
    assistants = client.beta.assistants.list(order="desc", limit=100)
    
    if not assistants.data:
        print("❌ Nenhum assistente encontrado.")
        return
    
    print(f"📋 Encontrados {len(assistants.data)} assistentes.\n")
    
    updated_count = 0
    already_has_count = 0
    
    for assistant in assistants.data:
        print(f"📝 Processando: {assistant.name} (ID: {assistant.id})")
        
        # Verifica se já tem code_interpreter
        current_tools = []
        has_code_interpreter = False
        
        for t in (assistant.tools or []):
            tool_type = t.type if hasattr(t, "type") else (t.get("type") if isinstance(t, dict) else None)
            if tool_type == "code_interpreter":
                has_code_interpreter = True
            
            # Preserva a estrutura completa da tool
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
        
        if has_code_interpreter:
            print(f"   ✅ Já possui code_interpreter")
            already_has_count += 1
        else:
            # Adiciona code_interpreter
            current_tools.append({"type": "code_interpreter"})
            try:
                client.beta.assistants.update(
                    assistant_id=assistant.id,
                    tools=current_tools
                )
                print(f"   ✅ Atualizado com code_interpreter")
                updated_count += 1
            except Exception as e:
                print(f"   ❌ Erro ao atualizar: {e}")
        
        print()
    
    print(f"\n📊 Resumo:")
    print(f"   ✅ Atualizados: {updated_count}")
    print(f"   ✓ Já possuíam: {already_has_count}")
    print(f"   📦 Total: {len(assistants.data)}")

if __name__ == "__main__":
    try:
        update_all_assistants()
        print("\n✅ Concluído!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
