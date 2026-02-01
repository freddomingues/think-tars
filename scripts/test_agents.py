#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar se todos os agentes podem ser carregados corretamente.
Execute na raiz do projeto: python scripts/test_agents.py
"""

import os
import sys

# Garante que a raiz do projeto está no PYTHONPATH
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from dotenv import load_dotenv
load_dotenv()

def test_agent_loading():
    """Testa se todos os agentes podem ser carregados."""
    from ai.agents import AGENTS_REGISTRY, load_agent_instructions, load_agent_tools
    
    print("=" * 60)
    print("🧪 TESTE DE CARREGAMENTO DE AGENTES")
    print("=" * 60)
    
    playground_agents = [a for a in AGENTS_REGISTRY if a.get("playground", True)]
    print(f"\n📋 Total de agentes no Playground: {len(playground_agents)}\n")
    
    errors = []
    success = []
    
    for agent in playground_agents:
        agent_id = agent["id"]
        agent_name = agent["name"]
        print(f"🔍 Testando: {agent_name} ({agent_id})")
        
        try:
            # Testa carregamento de instruções
            instructions = load_agent_instructions(agent_id)
            if not instructions:
                raise ValueError(f"Instruções não encontradas para {agent_id}")
            
            # Testa carregamento de tools
            tools = load_agent_tools(agent_id)
            if tools is None:
                raise ValueError(f"Tools não encontradas para {agent_id}")
            
            print(f"  ✅ OK - Instruções: {len(instructions)} chars, Tools: {len(tools)}")
            success.append(agent_id)
            
        except Exception as e:
            print(f"  ❌ ERRO: {str(e)}")
            errors.append((agent_id, str(e)))
    
    print("\n" + "=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    print(f"✅ Sucesso: {len(success)}/{len(playground_agents)}")
    print(f"❌ Erros: {len(errors)}/{len(playground_agents)}")
    
    if errors:
        print("\n❌ AGENTES COM ERRO:")
        for agent_id, error in errors:
            print(f"  - {agent_id}: {error}")
        return False
    else:
        print("\n✅ Todos os agentes foram carregados com sucesso!")
        return True

if __name__ == "__main__":
    success = test_agent_loading()
    sys.exit(0 if success else 1)