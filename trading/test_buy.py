# -*- coding: utf-8 -*-
"""
Script de teste para comprar uma pequena quantia de Bitcoin.
Compra R$ 0,50 (aproximadamente $0,10 USD) em Bitcoin.
"""
import sys
import os
import logging
from decimal import Decimal

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carrega variáveis de ambiente ANTES de importar
from dotenv import load_dotenv
load_dotenv()

# Importa biblioteca Binance diretamente
try:
    from binance.client import Client
    from binance.exceptions import BinanceAPIException, BinanceOrderException
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False
    Client = None

import os

# Obtém credenciais diretamente
api_key = os.getenv('BINANCE_API_KEY', '')
api_secret = os.getenv('BINANCE_API_SECRET', '')

# Cria cliente Binance diretamente
if BINANCE_AVAILABLE and api_key and api_secret:
    binance_client_direct = Client(api_key=api_key, api_secret=api_secret)
else:
    binance_client_direct = None

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_usd_to_brl_rate():
    """
    Obtém a taxa de conversão USD/BRL.
    Por simplicidade, vamos usar uma taxa fixa aproximada.
    Você pode melhorar isso usando uma API de câmbio.
    """
    # Taxa aproximada (ajuste conforme necessário)
    # Em produção, use uma API de câmbio como exchangerate-api.com
    return 5.0  # 1 USD ≈ 5 BRL


def buy_50_centavos():
    """
    Compra $10 USD (mínimo da Binance) em Bitcoin.
    """
    print("=" * 60)
    print("🧪 TESTE DE COMPRA - $10 USD em Bitcoin (Mínimo)")
    print("=" * 60)
    
    # Verifica credenciais
    if not api_key or not api_secret:
        print("❌ ERRO: Credenciais da Binance não configuradas!")
        print("\nPor favor, adicione ao arquivo .env:")
        print("BINANCE_API_KEY=sua_api_key")
        print("BINANCE_API_SECRET=seu_secret_key")
        return False
    
    if not binance_client_direct:
        print("❌ ERRO: Cliente Binance não disponível!")
        if not BINANCE_AVAILABLE:
            print("   Biblioteca python-binance não instalada")
        elif not api_key or not api_secret:
            print("   Credenciais não configuradas")
        return False
    
    try:
        # Valor mínimo da Binance em USD
        valor_usd = 10.0
        
        # Converte para reais (aproximado)
        usd_to_brl = get_usd_to_brl_rate()
        valor_brl = valor_usd * usd_to_brl
        
        print(f"\n💰 Valor a comprar: ${valor_usd:.2f} USD (≈ R$ {valor_brl:.2f})")
        
        # Obtém preço atual do Bitcoin
        print("\n📊 Obtendo preço atual do Bitcoin...")
        ticker = binance_client_direct.get_symbol_ticker(symbol="BTCUSDT")
        btc_price = float(ticker['price'])
        print(f"✅ Preço atual do BTC: ${btc_price:,.2f}")
        
        # Calcula quantidade de BTC
        quantidade_btc = valor_usd / btc_price
        
        print(f"\n📈 Quantidade de BTC a comprar: {quantidade_btc:.8f} BTC")
        
        # Verifica saldo disponível
        print("\n💼 Verificando saldo...")
        account = binance_client_direct.get_account()
        usdt_balance = float([b for b in account['balances'] if b['asset'] == 'USDT'][0]['free'])
        
        print(f"💰 Saldo USDT disponível: ${usdt_balance:,.2f}")
        
        if usdt_balance < valor_usd:
            print(f"\n⚠️ Saldo insuficiente!")
            print(f"   Necessário: ${valor_usd:.4f} USDT")
            print(f"   Disponível: ${usdt_balance:,.2f} USDT")
            print(f"\n💡 Você precisa depositar USDT na Binance primeiro.")
            print(f"   Deposite pelo menos ${valor_usd:.4f} USDT (≈ R$ {valor_brl:.2f})")
            return False
        
        # Confirmação
        print("\n" + "=" * 60)
        print("⚠️  ATENÇÃO: Esta é uma operação REAL!")
        print("=" * 60)
        print(f"Você está prestes a comprar:")
        print(f"  - Quantidade: {quantidade_btc:.8f} BTC")
        print(f"  - Valor: ${valor_usd:.4f} USDT (R$ {valor_brl:.2f})")
        print(f"  - Preço: ${btc_price:,.2f} por BTC")
        print("\nDeseja continuar? (digite 'SIM' para confirmar): ", end='')
        
        confirmacao = input().strip().upper()
        
        if confirmacao != 'SIM':
            print("❌ Operação cancelada pelo usuário")
            return False
        
        # Executa a compra
        print("\n🚀 Executando compra...")
        
        # A Binance requer quantidade mínima
        # Mínimo geralmente é $10 USD ou 0.00001 BTC
        # Para R$ 0,50 (≈ $0,10), vamos usar um valor maior ou avisar
        
        # Valor já está no mínimo ($10 USD)
        
        # Arredonda para 8 casas decimais (precisão da Binance)
        quantidade_btc_rounded = round(quantidade_btc, 8)
        
        # Verifica se tem saldo suficiente
        if usdt_balance < valor_usd:
            print(f"\n❌ Saldo insuficiente!")
            print(f"   Necessário: ${valor_usd:.2f} USDT")
            print(f"   Disponível: ${usdt_balance:,.2f} USDT")
            print(f"\n💡 Você precisa depositar USDT na Binance primeiro.")
            print(f"   Deposite pelo menos ${valor_usd:.2f} USDT (≈ R$ {valor_brl:.2f})")
            print(f"\n📝 Como depositar:")
            print(f"   1. Acesse https://www.binance.com")
            print(f"   2. Vá em 'Wallet' > 'Fiat and Spot'")
            print(f"   3. Clique em 'Deposit'")
            print(f"   4. Selecione USDT")
            print(f"   5. Siga as instruções para depositar")
            return False
        
        # Usa quoteOrderQty (valor em USDT) para melhor precisão
        try:
            order = binance_client_direct.order_market_buy(
                symbol="BTCUSDT",
                quoteOrderQty=valor_usd
            )
        except BinanceOrderException as e:
            print(f"\n❌ Erro na ordem: {e}")
            return False
        except BinanceAPIException as e:
            print(f"\n❌ Erro da API: {e}")
            return False
        
        if order:
            print("\n" + "=" * 60)
            print("✅ COMPRA EXECUTADA COM SUCESSO!")
            print("=" * 60)
            print(f"\n📋 Detalhes da Ordem:")
            print(f"   - ID: {order.get('orderId', 'N/A')}")
            print(f"   - Status: {order.get('status', 'N/A')}")
            executed_qty = float(order.get('executedQty', 0))
            cummulative_quote_qty = float(order.get('cummulativeQuoteQty', 0))
            print(f"   - Quantidade: {executed_qty:.8f} BTC")
            print(f"   - Valor: ${cummulative_quote_qty:.2f} USDT (R$ {valor_brl:.2f})")
            print(f"   - Preço médio: ${cummulative_quote_qty/executed_qty if executed_qty > 0 else 0:,.2f} por BTC")
            
            # Verifica saldo atualizado
            print("\n💼 Verificando saldo atualizado...")
            import time
            time.sleep(2)  # Aguarda atualização
            account_after = binance_client_direct.get_account()
            btc_balance_after = float([b for b in account_after['balances'] if b['asset'] == 'BTC'][0]['free'])
            usdt_balance_after = float([b for b in account_after['balances'] if b['asset'] == 'USDT'][0]['free'])
            print(f"   - BTC: {btc_balance_after:.8f}")
            print(f"   - USDT: ${usdt_balance_after:,.2f}")
            
            return True
        else:
            print("\n❌ Erro ao executar ordem de compra")
            return False
    
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import time
    
    success = buy_50_centavos()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
    else:
        print("\n❌ Teste falhou. Verifique os erros acima.")
    
    print("\n" + "=" * 60)

