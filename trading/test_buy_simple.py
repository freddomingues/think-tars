# -*- coding: utf-8 -*-
"""
Teste simples de compra direto com a API da Binance.
"""
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

try:
    from binance.client import Client
    from binance.exceptions import BinanceAPIException, BinanceOrderException
    
    api_key = os.getenv('BINANCE_API_KEY', '')
    api_secret = os.getenv('BINANCE_API_SECRET', '')
    
    if not api_key or not api_secret:
        print("❌ Credenciais não configuradas")
        exit(1)
    
    print("=" * 60)
    print("🧪 TESTE DE COMPRA SIMPLES - $10 USD")
    print("=" * 60)
    
    client = Client(api_key=api_key, api_secret=api_secret)
    
    # Obtém preço atual
    print("\n📊 Obtendo preço atual...")
    ticker = client.get_symbol_ticker(symbol="BTCUSDT")
    btc_price = float(ticker['price'])
    print(f"✅ Preço BTC: ${btc_price:,.2f}")
    
    # Verifica saldo
    print("\n💼 Verificando saldo...")
    account = client.get_account()
    usdt_balance = float([b for b in account['balances'] if b['asset'] == 'USDT'][0]['free'])
    print(f"✅ Saldo USDT: ${usdt_balance:,.2f}")
    
    if usdt_balance < 10.0:
        print(f"\n❌ Saldo insuficiente! Necessário: $10.00, Disponível: ${usdt_balance:,.2f}")
        exit(1)
    
    # Valor a comprar
    valor_usd = 10.0
    print(f"\n💰 Valor a comprar: ${valor_usd:.2f} USD")
    
    # Confirmação
    print("\n" + "=" * 60)
    print("⚠️  ATENÇÃO: Esta é uma operação REAL!")
    print("=" * 60)
    print(f"Você está prestes a comprar ${valor_usd:.2f} USD em Bitcoin")
    print(f"Preço atual: ${btc_price:,.2f}")
    print("\nDeseja continuar? (digite 'SIM' para confirmar): ", end='')
    
    confirmacao = input().strip().upper()
    if confirmacao != 'SIM':
        print("❌ Operação cancelada")
        exit(0)
    
    # Tenta comprar usando quoteOrderQty (valor em USDT)
    print("\n🚀 Executando compra...")
    try:
        order = client.order_market_buy(
            symbol='BTCUSDT',
            quoteOrderQty=valor_usd  # Valor em USDT
        )
        
        print("\n" + "=" * 60)
        print("✅ COMPRA EXECUTADA COM SUCESSO!")
        print("=" * 60)
        print(f"\n📋 Detalhes da Ordem:")
        print(f"   - ID: {order.get('orderId')}")
        print(f"   - Status: {order.get('status')}")
        print(f"   - Quantidade: {order.get('executedQty')} BTC")
        print(f"   - Valor: ${float(order.get('cummulativeQuoteQty', 0)):.2f} USDT")
        print(f"   - Preço médio: ${float(order.get('price', 0)):,.2f}")
        
        # Verifica saldo atualizado
        import time
        time.sleep(2)
        account_after = client.get_account()
        btc_balance = float([b for b in account_after['balances'] if b['asset'] == 'BTC'][0]['free'])
        usdt_balance_after = float([b for b in account_after['balances'] if b['asset'] == 'USDT'][0]['free'])
        
        print(f"\n💼 Saldo atualizado:")
        print(f"   - BTC: {btc_balance:.8f}")
        print(f"   - USDT: ${usdt_balance_after:,.2f}")
        
    except BinanceOrderException as e:
        print(f"\n❌ Erro na ordem: {e}")
        print("\n💡 Possíveis causas:")
        print("   1. Permissão 'Enable Spot & Margin Trading' não está ativada")
        print("   2. IP não está na whitelist (se configurado)")
        print("   3. API key expirada ou inválida")
        print("\n📝 Verifique em:")
        print("   https://www.binance.com/en/my/settings/api-management")
    except BinanceAPIException as e:
        print(f"\n❌ Erro da API: {e}")
        print(f"   Código: {e.code}")
        print(f"   Mensagem: {e.message}")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
    
except ImportError:
    print("❌ Biblioteca python-binance não instalada")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

