# -*- coding: utf-8 -*-
"""
Estratégia conservadora de trading para Bitcoin.
Foca em preservar capital e fazer trades apenas em momentos favoráveis.
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TradingSignal(Enum):
    """Sinais de trading."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    SELL_PARTIAL = "SELL_PARTIAL"


class ConservativeStrategy:
    """
    Estratégia conservadora de trading que prioriza:
    1. Preservação de capital
    2. Compras apenas em momentos de baixa (dips)
    3. Vendas apenas quando há lucro garantido
    4. Stop loss automático
    5. Take profit parcial
    """
    
    def __init__(
        self,
        max_position_size: float = 0.1,  # Máximo 10% do capital por trade
        stop_loss_percent: float = 2.0,   # Stop loss de 2%
        take_profit_percent: float = 5.0,  # Take profit de 5%
        rsi_oversold: float = 30.0,        # RSI oversold
        rsi_overbought: float = 70.0,       # RSI overbought
        min_profit_to_sell: float = 3.0    # Mínimo 3% de lucro para vender
    ):
        """
        Inicializa a estratégia conservadora.
        
        Args:
            max_position_size: Tamanho máximo da posição (fração do capital)
            stop_loss_percent: Percentual de stop loss
            take_profit_percent: Percentual de take profit
            rsi_oversold: Limite inferior do RSI para compra
            rsi_overbought: Limite superior do RSI para venda
            min_profit_to_sell: Lucro mínimo necessário para vender
        """
        self.max_position_size = max_position_size
        self.stop_loss_percent = stop_loss_percent
        self.take_profit_percent = take_profit_percent
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.min_profit_to_sell = min_profit_to_sell
        
        # Histórico de trades
        self.entry_prices: List[float] = []
        self.current_positions: List[Dict] = []
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        Calcula o RSI (Relative Strength Index).
        
        Args:
            prices: Lista de preços de fechamento
            period: Período para cálculo (padrão: 14)
        
        Returns:
            Valor do RSI (0-100)
        """
        if len(prices) < period + 1:
            return 50.0  # RSI neutro se não houver dados suficientes
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_moving_averages(self, prices: List[float]) -> Dict[str, float]:
        """
        Calcula médias móveis simples (SMA).
        
        Args:
            prices: Lista de preços de fechamento
        
        Returns:
            Dicionário com SMA20, SMA50, SMA200
        """
        sma20 = sum(prices[-20:]) / min(20, len(prices)) if prices else 0
        sma50 = sum(prices[-50:]) / min(50, len(prices)) if prices else 0
        sma200 = sum(prices[-200:]) / min(200, len(prices)) if prices else 0
        
        return {
            'sma20': sma20,
            'sma50': sma50,
            'sma200': sma200
        }
    
    def calculate_support_resistance(self, klines: List[Dict]) -> Dict[str, float]:
        """
        Identifica níveis de suporte e resistência.
        
        Args:
            klines: Lista de velas (candlesticks)
        
        Returns:
            Dicionário com suporte e resistência
        """
        if not klines:
            return {'support': 0, 'resistance': 0}
        
        lows = [k['low'] for k in klines]
        highs = [k['high'] for k in klines]
        
        # Suporte: média dos 3 menores valores
        support = sum(sorted(lows)[:3]) / min(3, len(lows))
        
        # Resistência: média dos 3 maiores valores
        resistance = sum(sorted(highs)[-3:]) / min(3, len(highs))
        
        return {
            'support': support,
            'resistance': resistance
        }
    
    def analyze_market(self, klines: List[Dict], current_price: float) -> Dict:
        """
        Analisa o mercado e retorna indicadores técnicos.
        
        Args:
            klines: Lista de velas
            current_price: Preço atual do BTC
        
        Returns:
            Dicionário com análise completa do mercado
        """
        if not klines:
            return {
                'rsi': 50.0,
                'signal': TradingSignal.HOLD,
                'confidence': 0.0,
                'indicators': {}
            }
        
        closes = [k['close'] for k in klines]
        
        # Calcula indicadores
        rsi = self.calculate_rsi(closes)
        mas = self.calculate_moving_averages(closes)
        sr = self.calculate_support_resistance(klines)
        
        # Análise de tendência
        price_vs_sma20 = (current_price - mas['sma20']) / mas['sma20'] * 100
        price_vs_sma50 = (current_price - mas['sma50']) / mas['sma50'] * 100
        
        # Determina sinal
        signal = TradingSignal.HOLD
        confidence = 0.5
        
        # Condições para COMPRA (conservadora)
        buy_conditions = [
            rsi < self.rsi_oversold,  # RSI oversold
            current_price < mas['sma20'],  # Preço abaixo da média de curto prazo
            current_price > sr['support'] * 0.98,  # Próximo ao suporte
            price_vs_sma50 < -2.0  # Pelo menos 2% abaixo da média de médio prazo
        ]
        
        # Condições para VENDA (conservadora)
        sell_conditions = [
            rsi > self.rsi_overbought,  # RSI overbought
            current_price > mas['sma20'],  # Preço acima da média de curto prazo
            current_price < sr['resistance'] * 1.02,  # Próximo à resistência
            price_vs_sma50 > 2.0  # Pelo menos 2% acima da média de médio prazo
        ]
        
        buy_score = sum(buy_conditions)
        sell_score = sum(sell_conditions)
        
        if buy_score >= 3:
            signal = TradingSignal.BUY
            confidence = min(0.9, 0.5 + (buy_score * 0.1))
        elif sell_score >= 3:
            signal = TradingSignal.SELL
            confidence = min(0.9, 0.5 + (sell_score * 0.1))
        
        return {
            'rsi': rsi,
            'signal': signal,
            'confidence': confidence,
            'indicators': {
                'moving_averages': mas,
                'support_resistance': sr,
                'price_vs_sma20': price_vs_sma20,
                'price_vs_sma50': price_vs_sma50,
                'current_price': current_price
            }
        }
    
    def should_buy(
        self,
        market_analysis: Dict,
        current_balance: Dict[str, float],
        current_price: float
    ) -> Tuple[bool, float]:
        """
        Decide se deve comprar e quanto comprar.
        
        Args:
            market_analysis: Análise do mercado
            current_balance: Saldo atual (btc, usdt)
            current_price: Preço atual do BTC
        
        Returns:
            Tupla (deve_comprar, quantidade_em_btc)
        """
        if market_analysis['signal'] != TradingSignal.BUY:
            return False, 0.0
        
        if market_analysis['confidence'] < 0.6:
            return False, 0.0
        
        # Verifica se há capital disponível
        available_usdt = current_balance.get('usdt', 0.0)
        if available_usdt < 100:  # Mínimo de $100 para comprar
            logger.info("💰 Capital insuficiente para compra")
            return False, 0.0
        
        # Calcula quantidade baseada no max_position_size
        max_investment = available_usdt * self.max_position_size
        quantity_btc = max_investment / current_price
        
        # Ajusta para o mínimo de 0.0001 BTC (precisão da Binance)
        if quantity_btc < 0.0001:
            return False, 0.0
        
        logger.info(f"✅ Sinal de COMPRA: {quantity_btc:.8f} BTC (${max_investment:.2f})")
        return True, quantity_btc
    
    def should_sell(
        self,
        market_analysis: Dict,
        current_balance: Dict[str, float],
        current_price: float,
        entry_price: Optional[float] = None
    ) -> Tuple[bool, float]:
        """
        Decide se deve vender e quanto vender.
        
        Args:
            market_analysis: Análise do mercado
            current_balance: Saldo atual (btc, usdt)
            current_price: Preço atual do BTC
            entry_price: Preço de entrada (para calcular lucro)
        
        Returns:
            Tupla (deve_vender, quantidade_em_btc)
        """
        btc_balance = current_balance.get('btc', 0.0)
        
        if btc_balance < 0.0001:  # Mínimo para vender
            return False, 0.0
        
        # Se não há preço de entrada, usa análise técnica
        if entry_price is None:
            if market_analysis['signal'] == TradingSignal.SELL:
                # Vende parcialmente (50%)
                sell_quantity = btc_balance * 0.5
                logger.info(f"✅ Sinal de VENDA (técnico): {sell_quantity:.8f} BTC")
                return True, sell_quantity
            return False, 0.0
        
        # Calcula lucro/prejuízo
        profit_percent = ((current_price - entry_price) / entry_price) * 100
        
        # Vende se houver lucro mínimo OU stop loss
        if profit_percent >= self.min_profit_to_sell:
            # Take profit: vende 50% se lucro >= 5%, 100% se >= 10%
            if profit_percent >= 10.0:
                sell_quantity = btc_balance
            elif profit_percent >= self.take_profit_percent:
                sell_quantity = btc_balance * 0.5
            else:
                sell_quantity = btc_balance * 0.25
            
            logger.info(f"✅ Take profit: vendendo {sell_quantity:.8f} BTC (lucro: {profit_percent:.2f}%)")
            return True, sell_quantity
        
        elif profit_percent <= -self.stop_loss_percent:
            # Stop loss: vende tudo
            logger.warning(f"⚠️ Stop loss: vendendo {btc_balance:.8f} BTC (prejuízo: {profit_percent:.2f}%)")
            return True, btc_balance
        
        # Vende se sinal técnico for forte
        if market_analysis['signal'] == TradingSignal.SELL and market_analysis['confidence'] > 0.7:
            sell_quantity = btc_balance * 0.5
            logger.info(f"✅ Venda técnica: {sell_quantity:.8f} BTC")
            return True, sell_quantity
        
        return False, 0.0
    
    def get_strategy_summary(self) -> Dict:
        """Retorna resumo da estratégia."""
        return {
            'max_position_size': self.max_position_size,
            'stop_loss_percent': self.stop_loss_percent,
            'take_profit_percent': self.take_profit_percent,
            'rsi_oversold': self.rsi_oversold,
            'rsi_overbought': self.rsi_overbought,
            'min_profit_to_sell': self.min_profit_to_sell,
            'strategy_type': 'CONSERVADORA'
        }
