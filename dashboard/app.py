#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard web para visualização de conversas e análise de sentimento.
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
from datetime import datetime, timedelta
from typing import Dict, List
import logging

from data_store.conversation_schema import ConversationManager
from sentiment_analyses.advanced_sentiment import sentiment_analyzer

# Configuração do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

logger = logging.getLogger(__name__)

# Cria uma nova instância do conversation_manager
conversation_manager = ConversationManager()
conversation_manager._load_tables()

@app.route('/')
def index():
    """Página principal do dashboard."""
    return render_template('dashboard.html')

@app.route('/api/conversations')
def get_conversations():
    """API para listar conversas."""
    try:
        phone_number = request.args.get('phone_number')
        
        if phone_number:
            conversations = conversation_manager.get_user_conversations(phone_number)
        else:
            # Lista todas as conversas
            conversations = conversation_manager.get_all_conversations()
        
        return jsonify({
            'status': 'success',
            'conversations': conversations
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar conversas: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/conversation/<conversation_id>')
def get_conversation_details(conversation_id):
    """API para detalhes de uma conversa específica."""
    try:
        # Busca mensagens da conversa
        messages = conversation_manager.get_conversation_messages(conversation_id)
        
        # Busca análises de sentimento
        sentiment_data = conversation_manager.get_conversation_sentiment(conversation_id)
        
        # Analisa sentimento geral da conversa
        conversation_sentiment = sentiment_analyzer.analyze_conversation_sentiment(messages)
        
        return jsonify({
            'status': 'success',
            'conversation_id': conversation_id,
            'messages': messages,
            'sentiment_analysis': sentiment_data,
            'conversation_sentiment': conversation_sentiment
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar detalhes da conversa: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sentiment/analyze', methods=['POST'])
def analyze_sentiment():
    """API para analisar sentimento de um texto."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'status': 'error', 'message': 'Texto não fornecido'}), 400
        
        analysis = sentiment_analyzer.analyze_sentiment(text)
        
        return jsonify({
            'status': 'success',
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na análise de sentimento: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """API para estatísticas gerais."""
    try:
        # Implementar estatísticas gerais
        stats = {
            'total_conversations': 0,
            'total_messages': 0,
            'sentiment_distribution': {
                'positivo': 0,
                'negativo': 0,
                'neutro': 0
            },
            'avg_confidence': 0.0
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar estatísticas: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Cliente conectado ao WebSocket."""
    logger.info("🔌 Cliente conectado ao dashboard")
    emit('status', {'message': 'Conectado ao dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado do WebSocket."""
    logger.info("🔌 Cliente desconectado do dashboard")

@socketio.on('join_conversation')
def handle_join_conversation(data):
    """Cliente quer acompanhar uma conversa específica."""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        logger.info(f"👥 Cliente acompanhando conversa: {conversation_id}")
        emit('joined_conversation', {'conversation_id': conversation_id})

def broadcast_new_message(conversation_id: str, message_data: Dict):
    """Broadcast nova mensagem para clientes conectados."""
    socketio.emit('new_message', {
        'conversation_id': conversation_id,
        'message': message_data
    })

def broadcast_sentiment_analysis(conversation_id: str, analysis_data: Dict):
    """Broadcast nova análise de sentimento."""
    socketio.emit('sentiment_update', {
        'conversation_id': conversation_id,
        'analysis': analysis_data
    })

if __name__ == '__main__':
    # Cria tabelas se não existirem
    conversation_manager.create_tables()
    
    # Inicia o dashboard
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
