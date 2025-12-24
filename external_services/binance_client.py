# -*- coding: utf-8 -*-
"""
Cliente para integração com a API da Binance.
Fornece funcionalidades para análise de mercado e execução de trades.
"""
import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import time

try:
    from binance.client import Client
    from binance.exceptions import BinanceAPIException, BinanceOrderException
except ImportError:
    Client = None
    BinanceAPIException = Exception
    BinanceOrderException = Exception

# Configurações serão carregadas via os.getenv dentro da classe

logger = logging.getLogger(__name__)


class BinanceClient:
    """Cliente para interagir com a API da Binance."""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Inicializa o cliente Binance.
        
        Args:
            api_key: Chave da API Binance (opcional, usa env se não fornecido)
            api_secret: Secret da API Binance (opcional, usa env se não fornecido)
        """
        self.api_key = api_key or os.getenv('BINANCE_API_KEY', '')
        self.api_secret = api_secret or os.getenv('BINANCE_API_SECRET', '')
        
        if not self.api_key or not self.api_secret:
            logger.warning("⚠️ Credenciais da Binance não configuradas. Modo de teste ativado.")
            self.client = None
            self.test_mode = True
        else:
            try:
                self.client = Client(api_key=self.api_key, api_secret=self.api_secret)
                self.test_mode = False
                logger.info("✅ Cliente Binance inicializado com sucesso")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar cliente Binance: {e}")
                self.client = None
                self.test_mode = True
    
    def get_btc_price(self) -> Optional[float]:
        """
        Obtém o preço atual do Bitcoin em USDT.
        
        Returns:
            Preço atual do BTC em USDT ou None em caso de erro
        """
        try:
            if self.test_mode:
                # Retorna um preço simulado para testes
                return 45000.0
            
            ticker = self.client.get_symbol_ticker(symbol="BTCUSDT")
            price = float(ticker['price'])
            logger.info(f"📊 Preço atual do BTC: ${price:,.2f}")
            return price
        except Exception as e:
            logger.error(f"❌ Erro ao obter preço do BTC: {e}")
            return None
    
    def get_btc_balance(self) -> Dict[str, float]:
        """
        Obtém o saldo de BTC e USDT na conta.
        Retorna exatamente o que está na Binance, incluindo valores muito pequenos.
        
        Returns:
            Dicionário com 'btc' e 'usdt' ou None em caso de erro
        """
        try:
            if self.test_mode:
                return {'btc': 0.001, 'usdt': 1000.0}
            
            account = self.client.get_account()
            balances = {'btc': 0.0, 'usdt': 0.0}
            
            # Itera por todos os balances, mesmo que sejam zero ou muito pequenos
            for balance in account['balances']:
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                # Sempre atualiza, mesmo se for zero ou muito pequeno
                if asset == 'BTC':
                    balances['btc'] = total
                    logger.debug(f"💰 Saldo BTC: free={free:.8f}, locked={locked:.8f}, total={total:.8f}")
                elif asset == 'USDT':
                    balances['usdt'] = total
                    logger.debug(f"💰 Saldo USDT: free={free:.2f}, locked={locked:.2f}, total={total:.2f}")
            
            logger.info(f"📊 Saldos obtidos da Binance - BTC: {balances['btc']:.8f}, USDT: {balances['usdt']:.2f}")
            return balances
        except Exception as e:
            logger.error(f"❌ Erro ao obter saldo: {e}")
            return {'btc': 0.0, 'usdt': 0.0}
    
    def get_klines(self, symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 100) -> List[Dict]:
        """
        Obtém dados de candlestick (velas) para análise técnica.
        
        Args:
            symbol: Par de negociação (padrão: BTCUSDT)
            interval: Intervalo das velas (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Número de velas a retornar (máximo 1000)
        
        Returns:
            Lista de dicionários com dados das velas
        """
        try:
            if self.test_mode:
                # Retorna dados simulados
                return self._generate_mock_klines(limit)
            
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            
            formatted_klines = []
            for kline in klines:
                formatted_klines.append({
                    'timestamp': int(kline[0]),
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5]),
                    'close_time': int(kline[6]),
                    'quote_volume': float(kline[7]),
                    'trades': int(kline[8])
                })
            
            logger.info(f"📈 Obtidas {len(formatted_klines)} velas de {interval}")
            return formatted_klines
        except Exception as e:
            logger.error(f"❌ Erro ao obter klines: {e}")
            return []
    
    def get_24h_ticker(self, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """
        Obtém estatísticas de 24h do símbolo.
        
        Returns:
            Dicionário com estatísticas ou None em caso de erro
        """
        try:
            if self.test_mode:
                return {
                    'priceChange': -500.0,
                    'priceChangePercent': -1.1,
                    'highPrice': 46000.0,
                    'lowPrice': 44000.0,
                    'volume': 1000.0
                }
            
            ticker = self.client.get_ticker(symbol=symbol)
            return {
                'priceChange': float(ticker['priceChange']),
                'priceChangePercent': float(ticker['priceChangePercent']),
                'highPrice': float(ticker['highPrice']),
                'lowPrice': float(ticker['lowPrice']),
                'volume': float(ticker['volume'])
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter ticker 24h: {e}")
            return None
    
    def place_market_buy_order(self, quantity: float = None, quote_order_qty: float = None, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """
        Executa uma ordem de compra a mercado.
        
        Args:
            quantity: Quantidade de BTC a comprar (opcional)
            quote_order_qty: Valor em USDT a gastar (opcional, preferido para valores pequenos)
            symbol: Par de negociação (padrão: BTCUSDT)
        
        Returns:
            Dicionário com informações da ordem ou None em caso de erro
        """
        try:
            if self.test_mode:
                if quote_order_qty:
                    logger.info(f"🧪 [TESTE] Ordem de compra simulada: ${quote_order_qty:.2f} USDT")
                else:
                    logger.info(f"🧪 [TESTE] Ordem de compra simulada: {quantity} BTC")
                return {
                    'orderId': int(time.time()),
                    'status': 'FILLED',
                    'symbol': symbol,
                    'side': 'BUY',
                    'type': 'MARKET',
                    'executedQty': str(quantity) if quantity else '0',
                    'test': True
                }
            
            # Usa quoteOrderQty se fornecido (melhor para valores pequenos)
            if quote_order_qty:
                order = self.client.order_market_buy(
                    symbol=symbol,
                    quoteOrderQty=quote_order_qty
                )
            else:
                order = self.client.order_market_buy(
                    symbol=symbol,
                    quantity=quantity
                )
            
            logger.info(f"✅ Ordem de compra executada: {order['orderId']}")
            return order
        except BinanceOrderException as e:
            logger.error(f"❌ Erro na ordem de compra: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro inesperado na compra: {e}")
            return None
    
    def place_market_sell_order(self, quantity: float, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """
        Executa uma ordem de venda a mercado.
        
        Args:
            quantity: Quantidade de BTC a vender
            symbol: Par de negociação (padrão: BTCUSDT)
        
        Returns:
            Dicionário com informações da ordem ou None em caso de erro
        """
        try:
            if self.test_mode:
                logger.info(f"🧪 [TESTE] Ordem de venda simulada: {quantity} BTC")
                return {
                    'orderId': int(time.time()),
                    'status': 'FILLED',
                    'symbol': symbol,
                    'side': 'SELL',
                    'type': 'MARKET',
                    'executedQty': str(quantity),
                    'test': True
                }
            
            order = self.client.order_market_sell(symbol=symbol, quantity=quantity)
            logger.info(f"✅ Ordem de venda executada: {order['orderId']}")
            return order
        except BinanceOrderException as e:
            logger.error(f"❌ Erro na ordem de venda: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro inesperado na venda: {e}")
            return None
    
    def _generate_mock_klines(self, limit: int) -> List[Dict]:
        """Gera dados de klines simulados para testes."""
        base_price = 45000.0
        klines = []
        current_time = int(time.time() * 1000) - (limit * 3600000)  # 1 hora atrás
        
        for i in range(limit):
            # Simula variação de preço
            price_variation = (i % 10 - 5) * 100
            open_price = base_price + price_variation
            high_price = open_price + 200
            low_price = open_price - 200
            close_price = open_price + (price_variation * 0.5)
            
            klines.append({
                'timestamp': current_time + (i * 3600000),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': 100.0 + (i % 50),
                'close_time': current_time + (i * 3600000) + 3600000,
                'quote_volume': (open_price + close_price) / 2 * (100.0 + (i % 50)),
                'trades': 100 + i
            })
        
        return klines


# Instância global do cliente
binance_client = BinanceClient()

