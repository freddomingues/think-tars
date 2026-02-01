# -*- coding: utf-8 -*-
"""
Ferramentas de trading para o agente de investimento.
Wrapper functions para integração com o sistema de tools do OpenAI.
"""
import json
import logging
from typing import Dict, Optional

from ai.trading.investment_agent import investment_agent

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
        recommendation = analysis.get('recommendation', {})
        combined_signal = analysis.get('combined_signal', {})
        
        result = f"""
📊 ANÁLISE DO MERCADO DE BITCOIN

💰 Preço Atual: ${current_price:,.2f}

📈 Análise Técnica:
   - RSI (1h): {analysis.get('analysis_1h', {}).get('rsi', 0):.2f}
   - RSI (4h): {analysis.get('analysis_4h', {}).get('rsi', 0):.2f}
   - Sinal Combinado: {combined_signal.get('signal', 'HOLD')}
   - Confiança: {combined_signal.get('confidence', 0):.0%}

🎯 Recomendação de Mercado:
   - Tendência: {recommendation.get('action', 'HOLD')}
   - Motivo: {recommendation.get('reason', 'Aguardando sinal mais claro')}
   - Confiança: {recommendation.get('confidence', 0):.0%}

⚠️ NOTA: Esta é apenas uma análise de mercado. Operações de compra e venda não estão disponíveis nesta versão.
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
    Função desabilitada por segurança - não exibe informações de carteira.
    
    Returns:
        Mensagem informando que a funcionalidade não está disponível
    """
    return "⚠️ Esta funcionalidade não está disponível por questões de segurança. Informações de carteira não são exibidas."


def buy_bitcoin(quantity: Optional[float] = None) -> str:
    """
    Função desabilitada por segurança - operações de compra não estão disponíveis.
    
    Args:
        quantity: Quantidade de BTC a comprar (ignorado)
    
    Returns:
        Mensagem informando que a funcionalidade não está disponível
    """
    return "⚠️ Operações de compra não estão disponíveis por questões de segurança. Esta é uma versão de demonstração que fornece apenas análise de mercado."


def sell_bitcoin(quantity: Optional[float] = None) -> str:
    """
    Função desabilitada por segurança - operações de venda não estão disponíveis.
    
    Args:
        quantity: Quantidade de BTC a vender (ignorado)
    
    Returns:
        Mensagem informando que a funcionalidade não está disponível
    """
    return "⚠️ Operações de venda não estão disponíveis por questões de segurança. Esta é uma versão de demonstração que fornece apenas análise de mercado."

