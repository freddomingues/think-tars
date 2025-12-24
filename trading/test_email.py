# -*- coding: utf-8 -*-
"""
Script de teste para verificar configuração de email.
"""
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from trading.email_notifier import email_notifier

print("=" * 60)
print("📧 TESTE DE NOTIFICAÇÃO POR EMAIL")
print("=" * 60)

if not email_notifier.enabled:
    print("\n❌ Notificações por email desabilitadas!")
    print("\n📝 Configure no arquivo .env:")
    print("   SMTP_SERVER=smtp-mail.outlook.com")
    print("   SMTP_PORT=587")
    print("   EMAIL_FROM=seu_email@outlook.com")
    print("   EMAIL_PASSWORD=sua_senha")
    print("   EMAIL_TO=fred_domingues@outlook.com")
    exit(1)

print(f"\n✅ Configuração encontrada:")
print(f"   - Servidor: {email_notifier.smtp_server}:{email_notifier.smtp_port}")
print(f"   - De: {email_notifier.email_from}")
print(f"   - Para: {email_notifier.email_to}")

print("\n📧 Enviando email de teste...")

# Dados de teste
test_data = {
    'timestamp': '2024-12-24 18:30:00',
    'current_price': 87720.42,
    'rsi_1h': 45.5,
    'rsi_4h': 48.2,
    'btc_balance': 0.00000989,
    'usdt_balance': 15.22,
    'total_value': 15.22
}

success = email_notifier.send_notification('analysis', test_data, '🧪 Teste - Trading Automático')

if success:
    print("\n✅ Email de teste enviado com sucesso!")
    print(f"   Verifique a caixa de entrada de {email_notifier.email_to}")
    print("   (incluindo pasta de spam)")
else:
    print("\n❌ Falha ao enviar email de teste")
    print("   Verifique os logs e configurações")

print("\n" + "=" * 60)

