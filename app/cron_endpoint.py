# -*- coding: utf-8 -*-
"""
Endpoint para execução do trading automático via cron externo.
Permite que serviços de cron (como cron-job.org) executem o trading via HTTP.
"""
import sys
import os
import logging

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import request, jsonify
from trading.auto_trader import main as run_auto_trader
from config.settings import CRON_SECRET_TOKEN

logger = logging.getLogger(__name__)

# Token de segurança importado de settings


def register_cron_endpoint(app):
    """
    Registra o endpoint de cron no app Flask.
    
    Args:
        app: Instância do Flask app
    """
    
    @app.route('/cron/trading', methods=['POST', 'GET'])
    def cron_trading():
        """
        Endpoint para executar trading automático via cron externo.
        
        Requer token de segurança no header X-Cron-Token ou query parameter.
        """
        # Verifica token de segurança
        token = request.headers.get('X-Cron-Token') or request.args.get('token', '')
        
        if CRON_SECRET_TOKEN and token != CRON_SECRET_TOKEN:
            logger.warning(f"❌ Tentativa de acesso não autorizado ao cron endpoint")
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Token inválido ou ausente'
            }), 401
        
        try:
            logger.info("🤖 Executando trading automático via endpoint cron...")
            
            # Executa o trading automático
            result = run_auto_trader(auto_execute=True)
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'message': 'Trading executado com sucesso',
                    'timestamp': result.get('timestamp'),
                    'action': result.get('action_taken', {}).get('action', 'HOLD')
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Erro desconhecido'),
                    'timestamp': result.get('timestamp')
                }), 500
        
        except Exception as e:
            logger.error(f"❌ Erro ao executar trading via cron endpoint: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/cron/trading/health', methods=['GET'])
    def cron_health():
        """Endpoint de health check para o cron."""
        return jsonify({
            'status': 'ok',
            'service': 'trading-automático',
            'endpoint': '/cron/trading'
        }), 200

