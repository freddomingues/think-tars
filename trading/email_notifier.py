# -*- coding: utf-8 -*-
"""
Sistema de notificação por email para operações de trading.
"""
import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Classe para enviar notificações por email sobre operações de trading."""
    
    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        email_from: Optional[str] = None,
        email_password: Optional[str] = None,
        email_to: Optional[str] = None
    ):
        """
        Inicializa o notificador de email.
        
        Args:
            smtp_server: Servidor SMTP (ex: smtp.gmail.com, smtp-mail.outlook.com)
            smtp_port: Porta SMTP (geralmente 587 para TLS)
            email_from: Email remetente
            email_password: Senha do email ou app password
            email_to: Email destinatário
        """
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.email_from = email_from or os.getenv('EMAIL_FROM', '')
        self.email_password = email_password or os.getenv('EMAIL_PASSWORD', '')
        self.email_to = email_to or os.getenv('EMAIL_TO', 'fred_domingues@outlook.com')
        
        self.enabled = bool(self.email_from and self.email_password and self.email_to)
        
        if not self.enabled:
            logger.warning("⚠️ Notificações por email desabilitadas - credenciais não configuradas")
        else:
            logger.info(f"✅ Notificador de email configurado: {self.email_from} -> {self.email_to}")
    
    def _create_email_body(self, subject_type: str, data: Dict) -> str:
        """
        Cria o corpo do email em HTML.
        
        Args:
            subject_type: Tipo de assunto (analysis, buy, sell, error)
            data: Dados da operação
        
        Returns:
            String HTML formatada
        """
        timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .content {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 0 0 10px 10px;
        }}
        .section {{
            margin: 20px 0;
            padding: 15px;
            background: white;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}
        .section h3 {{
            margin-top: 0;
            color: #667eea;
        }}
        .value {{
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .success {{
            color: #27ae60;
        }}
        .warning {{
            color: #f39c12;
        }}
        .error {{
            color: #e74c3c;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        table td {{
            padding: 8px;
            border-bottom: 1px solid #eee;
        }}
        table td:first-child {{
            font-weight: bold;
            width: 40%;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Trading Automático - Bitcoin</h1>
        <p>{timestamp}</p>
    </div>
    <div class="content">
"""
        
        if subject_type == 'analysis':
            recommendation = data.get('recommendation', {})
            action = recommendation.get('action', 'HOLD')
            confidence = recommendation.get('confidence', 0)
            action_taken = data.get('action_taken', {})
            
            html += f"""
        <div class="section">
            <h3>📊 Análise do Mercado</h3>
            <p><strong>Preço Atual do Bitcoin:</strong> <span class="value">${data.get('current_price', 0):,.2f}</span></p>
            <p><strong>RSI (1h):</strong> {data.get('rsi_1h', 0):.2f}</p>
            <p><strong>RSI (4h):</strong> {data.get('rsi_4h', 0):.2f}</p>
        </div>
        
        <div class="section">
            <h3>🎯 Recomendação</h3>
            <p><strong>Ação:</strong> <span class="value {'success' if action == 'BUY' else 'warning' if action == 'SELL' else ''}">{action}</span></p>
            <p><strong>Confiança:</strong> {confidence:.0%}</p>
            <p><strong>Motivo:</strong> {recommendation.get('reason', 'N/A')}</p>
        </div>
"""
            
            # Mostra ação executada se houver
            if action_taken.get('success'):
                action_result = action_taken.get('result', {})
                if action_taken.get('action') == 'BUY':
                    html += f"""
        <div class="section">
            <h3>✅ Ação Executada: COMPRA</h3>
            <table>
                <tr><td>Quantidade:</td><td class="value">{action_result.get('quantity_btc', 0):.8f} BTC</td></tr>
                <tr><td>Valor:</td><td class="value">${action_result.get('total_usd', 0):,.2f}</td></tr>
                <tr><td>Preço:</td><td>${action_result.get('price', 0):,.2f}</td></tr>
            </table>
        </div>
"""
                elif action_taken.get('action') == 'SELL':
                    profit_percent = action_result.get('profit_percent', 0)
                    profit_class = 'success' if profit_percent > 0 else 'error' if profit_percent < 0 else ''
                    html += f"""
        <div class="section">
            <h3>💸 Ação Executada: VENDA</h3>
            <table>
                <tr><td>Quantidade:</td><td class="value">{action_result.get('quantity_btc', 0):.8f} BTC</td></tr>
                <tr><td>Valor Recebido:</td><td class="value">${action_result.get('total_usd', 0):,.2f}</td></tr>
                <tr><td>Preço:</td><td>${action_result.get('price', 0):,.2f}</td></tr>
"""
                    if profit_percent != 0:
                        html += f"""
                <tr><td>Lucro/Prejuízo:</td><td class="value {profit_class}">{profit_percent:+.2f}%</td></tr>
"""
                    html += """
            </table>
        </div>
"""
            elif action_taken.get('action') == 'HOLD' or not action_taken.get('success'):
                html += f"""
        <div class="section">
            <h3>⏸️ Nenhuma Ação Executada</h3>
            <p>{action_taken.get('reason', 'Aguardando sinal mais claro')}</p>
        </div>
"""
            
            # Formata BTC com precisão adequada (mostra até 8 casas decimais se necessário)
            btc_balance = data.get('btc_balance', 0)
            usdt_balance = data.get('usdt_balance', 0)
            
            # Determina quantas casas decimais mostrar para BTC
            if btc_balance == 0:
                btc_format = "0.00000000"
            elif btc_balance < 0.00001:
                btc_format = f"{btc_balance:.8f}".rstrip('0').rstrip('.')
            elif btc_balance < 0.01:
                btc_format = f"{btc_balance:.6f}".rstrip('0').rstrip('.')
            else:
                btc_format = f"{btc_balance:.8f}".rstrip('0').rstrip('.')
            
            html += f"""
        <div class="section">
            <h3>💼 Portfólio Atual</h3>
            <table>
                <tr><td>Bitcoin (BTC):</td><td class="value">{btc_format}</td></tr>
                <tr><td>USDT:</td><td>${usdt_balance:,.2f}</td></tr>
                <tr><td>Valor Total:</td><td class="value">${data.get('total_value', 0):,.2f}</td></tr>
"""
            
            # Adiciona lucro/prejuízo não realizado se houver
            if data.get('unrealized_pnl'):
                pnl = data.get('unrealized_pnl', {})
                pnl_percent = pnl.get('percent', 0)
                pnl_class = 'success' if pnl_percent > 0 else 'error' if pnl_percent < 0 else ''
                if pnl_percent != 0:
                    html += f"""
                <tr><td>Lucro/Prejuízo Não Realizado:</td><td class="value {pnl_class}">{pnl_percent:+.2f}%</td></tr>
"""
            
            html += """
            </table>
        </div>
"""
        
        elif subject_type == 'buy':
            order = data.get('order', {})
            html += f"""
        <div class="section">
            <h3>✅ Compra Executada</h3>
            <table>
                <tr><td>ID da Ordem:</td><td>{order.get('orderId', 'N/A')}</td></tr>
                <tr><td>Status:</td><td class="success">{order.get('status', 'N/A')}</td></tr>
                <tr><td>Quantidade:</td><td class="value">{data.get('quantity_btc', 0):.8f} BTC</td></tr>
                <tr><td>Valor:</td><td class="value">${data.get('value_usd', 0):,.2f} USDT</td></tr>
                <tr><td>Preço:</td><td>${data.get('price', 0):,.2f} por BTC</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h3>💼 Portfólio Atualizado</h3>
            <table>
                <tr><td>Bitcoin (BTC):</td><td class="value">{data.get('btc_balance_after', 0):.8f}</td></tr>
                <tr><td>USDT:</td><td>${data.get('usdt_balance_after', 0):,.2f}</td></tr>
                <tr><td>Valor Total:</td><td class="value">${data.get('total_value_after', 0):,.2f}</td></tr>
            </table>
        </div>
"""
        
        elif subject_type == 'sell':
            order = data.get('order', {})
            profit_percent = data.get('profit_percent', 0)
            profit_class = 'success' if profit_percent > 0 else 'error' if profit_percent < 0 else ''
            
            html += f"""
        <div class="section">
            <h3>💸 Venda Executada</h3>
            <table>
                <tr><td>ID da Ordem:</td><td>{order.get('orderId', 'N/A')}</td></tr>
                <tr><td>Status:</td><td class="success">{order.get('status', 'N/A')}</td></tr>
                <tr><td>Quantidade:</td><td class="value">{data.get('quantity_btc', 0):.8f} BTC</td></tr>
                <tr><td>Valor Recebido:</td><td class="value">${data.get('value_usd', 0):,.2f} USDT</td></tr>
                <tr><td>Preço:</td><td>${data.get('price', 0):,.2f} por BTC</td></tr>
            </table>
        </div>
"""
            
            if profit_percent != 0:
                html += f"""
        <div class="section">
            <h3>📊 Performance</h3>
            <p><strong>Preço de Entrada:</strong> ${data.get('entry_price', 0):,.2f}</p>
            <p><strong>Preço de Saída:</strong> ${data.get('price', 0):,.2f}</p>
            <p><strong>Lucro/Prejuízo:</strong> <span class="value {profit_class}">{profit_percent:+.2f}%</span></p>
        </div>
"""
            
            html += f"""
        <div class="section">
            <h3>💼 Portfólio Atualizado</h3>
            <table>
                <tr><td>Bitcoin (BTC):</td><td class="value">{data.get('btc_balance_after', 0):.8f}</td></tr>
                <tr><td>USDT:</td><td>${data.get('usdt_balance_after', 0):,.2f}</td></tr>
                <tr><td>Valor Total:</td><td class="value">${data.get('total_value_after', 0):,.2f}</td></tr>
            </table>
        </div>
"""
        
        elif subject_type == 'error':
            html += f"""
        <div class="section">
            <h3 class="error">❌ Erro na Operação</h3>
            <p><strong>Erro:</strong> <span class="error">{data.get('error', 'Erro desconhecido')}</span></p>
            <p><strong>Detalhes:</strong> {data.get('details', 'N/A')}</p>
        </div>
"""
        
        html += f"""
    </div>
    <div class="footer">
        <p>Este é um email automático do sistema de Trading Automático</p>
        <p>Não responda este email</p>
    </div>
</body>
</html>
"""
        
        return html
    
    def send_notification(
        self,
        subject_type: str,
        data: Dict,
        subject_override: Optional[str] = None
    ) -> bool:
        """
        Envia notificação por email.
        
        Args:
            subject_type: Tipo de notificação (analysis, buy, sell, error)
            data: Dados da operação
            subject_override: Assunto personalizado (opcional)
        
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.enabled:
            logger.warning("Notificações por email desabilitadas")
            return False
        
        try:
            # Define assunto
            subjects = {
                'analysis': '📊 Análise de Mercado - Trading Automático',
                'buy': '✅ Compra Executada - Trading Automático',
                'sell': '💸 Venda Executada - Trading Automático',
                'error': '❌ Erro no Trading Automático'
            }
            subject = subject_override or subjects.get(subject_type, 'Notificação - Trading Automático')
            
            # Cria mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = subject
            
            # Cria corpo HTML
            html_body = self._create_email_body(subject_type, data)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Envia email
            logger.info(f"📧 Enviando email para {self.email_to}...")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email enviado com sucesso para {self.email_to}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Erro ao enviar email: {e}")
            return False


# Instância global
email_notifier = EmailNotifier()

