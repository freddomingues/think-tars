# -*- coding: utf-8 -*-
"""
Agente de Análise de Investimento em Bitcoin.
Combina análise técnica, estratégia conservadora e execução de trades.
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

from external_services.binance_client import binance_client
from trading.strategy import ConservativeStrategy, TradingSignal

logger = logging.getLogger(__name__)


class InvestmentAgent:
    """
    Agente de investimento que analisa o mercado de Bitcoin e executa trades
    seguindo uma estratégia conservadora.
    """
    
    def __init__(self):
        """Inicializa o agente de investimento."""
        self.binance = binance_client
        self.strategy = ConservativeStrategy()
        self.entry_prices: Dict[str, float] = {}  # Preços de entrada por trade
    
    def get_market_status(self) -> Dict:
        """
        Obtém status completo do mercado.
        
        Returns:
            Dicionário com informações do mercado
        """
        try:
            current_price = self.binance.get_btc_price()
            if current_price is None:
                return {'error': 'Não foi possível obter preço do BTC'}
            
            balance = self.binance.get_btc_balance()
            ticker_24h = self.binance.get_24h_ticker()
            klines_1h = self.binance.get_klines(interval="1h", limit=100)
            klines_4h = self.binance.get_klines(interval="4h", limit=50)
            
            return {
                'current_price': current_price,
                'balance': balance,
                'ticker_24h': ticker_24h,
                'klines_1h_count': len(klines_1h),
                'klines_4h_count': len(klines_4h),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter status do mercado: {e}")
            return {'error': str(e)}
    
    def analyze_market(self) -> Dict:
        """
        Realiza análise completa do mercado.
        
        Returns:
            Dicionário com análise detalhada
        """
        try:
            current_price = self.binance.get_btc_price()
            if current_price is None:
                return {'error': 'Não foi possível obter preço do BTC'}
            
            # Obtém dados históricos
            klines_1h = self.binance.get_klines(interval="1h", limit=100)
            klines_4h = self.binance.get_klines(interval="4h", limit=50)
            
            if not klines_1h:
                return {'error': 'Não foi possível obter dados históricos'}
            
            # Análise de curto prazo (1h)
            analysis_1h = self.strategy.analyze_market(klines_1h, current_price)
            
            # Análise de médio prazo (4h)
            analysis_4h = self.strategy.analyze_market(klines_4h, current_price)
            
            # Combina análises
            combined_signal = self._combine_signals(analysis_1h, analysis_4h)
            
            balance = self.binance.get_btc_balance()
            
            return {
                'current_price': current_price,
                'balance': balance,
                'analysis_1h': {
                    'rsi': analysis_1h['rsi'],
                    'signal': analysis_1h['signal'].value,
                    'confidence': analysis_1h['confidence'],
                    'indicators': analysis_1h['indicators']
                },
                'analysis_4h': {
                    'rsi': analysis_4h['rsi'],
                    'signal': analysis_4h['signal'].value,
                    'confidence': analysis_4h['confidence'],
                    'indicators': analysis_4h['indicators']
                },
                'combined_signal': combined_signal,
                'recommendation': self._get_recommendation(combined_signal, balance, current_price),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Erro na análise do mercado: {e}")
            return {'error': str(e)}
    
    def _combine_signals(self, analysis_1h: Dict, analysis_4h: Dict) -> Dict:
        """Combina sinais de diferentes timeframes."""
        signal_1h = analysis_1h['signal']
        signal_4h = analysis_4h['signal']
        confidence_1h = analysis_1h['confidence']
        confidence_4h = analysis_4h['confidence']
        
        # Se ambos concordam, aumenta confiança
        if signal_1h == signal_4h:
            combined_confidence = (confidence_1h + confidence_4h) / 2
            if combined_confidence > 0.7:
                return {
                    'signal': signal_1h.value,
                    'confidence': min(0.95, combined_confidence + 0.1),
                    'timeframe_agreement': True
                }
        
        # Prioriza sinal de maior confiança
        if confidence_1h > confidence_4h:
            return {
                'signal': signal_1h.value,
                'confidence': confidence_1h,
                'timeframe_agreement': False
            }
        else:
            return {
                'signal': signal_4h.value,
                'confidence': confidence_4h,
                'timeframe_agreement': False
            }
    
    def _get_recommendation(
        self,
        combined_signal: Dict,
        balance: Dict[str, float],
        current_price: float
    ) -> Dict:
        """Gera recomendação de ação baseada na análise."""
        signal = combined_signal['signal']
        confidence = combined_signal['confidence']
        
        recommendation = {
            'action': 'HOLD',
            'reason': 'Aguardando sinal mais claro',
            'confidence': confidence
        }
        
        if signal == 'BUY' and confidence > 0.6:
            should_buy, quantity = self.strategy.should_buy(
                {'signal': TradingSignal.BUY, 'confidence': confidence},
                balance,
                current_price
            )
            
            if should_buy:
                recommendation = {
                    'action': 'BUY',
                    'quantity_btc': quantity,
                    'quantity_usd': quantity * current_price,
                    'reason': f'RSI oversold, preço próximo ao suporte, confiança: {confidence:.0%}',
                    'confidence': confidence
                }
        
        elif signal == 'SELL' and confidence > 0.6:
            entry_price = self.entry_prices.get('last_entry', current_price)
            should_sell, quantity = self.strategy.should_sell(
                {'signal': TradingSignal.SELL, 'confidence': confidence},
                balance,
                current_price,
                entry_price
            )
            
            if should_sell:
                profit_percent = ((current_price - entry_price) / entry_price) * 100 if entry_price else 0
                recommendation = {
                    'action': 'SELL',
                    'quantity_btc': quantity,
                    'quantity_usd': quantity * current_price,
                    'profit_percent': profit_percent,
                    'reason': f'RSI overbought ou take profit atingido, confiança: {confidence:.0%}',
                    'confidence': confidence
                }
        
        return recommendation
    
    def execute_buy(self, quantity: Optional[float] = None) -> Dict:
        """
        Executa uma compra de Bitcoin.
        
        Args:
            quantity: Quantidade de BTC a comprar (opcional, usa estratégia se não fornecido)
        
        Returns:
            Dicionário com resultado da operação
        """
        try:
            current_price = self.binance.get_btc_price()
            balance = self.binance.get_btc_balance()
            
            if quantity is None:
                # Usa estratégia para determinar quantidade
                analysis = self.analyze_market()
                if 'error' in analysis:
                    return {'error': analysis['error']}
                
                recommendation = analysis.get('recommendation', {})
                if recommendation.get('action') != 'BUY':
                    return {
                        'error': 'Não é um bom momento para comprar segundo a estratégia',
                        'analysis': analysis
                    }
                
                quantity = recommendation.get('quantity_btc', 0)
            
            if quantity <= 0:
                return {'error': 'Quantidade inválida'}
            
            # Executa ordem
            order = self.binance.place_market_buy_order(quantity)
            
            if order:
                # Registra preço de entrada
                self.entry_prices['last_entry'] = current_price
                self.entry_prices[order.get('orderId', 'unknown')] = current_price
                
                return {
                    'success': True,
                    'order': order,
                    'quantity_btc': quantity,
                    'price': current_price,
                    'total_usd': quantity * current_price,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'error': 'Falha ao executar ordem de compra'}
        
        except Exception as e:
            logger.error(f"❌ Erro ao executar compra: {e}")
            return {'error': str(e)}
    
    def execute_sell(self, quantity: Optional[float] = None) -> Dict:
        """
        Executa uma venda de Bitcoin.
        
        Args:
            quantity: Quantidade de BTC a vender (opcional, usa estratégia se não fornecido)
        
        Returns:
            Dicionário com resultado da operação
        """
        try:
            current_price = self.binance.get_btc_price()
            balance = self.binance.get_btc_balance()
            
            if balance.get('btc', 0) < 0.0001:
                return {'error': 'Saldo de BTC insuficiente'}
            
            if quantity is None:
                # Usa estratégia para determinar quantidade
                analysis = self.analyze_market()
                if 'error' in analysis:
                    return {'error': analysis['error']}
                
                recommendation = analysis.get('recommendation', {})
                if recommendation.get('action') != 'SELL':
                    return {
                        'error': 'Não é um bom momento para vender segundo a estratégia',
                        'analysis': analysis
                    }
                
                quantity = recommendation.get('quantity_btc', 0)
            
            if quantity <= 0 or quantity > balance.get('btc', 0):
                return {'error': 'Quantidade inválida ou maior que o saldo'}
            
            # Executa ordem
            order = self.binance.place_market_sell_order(quantity)
            
            if order:
                # Calcula lucro se houver preço de entrada
                entry_price = self.entry_prices.get('last_entry', current_price)
                profit_percent = ((current_price - entry_price) / entry_price) * 100 if entry_price else 0
                
                return {
                    'success': True,
                    'order': order,
                    'quantity_btc': quantity,
                    'price': current_price,
                    'total_usd': quantity * current_price,
                    'entry_price': entry_price,
                    'profit_percent': profit_percent,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'error': 'Falha ao executar ordem de venda'}
        
        except Exception as e:
            logger.error(f"❌ Erro ao executar venda: {e}")
            return {'error': str(e)}
    
    def get_portfolio_status(self) -> Dict:
        """
        Obtém status completo do portfólio.
        
        Returns:
            Dicionário com informações do portfólio
        """
        try:
            balance = self.binance.get_btc_balance()
            current_price = self.binance.get_btc_price()
            
            if current_price is None:
                return {'error': 'Não foi possível obter preço do BTC'}
            
            btc_value = balance.get('btc', 0) * current_price
            total_value = btc_value + balance.get('usdt', 0)
            
            # Calcula lucro/prejuízo se houver entrada
            entry_price = self.entry_prices.get('last_entry')
            unrealized_pnl = 0.0
            unrealized_pnl_percent = 0.0
            
            if entry_price and balance.get('btc', 0) > 0:
                unrealized_pnl = (current_price - entry_price) * balance.get('btc', 0)
                unrealized_pnl_percent = ((current_price - entry_price) / entry_price) * 100
            
            return {
                'balance': balance,
                'current_price': current_price,
                'portfolio_value': {
                    'btc_value_usd': btc_value,
                    'usdt_balance': balance.get('usdt', 0),
                    'total_usd': total_value
                },
                'unrealized_pnl': {
                    'usd': unrealized_pnl,
                    'percent': unrealized_pnl_percent,
                    'entry_price': entry_price
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter status do portfólio: {e}")
            return {'error': str(e)}


# Instância global do agente
investment_agent = InvestmentAgent()

