#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inicializar o sistema completo com dashboard e análise de sentimento.
"""

import os
import sys
import subprocess
import time
from multiprocessing import Process
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def start_main_app():
    """Inicia a aplicação principal."""
    print("🚀 Iniciando aplicação principal...")
    os.system("cd /Users/freddomingues/Desenvolvimento/genai && export PYTHONPATH=/Users/freddomingues/Desenvolvimento/genai && source venv/bin/activate && python app/main.py")

def start_dashboard():
    """Inicia o dashboard."""
    print("📊 Iniciando dashboard...")
    os.system("cd /Users/freddomingues/Desenvolvimento/genai && export PYTHONPATH=/Users/freddomingues/Desenvolvimento/genai && source venv/bin/activate && python dashboard/app.py")

def create_tables():
    """Cria as tabelas necessárias."""
    print("🗄️  Criando tabelas do banco de dados...")
    try:
        from data_store.conversation_schema import conversation_manager
        conversation_manager.create_tables()
        print("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")

def main():
    print("🎯 Iniciando Sistema de Análise de Sentimento")
    print("=" * 50)
    
    # Verifica se as variáveis de ambiente estão configuradas
    required_vars = ['OPENAI_API_KEY', 'PINECONE_API_KEY', 'AWS_ACCESS_KEY_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        print("Configure essas variáveis no arquivo .env")
        sys.exit(1)
    
    # Cria tabelas
    create_tables()
    
    print("\n🎯 Sistema iniciado com sucesso!")
    print("📱 Aplicação principal: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5001")
    print("\nPressione Ctrl+C para parar o sistema")
    
    try:
        # Inicia aplicação principal em processo separado
        main_process = Process(target=start_main_app)
        main_process.start()
        
        # Aguarda um pouco para a aplicação principal inicializar
        time.sleep(3)
        
        # Inicia dashboard
        start_dashboard()
        
    except KeyboardInterrupt:
        print("\n⏹️  Parando sistema...")
        main_process.terminate()
        main_process.join()
        print("✅ Sistema parado com sucesso!")

if __name__ == "__main__":
    main()
