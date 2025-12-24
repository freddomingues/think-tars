# -*- coding: utf-8 -*-
"""
Script para testar permissões da API da Binance.
"""
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

try:
    from binance.client import Client
    from binance.exceptions import BinanceAPIException
    
    api_key = os.getenv('BINANCE_API_KEY', '')
    api_secret = os.getenv('BINANCE_API_SECRET', '')
    
    if not api_key or not api_secret:
        print("❌ Credenciais não configuradas")
        exit(1)
    
    print("=" * 60)
    print("🔍 TESTANDO PERMISSÕES DA API BINANCE")
    print("=" * 60)
    
    client = Client(api_key=api_key, api_secret=api_secret)
    
    # Teste 1: Informações da conta (requer Enable Reading)
    print("\n1️⃣ Testando permissão de leitura...")
    try:
        account = client.get_account()
        print("   ✅ Permissão de leitura: OK")
        print(f"   📊 Saldo USDT: ${float([b for b in account['balances'] if b['asset'] == 'USDT'][0]['free']):,.2f}")
    except BinanceAPIException as e:
        print(f"   ❌ Erro na leitura: {e}")
        print("   💡 Verifique se 'Enable Reading' está ativado na API")
    
    # Teste 2: Preço (não requer permissões especiais)
    print("\n2️⃣ Testando obtenção de preço...")
    try:
        ticker = client.get_symbol_ticker(symbol="BTCUSDT")
        print(f"   ✅ Preço obtido: ${float(ticker['price']):,.2f}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste 3: Status da API
    print("\n3️⃣ Testando status da API...")
    try:
        status = client.get_system_status()
        print(f"   ✅ Status da API: {status.get('status', 'N/A')}")
    except Exception as e:
        print(f"   ⚠️ Não foi possível verificar status: {e}")
    
    # Teste 4: Informações sobre a API key
    print("\n4️⃣ Verificando informações da API...")
    try:
        # Tenta obter informações da API (se disponível)
        print("   💡 Verifique manualmente na Binance:")
        print("      https://www.binance.com/en/my/settings/api-management")
        print("   📋 Permissões necessárias:")
        print("      ✅ Enable Reading")
        print("      ✅ Enable Spot & Margin Trading")
        print("   🔒 Se configurou IP whitelist:")
        print("      Adicione seu IP atual à lista")
    except Exception as e:
        pass
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído")
    print("=" * 60)
    
except ImportError:
    print("❌ Biblioteca python-binance não instalada")
    print("   Execute: pip install python-binance")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

