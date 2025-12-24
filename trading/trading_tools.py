# -*- coding: utf-8 -*-
"""
Ferramentas de trading para o agente de investimento.
Wrapper functions para integração com o sistema de tools do OpenAI.
"""
import json
import logging
from typing import Dict, Optional

from trading.investment_agent import investment_agent

logger = logging.getLogger(__name__)


def analyze_bitcoin_market() -> str:
    """
    Analisa o mercado de Bitcoin e retorna recomendações de trading.
    
    Returns:
        String formatada com análise do mercado e recomendações
    """
    try:
        analysis = investment_agent.analyze_market()
        
        if 'error' in analysis:
            return f"❌ Erro na análise: {analysis['error']}"
        
        current_price = analysis.get('current_price', 0)
        balance = analysis.get('balance', {})
        recommendation = analysis.get('recommendation', {})
        combined_signal = analysis.get('combined_signal', {})
        
        result = f"""
📊 ANÁLISE DO MERCADO DE BITCOIN

💰 Preço Atual: ${current_price:,.2f}

💼 Portfólio:
   - BTC: {balance.get('btc', 0):.8f}
   - USDT: ${balance.get('usdt', 0):,.2f}

📈 Análise Técnica:
   - RSI (1h): {analysis.get('analysis_1h', {}).get('rsi', 0):.2f}
   - RSI (4h): {analysis.get('analysis_4h', {}).get('rsi', 0):.2f}
   - Sinal Combinado: {combined_signal.get('signal', 'HOLD')}
   - Confiança: {combined_signal.get('confidence', 0):.0%}

🎯 Recomendação:
   - Ação: {recommendation.get('action', 'HOLD')}
   - Motivo: {recommendation.get('reason', 'Aguardando sinal mais claro')}
   - Confiança: {recommendation.get('confidence', 0):.0%}
"""
        
        if recommendation.get('action') == 'BUY':
            result += f"""
   - Quantidade sugerida: {recommendation.get('quantity_btc', 0):.8f} BTC
   - Valor: ${recommendation.get('quantity_usd', 0):,.2f}
"""
        elif recommendation.get('action') == 'SELL':
            result += f"""
   - Quantidade sugerida: {recommendation.get('quantity_btc', 0):.8f} BTC
   - Valor: ${recommendation.get('quantity_usd', 0):,.2f}
   - Lucro: {recommendation.get('profit_percent', 0):.2f}%
"""
        
        return result.strip()
    
    except Exception as e:
        logger.error(f"❌ Erro ao analisar mercado: {e}")
        return f"❌ Erro ao analisar mercado: {str(e)}"


def get_bitcoin_price() -> str:
    """
    Obtém o preço atual do Bitcoin.
    
    Returns:
        String com preço atual formatado
    """
    try:
        price = investment_agent.binance.get_btc_price()
        if price is None:
            return "❌ Não foi possível obter o preço do Bitcoin"
        
        ticker_24h = investment_agent.binance.get_24h_ticker()
        
        result = f"💰 Preço atual do Bitcoin: ${price:,.2f}"
        
        if ticker_24h:
            change_24h = ticker_24h.get('priceChangePercent', 0)
            high_24h = ticker_24h.get('highPrice', 0)
            low_24h = ticker_24h.get('lowPrice', 0)
            
            result += f"\n\n📊 Últimas 24h:"
            result += f"\n   - Variação: {change_24h:+.2f}%"
            result += f"\n   - Máxima: ${high_24h:,.2f}"
            result += f"\n   - Mínima: ${low_24h:,.2f}"
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Erro ao obter preço: {e}")
        return f"❌ Erro ao obter preço: {str(e)}"


def get_portfolio_status() -> str:
    """
    Obtém status completo do portfólio.
    
    Returns:
        String formatada com informações do portfólio
    """
    try:
        status = investment_agent.get_portfolio_status()
        
        if 'error' in status:
            return f"❌ Erro ao obter status: {status['error']}"
        
        balance = status.get('balance', {})
        portfolio_value = status.get('portfolio_value', {})
        unrealized_pnl = status.get('unrealized_pnl', {})
        current_price = status.get('current_price', 0)
        
        result = f"""
💼 STATUS DO PORTFÓLIO

💰 Saldos:
   - Bitcoin: {balance.get('btc', 0):.8f} BTC
   - USDT: ${balance.get('usdt', 0):,.2f}

💵 Valor Total:
   - Valor em BTC: ${portfolio_value.get('btc_value_usd', 0):,.2f}
   - Saldo USDT: ${portfolio_value.get('usdt_balance', 0):,.2f}
   - TOTAL: ${portfolio_value.get('total_usd', 0):,.2f}

📊 Lucro/Prejuízo Não Realizado:
"""
        
        if unrealized_pnl.get('entry_price'):
            pnl_usd = unrealized_pnl.get('usd', 0)
            pnl_percent = unrealized_pnl.get('percent', 0)
            entry_price = unrealized_pnl.get('entry_price', 0)
            
            pnl_sign = "+" if pnl_usd >= 0 else ""
            result += f"""
   - Preço de entrada: ${entry_price:,.2f}
   - Preço atual: ${current_price:,.2f}
   - P&L: {pnl_sign}${pnl_usd:,.2f} ({pnl_sign}{pnl_percent:.2f}%)
"""
        else:
            result += "\n   - Nenhuma posição aberta"
        
        return result.strip()
    
    except Exception as e:
        logger.error(f"❌ Erro ao obter status do portfólio: {e}")
        return f"❌ Erro ao obter status: {str(e)}"


def buy_bitcoin(quantity: Optional[float] = None) -> str:
    """
    Compra Bitcoin seguindo a estratégia conservadora.
    
    Args:
        quantity: Quantidade de BTC a comprar (opcional, usa estratégia se não fornecido)
    
    Returns:
        String com resultado da operação
    """
    try:
        result = investment_agent.execute_buy(quantity)
        
        if 'error' in result:
            return f"❌ Erro na compra: {result['error']}"
        
        if result.get('success'):
            order = result.get('order', {})
            return f"""
✅ COMPRA EXECUTADA COM SUCESSO

📋 Detalhes da Ordem:
   - ID: {order.get('orderId', 'N/A')}
   - Quantidade: {result.get('quantity_btc', 0):.8f} BTC
   - Preço: ${result.get('price', 0):,.2f}
   - Total: ${result.get('total_usd', 0):,.2f}
   - Status: {order.get('status', 'FILLED')}
   - Data: {result.get('timestamp', 'N/A')}
"""
        else:
            return f"❌ Falha na compra: {result.get('error', 'Erro desconhecido')}"
    
    except Exception as e:
        logger.error(f"❌ Erro ao comprar Bitcoin: {e}")
        return f"❌ Erro ao comprar Bitcoin: {str(e)}"


def sell_bitcoin(quantity: Optional[float] = None) -> str:
    """
    Vende Bitcoin seguindo a estratégia conservadora.
    
    Args:
        quantity: Quantidade de BTC a vender (opcional, usa estratégia se não fornecido)
    
    Returns:
        String com resultado da operação
    """
    try:
        result = investment_agent.execute_sell(quantity)
        
        if 'error' in result:
            return f"❌ Erro na venda: {result['error']}"
        
        if result.get('success'):
            order = result.get('order', {})
            profit_percent = result.get('profit_percent', 0)
            entry_price = result.get('entry_price', 0)
            
            result_str = f"""
✅ VENDA EXECUTADA COM SUCESSO

📋 Detalhes da Ordem:
   - ID: {order.get('orderId', 'N/A')}
   - Quantidade: {result.get('quantity_btc', 0):.8f} BTC
   - Preço: ${result.get('price', 0):,.2f}
   - Total: ${result.get('total_usd', 0):,.2f}
   - Status: {order.get('status', 'FILLED')}
   - Data: {result.get('timestamp', 'N/A')}
"""
            
            if entry_price:
                result_str += f"""
📊 Performance:
   - Preço de entrada: ${entry_price:,.2f}
   - Preço de saída: ${result.get('price', 0):,.2f}
   - Lucro: {profit_percent:+.2f}%
"""
            
            return result_str.strip()
        else:
            return f"❌ Falha na venda: {result.get('error', 'Erro desconhecido')}"
    
    except Exception as e:
        logger.error(f"❌ Erro ao vender Bitcoin: {e}")
        return f"❌ Erro ao vender Bitcoin: {str(e)}"

