#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inicializar o sistema (app principal).
Execute na raiz do projeto: python scripts/start_system.py
"""

import os
import sys
import subprocess
import time
from multiprocessing import Process
from dotenv import load_dotenv

# Garante que a raiz do projeto está no PYTHONPATH
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

# Carrega variáveis de ambiente
load_dotenv()

def start_main_app():
    """Inicia a aplicação principal (Flask)."""
    print("🚀 Iniciando aplicação principal...")
    os.chdir(_root)
    env = os.environ.copy()
    env["PYTHONPATH"] = _root
    app_main = os.path.join(_root, "app", "main.py")
    subprocess.run([sys.executable, app_main], cwd=_root, env=env)

def main():
    print("🎯 Iniciando Sistema think-tars")
    print("=" * 50)
    
    required_vars = ['OPENAI_API_KEY', 'PINECONE_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        print("Configure essas variáveis no arquivo .env")
        sys.exit(1)
    
    print("\n🎯 Sistema iniciado com sucesso!")
    print("📱 Aplicação: http://localhost:5004 (ou porta configurada)")
    print("\nPressione Ctrl+C para parar o sistema")
    
    try:
        start_main_app()
    except KeyboardInterrupt:
        print("\n⏹️  Parando sistema...")
        print("✅ Sistema parado com sucesso!")

if __name__ == "__main__":
    main()
