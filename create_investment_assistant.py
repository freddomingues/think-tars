# -*- coding: utf-8 -*-
"""
Script para criar o Assistente de Análise de Investimento.
Este script é independente e não requer Pinecone ou outras dependências além de OpenAI e Binance.
"""
import sys
import os

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa diretamente do OpenAI para evitar dependências do Pinecone
from openai import OpenAI
from config.settings import OPENAI_API_KEY, LLM_MODEL

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def create_or_get_assistant(assistant_name: str) -> str:
    """Cria um novo assistente ou recupera um existente com base no nome."""
    try:
        my_assistants = openai_client.beta.assistants.list(order="desc", limit="100")
        for existing_assistant in my_assistants.data:
            if existing_assistant.name == assistant_name:
                return existing_assistant.id
        
        # Se não encontrou, cria um novo (sem tools por enquanto, será atualizado depois)
        assistant = openai_client.beta.assistants.create(
            name=assistant_name,
            instructions="",
            model=LLM_MODEL,
            tools=[]
        )
        return assistant.id
    except Exception as e:
        print(f"Erro ao criar/obter o Assistente: {e}")
        return None

def update_assistant_instructions(assistant_id: str, new_instructions: str, new_tools: list = None):
    """Atualiza as instruções e ferramentas de um assistente existente."""
    update_params = {"instructions": new_instructions}
    if new_tools is not None:
        update_params["tools"] = new_tools
    
    try:
        updated_assistant = openai_client.beta.assistants.update(
            assistant_id=assistant_id,
            **update_params
        )
        return updated_assistant
    except Exception as e:
        print(f"Erro ao atualizar as instruções do Assistente: {e}")
        raise
from llm_assistant.investment_prompts import INVESTMENT_ASSISTANT_INSTRUCTIONS
from trading.trading_tools_definition import TRADING_TOOLS_DEFINITION
from config.settings import LLM_MODEL

def create_investment_assistant():
    """Cria ou atualiza o assistente de investimento."""
    print("🚀 Criando Assistente de Análise de Investimento...")
    
    assistant_id = create_or_get_assistant("Analista de Investimento Bitcoin")
    
    if not assistant_id:
        print("❌ Falha ao criar/obter assistente")
        return None
    
    print(f"✅ Assistente ID: {assistant_id}")
    
    # Atualiza instruções e ferramentas (apenas ferramentas de trading)
    print("📝 Atualizando instruções e ferramentas...")
    update_assistant_instructions(
        assistant_id=assistant_id,
        new_instructions=INVESTMENT_ASSISTANT_INSTRUCTIONS,
        new_tools=TRADING_TOOLS_DEFINITION
    )
    
    print("✅ Assistente de Investimento configurado com sucesso!")
    print(f"\n📋 ID do Assistente: {assistant_id}")
    print("\n🔧 Ferramentas disponíveis:")
    print("   - analyze_bitcoin_market: Análise técnica completa")
    print("   - get_bitcoin_price: Preço atual")
    print("   - get_portfolio_status: Status do portfólio")
    print("   - buy_bitcoin: Compra seguindo estratégia")
    print("   - sell_bitcoin: Venda seguindo estratégia")
    
    return assistant_id

if __name__ == "__main__":
    create_investment_assistant()

