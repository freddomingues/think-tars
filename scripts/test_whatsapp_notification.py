#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para validar envio de notificação WhatsApp após criar evento.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import AGENDAMENTO_WHATSAPP_NUMBER
from external_services.zapi_client import send_text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_whatsapp_notification():
    """Testa envio de notificação WhatsApp."""
    print("=" * 60)
    print("TESTE DE NOTIFICAÇÃO WHATSAPP")
    print("=" * 60)
    print()
    
    print(f"1. Número configurado: {AGENDAMENTO_WHATSAPP_NUMBER}")
    
    # Mensagem de teste
    test_message = (
        f"📅 *TESTE DE NOTIFICAÇÃO*\n\n"
        f"👤 *Lead:* Teste Automatizado\n"
        f"📋 *Assunto:* Reunião de Teste\n"
        f"📅 *Data:* 03/02/2026\n"
        f"🕐 *Horário:* 14:00\n"
        f"\n📝 *Detalhes:* Este é um teste do sistema de notificação automática.\n"
    )
    
    print(f"\n2. Enviando mensagem de teste...")
    print(f"   Mensagem: {test_message[:100]}...")
    
    result = send_text(AGENDAMENTO_WHATSAPP_NUMBER, test_message)
    
    if result:
        print(f"\n✅ Mensagem enviada com sucesso para {AGENDAMENTO_WHATSAPP_NUMBER}")
    else:
        print(f"\n❌ Falha ao enviar mensagem para {AGENDAMENTO_WHATSAPP_NUMBER}")
        print("   Verifique:")
        print("   - ZAPI_INSTANCE_ID está configurado?")
        print("   - ZAPI_TOKEN_INSTANCE está configurado?")
        print("   - Z-API está funcionando?")
    
    print("\n" + "=" * 60)
    return result

if __name__ == "__main__":
    success = test_whatsapp_notification()
    sys.exit(0 if success else 1)
