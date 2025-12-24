# -*- coding: utf-8 -*-
"""
Trading Automático - Executa análise de mercado e trades automaticamente.
Este script pode ser executado via cron para operar automaticamente.
"""
import sys
import os
import logging
from datetime import datetime
from typing import Dict, Optional

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading.investment_agent import investment_agent
from trading.email_notifier import email_notifier
from config.settings import OPENAI_API_KEY

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading/auto_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoTrader:
    """
    Classe para executar trading automático baseado em análise técnica.
    """
    
    def __init__(self, auto_execute: bool = True):
        """
        Inicializa o auto trader.
        
        Args:
            auto_execute: Se True, executa trades automaticamente. Se False, apenas analisa.
        """
        self.auto_execute = auto_execute
        self.agent = investment_agent
        logger.info(f"🤖 AutoTrader inicializado (auto_execute={auto_execute})")
    
    def run_analysis(self) -> Dict:
        """
        Executa análise completa do mercado.
        
        Returns:
            Dicionário com resultado da análise
        """
        try:
            logger.info("📊 Iniciando análise do mercado...")
            
            # Obtém status do portfólio
            portfolio_status = self.agent.get_portfolio_status()
            if 'error' in portfolio_status:
                logger.error(f"❌ Erro ao obter status do portfólio: {portfolio_status['error']}")
                return {'success': False, 'error': portfolio_status['error']}
            
            # Analisa mercado
            market_analysis = self.agent.analyze_market()
            if 'error' in market_analysis:
                logger.error(f"❌ Erro na análise do mercado: {market_analysis['error']}")
                return {'success': False, 'error': market_analysis['error']}
            
            recommendation = market_analysis.get('recommendation', {})
            action = recommendation.get('action', 'HOLD')
            confidence = recommendation.get('confidence', 0.0)
            
            logger.info(f"📈 Análise concluída:")
            logger.info(f"   - Ação recomendada: {action}")
            logger.info(f"   - Confiança: {confidence:.0%}")
            logger.info(f"   - Preço atual: ${market_analysis.get('current_price', 0):,.2f}")
            
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'portfolio_status': portfolio_status,
                'market_analysis': market_analysis,
                'recommendation': recommendation,
                'action_taken': None
            }
            
            # Executa ação se recomendado e confiança suficiente
            if action != 'HOLD' and confidence >= 0.6:
                if self.auto_execute:
                    action_result = self._execute_action(action, recommendation, portfolio_status)
                    result['action_taken'] = action_result
                    
                    # Envia email sobre a ação executada
                    if action_result.get('success'):
                        self._send_action_email(action_result, market_analysis, portfolio_status)
                else:
                    logger.info(f"⚠️ Modo de análise apenas - ação {action} não executada")
                    result['action_taken'] = {'mode': 'analysis_only', 'action': action}
            else:
                logger.info(f"⏸️ Aguardando - ação: {action}, confiança: {confidence:.0%}")
                result['action_taken'] = {'action': 'HOLD', 'reason': 'Confiança insuficiente ou sem sinal claro'}
            
            # Sempre envia email com análise (mesmo que não tenha ação)
            self._send_analysis_email(result)
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Erro durante análise: {e}", exc_info=True)
            error_result = {'success': False, 'error': str(e)}
            
            # Envia email de erro
            email_notifier.send_notification('error', {
                'error': str(e),
                'details': 'Erro durante análise do mercado',
                'timestamp': datetime.now().isoformat()
            })
            
            return error_result
    
    def _execute_action(self, action: str, recommendation: Dict, portfolio_status: Dict) -> Dict:
        """
        Executa a ação recomendada.
        
        Args:
            action: Ação a executar (BUY ou SELL)
            recommendation: Recomendação completa
            portfolio_status: Status do portfólio
        
        Returns:
            Dicionário com resultado da execução
        """
        try:
            if action == 'BUY':
                logger.info("💰 Executando COMPRA...")
                result = self.agent.execute_buy()
                
                if result.get('success'):
                    logger.info(f"✅ Compra executada com sucesso!")
                    logger.info(f"   - Quantidade: {result.get('quantity_btc', 0):.8f} BTC")
                    logger.info(f"   - Valor: ${result.get('total_usd', 0):,.2f}")
                    return {
                        'success': True,
                        'action': 'BUY',
                        'result': result
                    }
                else:
                    error_msg = result.get('error', 'Erro desconhecido')
                    logger.warning(f"⚠️ Compra não executada: {error_msg}")
                    return {
                        'success': False,
                        'action': 'BUY',
                        'error': error_msg
                    }
            
            elif action == 'SELL':
                logger.info("💸 Executando VENDA...")
                result = self.agent.execute_sell()
                
                if result.get('success'):
                    logger.info(f"✅ Venda executada com sucesso!")
                    logger.info(f"   - Quantidade: {result.get('quantity_btc', 0):.8f} BTC")
                    logger.info(f"   - Valor: ${result.get('total_usd', 0):,.2f}")
                    if result.get('profit_percent'):
                        logger.info(f"   - Lucro: {result.get('profit_percent', 0):+.2f}%")
                    return {
                        'success': True,
                        'action': 'SELL',
                        'result': result
                    }
                else:
                    error_msg = result.get('error', 'Erro desconhecido')
                    logger.warning(f"⚠️ Venda não executada: {error_msg}")
                    return {
                        'success': False,
                        'action': 'SELL',
                        'error': error_msg
                    }
            
            else:
                logger.info(f"⏸️ Nenhuma ação executada: {action}")
                return {
                    'success': True,
                    'action': 'HOLD',
                    'reason': 'Nenhuma ação recomendada'
                }
        
        except Exception as e:
            logger.error(f"❌ Erro ao executar ação {action}: {e}", exc_info=True)
            error_result = {
                'success': False,
                'action': action,
                'error': str(e)
            }
            
            # Envia email de erro
            email_notifier.send_notification('error', {
                'error': str(e),
                'details': f'Erro ao executar {action}',
                'timestamp': datetime.now().isoformat()
            })
            
            return error_result
    
    def _send_analysis_email(self, analysis_result: Dict):
        """Envia email com análise do mercado e resumo completo."""
        try:
            market = analysis_result.get('market_analysis', {})
            recommendation = analysis_result.get('recommendation', {})
            action_taken = analysis_result.get('action_taken', {})
            
            # SEMPRE obtém dados ATUALIZADOS diretamente da Binance no momento de enviar email
            # Não usa valores em cache ou da análise anterior
            logger.info("📧 Obtendo dados atualizados da Binance para email...")
            
            # Importa diretamente para garantir que usa a instância mais recente
            from external_services.binance_client import binance_client
            
            # Verifica se está em modo de teste
            if binance_client.test_mode:
                logger.warning("⚠️ Cliente Binance em modo de teste! Verifique as credenciais.")
            
            # Busca saldos atualizados diretamente da instância global
            balance_fresh = binance_client.get_btc_balance()
            if balance_fresh is None:
                logger.error("❌ Não foi possível obter saldos da Binance para email")
                balance_fresh = {'btc': 0.0, 'usdt': 0.0}
            
            # Busca preço atualizado diretamente da instância global
            current_price_fresh = binance_client.get_btc_price()
            if current_price_fresh is None:
                logger.error("❌ Não foi possível obter preço atualizado, usando da análise")
                current_price_fresh = market.get('current_price', 0)
            
            # Calcula valores atualizados
            btc_balance = balance_fresh.get('btc', 0.0)
            usdt_balance = balance_fresh.get('usdt', 0.0)
            btc_value = btc_balance * current_price_fresh
            total_value = btc_value + usdt_balance
            
            logger.info(f"📊 Dados atualizados para email:")
            logger.info(f"   - Preço BTC: ${current_price_fresh:,.2f}")
            logger.info(f"   - Saldo BTC: {btc_balance:.8f}")
            logger.info(f"   - Saldo USDT: ${usdt_balance:,.2f}")
            logger.info(f"   - Valor Total: ${total_value:,.2f}")
            
            # Obtém P&L não realizado se houver
            portfolio_after = self.agent.get_portfolio_status()
            unrealized_pnl = portfolio_after.get('unrealized_pnl', {}) if 'error' not in portfolio_after else {}
            
            email_data = {
                'timestamp': datetime.now().isoformat(),
                'current_price': current_price_fresh,  # Preço atualizado
                'rsi_1h': market.get('analysis_1h', {}).get('rsi', 0),
                'rsi_4h': market.get('analysis_4h', {}).get('rsi', 0),
                'btc_balance': btc_balance,  # Saldo atualizado
                'usdt_balance': usdt_balance,  # Saldo atualizado
                'total_value': total_value,  # Valor total atualizado
                'recommendation': recommendation,
                'action_taken': action_taken,
                'unrealized_pnl': unrealized_pnl
            }
            
            # Define assunto baseado na ação
            if action_taken.get('success') and action_taken.get('action') in ['BUY', 'SELL']:
                subject = f"🤖 Trading Automático - {action_taken.get('action')} Executada"
            else:
                subject = "🤖 Trading Automático - Análise de Mercado"
            
            email_notifier.send_notification('analysis', email_data, subject_override=subject)
            logger.info(f"📧 Email enviado com resumo completo")
        except Exception as e:
            logger.error(f"❌ Erro ao enviar email de análise: {e}")
    
    def _send_action_email(self, action_result: Dict, market_analysis: Dict, portfolio_status: Dict):
        """Envia email sobre ação executada (compra/venda)."""
        try:
            action = action_result.get('action')
            result = action_result.get('result', {})
            order = result.get('order', {})
            
            portfolio_value = portfolio_status.get('portfolio_value', {})
            balance = portfolio_status.get('balance', {})
            
            if action == 'BUY':
                email_data = {
                    'timestamp': datetime.now().isoformat(),
                    'order': order,
                    'quantity_btc': result.get('quantity_btc', 0),
                    'value_usd': result.get('total_usd', 0),
                    'price': result.get('price', 0),
                    'btc_balance_after': balance.get('btc', 0),
                    'usdt_balance_after': balance.get('usdt', 0),
                    'total_value_after': portfolio_value.get('total_usd', 0)
                }
                email_notifier.send_notification('buy', email_data)
            
            elif action == 'SELL':
                email_data = {
                    'timestamp': datetime.now().isoformat(),
                    'order': order,
                    'quantity_btc': result.get('quantity_btc', 0),
                    'value_usd': result.get('total_usd', 0),
                    'price': result.get('price', 0),
                    'entry_price': result.get('entry_price', 0),
                    'profit_percent': result.get('profit_percent', 0),
                    'btc_balance_after': balance.get('btc', 0),
                    'usdt_balance_after': balance.get('usdt', 0),
                    'total_value_after': portfolio_value.get('total_usd', 0)
                }
                email_notifier.send_notification('sell', email_data)
        except Exception as e:
            logger.error(f"❌ Erro ao enviar email de ação: {e}")
    
    def get_summary(self, analysis_result: Dict) -> str:
        """
        Gera um resumo legível da análise.
        
        Args:
            analysis_result: Resultado da análise
        
        Returns:
            String formatada com resumo
        """
        if not analysis_result.get('success'):
            return f"❌ Erro: {analysis_result.get('error', 'Erro desconhecido')}"
        
        portfolio = analysis_result.get('portfolio_status', {})
        market = analysis_result.get('market_analysis', {})
        recommendation = analysis_result.get('recommendation', {})
        action_taken = analysis_result.get('action_taken', {})
        
        portfolio_value = portfolio.get('portfolio_value', {})
        current_price = market.get('current_price', 0)
        action = recommendation.get('action', 'HOLD')
        confidence = recommendation.get('confidence', 0)
        
        summary = f"""
╔═══════════════════════════════════════════════════════════╗
║           RELATÓRIO DE TRADING AUTOMÁTICO                 ║
╚═══════════════════════════════════════════════════════════╝

📅 Data/Hora: {analysis_result.get('timestamp', 'N/A')}

💰 PORTFÓLIO:
   - Valor Total: ${portfolio_value.get('total_usd', 0):,.2f}
   - BTC: {portfolio.get('balance', {}).get('btc', 0):.8f}
   - USDT: ${portfolio.get('balance', {}).get('usdt', 0):,.2f}

📊 MERCADO:
   - Preço BTC: ${current_price:,.2f}
   - RSI (1h): {market.get('analysis_1h', {}).get('rsi', 0):.2f}
   - RSI (4h): {market.get('analysis_4h', {}).get('rsi', 0):.2f}

🎯 RECOMENDAÇÃO:
   - Ação: {action}
   - Confiança: {confidence:.0%}
   - Motivo: {recommendation.get('reason', 'N/A')}

⚡ AÇÃO EXECUTADA:
"""
        
        if action_taken.get('success'):
            action_result = action_taken.get('result', {})
            if action_taken.get('action') == 'BUY':
                summary += f"   ✅ COMPRA executada\n"
                summary += f"   - Quantidade: {action_result.get('quantity_btc', 0):.8f} BTC\n"
                summary += f"   - Valor: ${action_result.get('total_usd', 0):,.2f}\n"
            elif action_taken.get('action') == 'SELL':
                summary += f"   ✅ VENDA executada\n"
                summary += f"   - Quantidade: {action_result.get('quantity_btc', 0):.8f} BTC\n"
                summary += f"   - Valor: ${action_result.get('total_usd', 0):,.2f}\n"
                if action_result.get('profit_percent'):
                    summary += f"   - Lucro: {action_result.get('profit_percent', 0):+.2f}%\n"
        elif action_taken.get('mode') == 'analysis_only':
            summary += f"   ⚠️ Modo de análise apenas - ação não executada\n"
        else:
            summary += f"   ⏸️ {action_taken.get('reason', 'Nenhuma ação')}\n"
        
        return summary


def main(auto_execute: bool = True):
    """
    Função principal para execução do auto trader.
    
    Args:
        auto_execute: Se True, executa trades. Se False, apenas analisa.
    """
    logger.info("=" * 60)
    logger.info("🤖 INICIANDO TRADING AUTOMÁTICO")
    logger.info("=" * 60)
    
    trader = AutoTrader(auto_execute=auto_execute)
    result = trader.run_analysis()
    
    # Imprime resumo
    summary = trader.get_summary(result)
    print(summary)
    logger.info(summary)
    
    logger.info("=" * 60)
    logger.info("✅ TRADING AUTOMÁTICO FINALIZADO")
    logger.info("=" * 60)
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Trading Automático de Bitcoin')
    parser.add_argument(
        '--analysis-only',
        action='store_true',
        help='Apenas analisa, não executa trades'
    )
    
    args = parser.parse_args()
    auto_execute = not args.analysis_only
    
    main(auto_execute=auto_execute)

