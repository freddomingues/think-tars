# -*- coding: utf-8 -*-
"""
Script para verificar se as credenciais da Binance estão configuradas.
Execute na raiz do projeto: python -m ai.trading.verificar_credenciais
"""
import os
from dotenv import load_dotenv

# Raiz do projeto (ai/trading/ -> raiz)
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(_ROOT, '.env'))

print("=" * 60)
print("🔍 VERIFICAÇÃO DE CREDENCIAIS BINANCE")
print("=" * 60)

# Verifica se o arquivo .env existe
env_file = os.path.join(_ROOT, '.env')
if os.path.exists(env_file):
    print(f"✅ Arquivo .env encontrado: {env_file}")
else:
    print(f"❌ Arquivo .env NÃO encontrado: {env_file}")
    print("\n💡 Crie o arquivo .env na raiz do projeto com:")
    print("BINANCE_API_KEY=sua_api_key")
    print("BINANCE_API_SECRET=seu_secret_key")

print()

# Verifica variáveis de ambiente
api_key = os.getenv('BINANCE_API_KEY', '')
api_secret = os.getenv('BINANCE_API_SECRET', '')

if api_key:
    # Mostra apenas os primeiros e últimos caracteres por segurança
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print(f"✅ BINANCE_API_KEY encontrada: {masked_key}")
else:
    print("❌ BINANCE_API_KEY NÃO encontrada")

if api_secret:
    # Mostra apenas os primeiros e últimos caracteres por segurança
    masked_secret = api_secret[:8] + "..." + api_secret[-4:] if len(api_secret) > 12 else "***"
    print(f"✅ BINANCE_API_SECRET encontrada: {masked_secret}")
else:
    print("❌ BINANCE_API_SECRET NÃO encontrada")

print()

# Verifica se ambas estão configuradas
if api_key and api_secret:
    print("=" * 60)
    print("✅ CREDENCIAIS CONFIGURADAS CORRETAMENTE!")
    print("=" * 60)
    print("\nVocê pode executar o teste de compra:")
    print("  python -m ai.trading.trading_tools  # (ou script de teste equivalente)")
else:
    print("=" * 60)
    print("❌ CREDENCIAIS NÃO CONFIGURADAS")
    print("=" * 60)
    print("\n📝 Para configurar:")
    print("1. Edite o arquivo .env na raiz do projeto")
    print("2. Adicione as linhas:")
    print("   BINANCE_API_KEY=sua_api_key_aqui")
    print("   BINANCE_API_SECRET=seu_secret_key_aqui")
    print("\n📚 Veja o guia completo:")
    print("   ai/trading/ (documentação se existir)")

print()
