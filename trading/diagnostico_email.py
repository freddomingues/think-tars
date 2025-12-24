# -*- coding: utf-8 -*-
"""
Diagnóstico detalhado da configuração de email.
"""
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Força recarregar o .env
load_dotenv(override=True)

print("=" * 60)
print("🔍 DIAGNÓSTICO DE CONFIGURAÇÃO DE EMAIL")
print("=" * 60)

# Verifica se o arquivo .env existe
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
print(f"\n📁 Arquivo .env: {env_path}")
print(f"   Existe: {'✅ Sim' if os.path.exists(env_path) else '❌ Não'}")

# Carrega variáveis
smtp_server = os.getenv('SMTP_SERVER', '')
smtp_port = os.getenv('SMTP_PORT', '')
email_from = os.getenv('EMAIL_FROM', '')
email_password = os.getenv('EMAIL_PASSWORD', '')
email_to = os.getenv('EMAIL_TO', '')

print(f"\n📋 Configurações Carregadas:")
print(f"   SMTP_SERVER: {smtp_server}")
print(f"   SMTP_PORT: {smtp_port}")
print(f"   EMAIL_FROM: {email_from}")
print(f"   EMAIL_PASSWORD: {'✅ Configurada' if email_password else '❌ Não configurada'}")
if email_password:
    # Mostra apenas primeiros e últimos caracteres por segurança
    masked = email_password[:4] + "..." + email_password[-4:] if len(email_password) > 8 else "***"
    print(f"      (mostrando: {masked}, tamanho: {len(email_password)} caracteres)")
print(f"   EMAIL_TO: {email_to}")

# Verifica se é App Password (geralmente tem 16 caracteres)
print(f"\n🔍 Análise da Senha:")
if email_password:
    if len(email_password) == 16 and email_password.replace(' ', '').isalnum():
        print(f"   ✅ Parece ser uma App Password (16 caracteres alfanuméricos)")
    elif ' ' in email_password:
        print(f"   ⚠️ A senha contém espaços! Remova os espaços.")
        print(f"      Exemplo: 'abcd efgh ijkl mnop' → 'abcdefghijklmnop'")
    elif len(email_password) < 16:
        print(f"   ⚠️ App Password geralmente tem 16 caracteres")
        print(f"      Tamanho atual: {len(email_password)}")
    else:
        print(f"   ⚠️ Verifique se é uma App Password válida")
else:
    print(f"   ❌ Senha não configurada")

# Testa conexão SMTP
print(f"\n🔌 Testando Conexão SMTP...")
try:
    import smtplib
    
    if not smtp_server or not email_from or not email_password:
        print("   ❌ Configurações incompletas")
    else:
        print(f"   Conectando a {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, int(smtp_port) if smtp_port else 587)
        server.starttls()
        print(f"   Tentando autenticar como {email_from}...")
        try:
            server.login(email_from, email_password)
            print(f"   ✅ Autenticação bem-sucedida!")
            server.quit()
        except smtplib.SMTPAuthenticationError as e:
            print(f"   ❌ Erro de autenticação: {e}")
            if "Application-specific password" in str(e):
                print(f"\n   💡 SOLUÇÃO:")
                print(f"      1. Acesse: https://myaccount.google.com/apppasswords")
                print(f"      2. Gere uma nova App Password para 'Mail'")
                print(f"      3. Copie a senha de 16 caracteres SEM espaços")
                print(f"      4. Atualize EMAIL_PASSWORD no .env")
            elif "Invalid login" in str(e) or "535" in str(e):
                print(f"\n   💡 Verifique:")
                print(f"      - Se a senha está correta")
                print(f"      - Se está usando App Password (não senha normal)")
                print(f"      - Se a verificação em duas etapas está ativada")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            server.quit()
except Exception as e:
    print(f"   ❌ Erro na conexão: {e}")

print("\n" + "=" * 60)
print("✅ Diagnóstico concluído")
print("=" * 60)

