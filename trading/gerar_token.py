# -*- coding: utf-8 -*-
"""
Script para gerar token secreto para o endpoint de cron.
"""
import secrets
import string

def gerar_token_secreto(tamanho=32):
    """
    Gera um token secreto seguro.
    
    Args:
        tamanho: Tamanho do token (padrão: 32 caracteres)
    
    Returns:
        String com token seguro
    """
    # Usa secrets para gerar token seguro
    alfabeto = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alfabeto) for _ in range(tamanho))
    return token

if __name__ == "__main__":
    print("=" * 60)
    print("🔑 GERADOR DE TOKEN SECRETO")
    print("=" * 60)
    
    # Gera token
    token = gerar_token_secreto(32)
    
    print(f"\n✅ Token gerado com sucesso!")
    print(f"\n📋 Adicione ao arquivo .env:")
    print(f"   CRON_SECRET_TOKEN={token}")
    print(f"\n📋 Ou adicione no Render (variáveis de ambiente):")
    print(f"   CRON_SECRET_TOKEN = {token}")
    print(f"\n⚠️  IMPORTANTE:")
    print(f"   - Guarde este token com segurança")
    print(f"   - Use o mesmo token no serviço de cron externo")
    print(f"   - Não compartilhe este token")
    print(f"\n" + "=" * 60)

