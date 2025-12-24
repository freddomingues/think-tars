# -*- coding: utf-8 -*-
"""
Script para vender todo o Bitcoin disponível na conta.
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
    print("💸 VENDA DE TODO O BITCOIN")
    print("=" * 60)
    
    client = Client(api_key=api_key, api_secret=api_secret)
    
    # Verifica saldo de BTC
    print("\n💼 Verificando saldo...")
    account = client.get_account()
    btc_balance = float([b for b in account['balances'] if b['asset'] == 'BTC'][0]['free'])
    usdt_balance = float([b for b in account['balances'] if b['asset'] == 'USDT'][0]['free'])
    
    print(f"   - BTC disponível: {btc_balance:.8f}")
    print(f"   - USDT atual: ${usdt_balance:,.2f}")
    
    if btc_balance < 0.00001:
        print("\n❌ Saldo de BTC insuficiente para vender!")
        print("   Mínimo necessário: 0.00001 BTC")
        exit(1)
    
    # Obtém preço atual
    print("\n📊 Obtendo preço atual...")
    ticker = client.get_symbol_ticker(symbol="BTCUSDT")
    btc_price = float(ticker['price'])
    print(f"✅ Preço BTC: ${btc_price:,.2f}")
    
    # Calcula valor estimado
    valor_estimado_usdt = btc_balance * btc_price
    print(f"\n💰 Valor estimado da venda: ${valor_estimado_usdt:,.2f} USDT")
    
    # Confirmação
    print("\n" + "=" * 60)
    print("⚠️  ATENÇÃO: Esta é uma operação REAL!")
    print("=" * 60)
    print(f"Você está prestes a VENDER:")
    print(f"  - Quantidade: {btc_balance:.8f} BTC")
    print(f"  - Valor estimado: ${valor_estimado_usdt:,.2f} USDT")
    print(f"  - Preço: ${btc_price:,.2f} por BTC")
    print("\nDeseja continuar? (digite 'SIM' para confirmar): ", end='')
    
    confirmacao = input().strip().upper()
    if confirmacao != 'SIM':
        print("❌ Operação cancelada")
        exit(0)
    
    # Obtém informações do símbolo para ajustar quantidade
    print("\n🔧 Ajustando quantidade...")
    try:
        exchange_info = client.get_exchange_info()
        symbol_info = next((s for s in exchange_info['symbols'] if s['symbol'] == 'BTCUSDT'), None)
        
        if symbol_info:
            # Encontra o filtro LOT_SIZE
            lot_size = next((f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE'), None)
            if lot_size:
                step_size = float(lot_size['stepSize'])
                min_qty = float(lot_size['minQty'])
                
                print(f"   - Quantidade mínima: {min_qty:.8f} BTC")
                print(f"   - Step size: {step_size:.8f}")
                
                # Ajusta quantidade para o step size
                # Arredonda para baixo para o step size mais próximo
                adjusted_qty = (btc_balance // step_size) * step_size
                
                if adjusted_qty < min_qty:
                    print(f"\n❌ Quantidade ajustada ({adjusted_qty:.8f} BTC) está abaixo do mínimo ({min_qty:.8f} BTC)")
                    print("   Não é possível vender esta quantidade")
                    exit(1)
                
                if adjusted_qty < btc_balance:
                    print(f"   ⚠️ Quantidade ajustada de {btc_balance:.8f} para {adjusted_qty:.8f} BTC (step size)")
                    btc_balance = adjusted_qty
        else:
            print("   ⚠️ Não foi possível obter informações do símbolo, usando quantidade original")
    except Exception as e:
        print(f"   ⚠️ Erro ao obter informações: {e}, usando quantidade original")
    
    # Executa a venda
    print("\n🚀 Executando venda...")
    try:
        # Formata quantidade para string com precisão correta (8 casas decimais)
        quantity_str = f"{btc_balance:.8f}".rstrip('0').rstrip('.')
        
        # Vende todo o BTC disponível
        order = client.order_market_sell(
            symbol='BTCUSDT',
            quantity=quantity_str  # Quantidade de BTC a vender
        )
        
        print("\n" + "=" * 60)
        print("✅ VENDA EXECUTADA COM SUCESSO!")
        print("=" * 60)
        print(f"\n📋 Detalhes da Ordem:")
        print(f"   - ID: {order.get('orderId')}")
        print(f"   - Status: {order.get('status')}")
        print(f"   - Quantidade: {order.get('executedQty')} BTC")
        
        # Calcula valor recebido
        cummulative_quote_qty = float(order.get('cummulativeQuoteQty', 0))
        print(f"   - Valor recebido: ${cummulative_quote_qty:,.2f} USDT")
        
        if order.get('price'):
            print(f"   - Preço médio: ${float(order.get('price')):,.2f}")
        
        # Verifica saldo atualizado
        import time
        time.sleep(2)
        print("\n💼 Verificando saldo atualizado...")
        account_after = client.get_account()
        btc_balance_after = float([b for b in account_after['balances'] if b['asset'] == 'BTC'][0]['free'])
        usdt_balance_after = float([b for b in account_after['balances'] if b['asset'] == 'USDT'][0]['free'])
        
        print(f"   - BTC: {btc_balance_after:.8f}")
        print(f"   - USDT: ${usdt_balance_after:,.2f}")
        
        # Calcula lucro/prejuízo (se possível)
        if btc_balance > 0:
            preco_medio_venda = cummulative_quote_qty / float(order.get('executedQty', 1))
            print(f"\n📊 Resumo:")
            print(f"   - BTC vendido: {float(order.get('executedQty', 0)):.8f}")
            print(f"   - USDT recebido: ${cummulative_quote_qty:,.2f}")
            print(f"   - Preço médio de venda: ${preco_medio_venda:,.2f}")
        
    except BinanceOrderException as e:
        print(f"\n❌ Erro na ordem: {e}")
        print("\n💡 Possíveis causas:")
        print("   1. Quantidade muito pequena (mínimo 0.00001 BTC)")
        print("   2. Permissão 'Enable Spot & Margin Trading' não está ativada")
        print("   3. IP não está na whitelist (se configurado)")
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

