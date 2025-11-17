#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e criar tabelas necessárias no DynamoDB.
"""

import sys
import os
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Carrega variáveis de ambiente
load_dotenv()

from data_store.conversation_schema import conversation_manager

def main():
    """Verifica e cria as tabelas necessárias."""
    print("🔍 Verificando estrutura do banco de dados...")
    print("-" * 60)
    
    try:
        # Tenta criar as tabelas
        print("📝 Criando/verificando tabelas...")
        conversation_manager.create_tables()
        
        print("-" * 60)
        print("✅ Estrutura do banco de dados configurada com sucesso!")
        print()
        print("📋 Tabelas criadas/verificadas:")
        print("   - Messages: Armazena todas as mensagens trocadas")
        print("   - Conversations: Armazena informações das conversas")
        print("   - SentimentAnalysis: Armazena análises de sentimento")
        print()
        print("🚀 O sistema está pronto para uso!")
        
    except Exception as e:
        print(f"❌ Erro ao configurar banco de dados: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

