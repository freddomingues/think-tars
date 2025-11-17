#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schema para armazenar conversas e análises de sentimento.
"""

import boto3
from datetime import datetime
from typing import Dict, List, Optional
import json
from decimal import Decimal
from config.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

class DecimalEncoder(json.JSONEncoder):
    """JSON encoder que converte Decimal para float."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

class ConversationManager:
    def __init__(self):
        self.dynamodb = boto3.resource(
            "dynamodb",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        # Inicializa as tabelas
        self._load_tables()
    
    def _convert_floats_to_decimal(self, obj):
        """Converte valores float para Decimal para compatibilidade com DynamoDB."""
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_floats_to_decimal(item) for item in obj]
        else:
            return obj
    
    def _load_tables(self):
        """Carrega as tabelas existentes."""
        try:
            # Tabela para conversas
            self.conversations_table = self.dynamodb.Table("Conversations")
            
            # Tabela para mensagens individuais
            self.messages_table = self.dynamodb.Table("Messages")
            
            # Tabela para análises de sentimento
            self.sentiment_table = self.dynamodb.Table("SentimentAnalysis")
        except Exception as e:
            print(f"⚠️  Erro ao carregar tabelas: {e}")
            # Tabelas ainda não existem, serão criadas no create_tables()

    def create_tables(self):
        """Cria as tabelas necessárias no DynamoDB."""
        try:
            # Tabela de conversas
            self.conversations_table = self.dynamodb.create_table(
                TableName='Conversations',
                KeySchema=[
                    {'AttributeName': 'conversation_id', 'KeyType': 'HASH'},
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'conversation_id', 'AttributeType': 'S'},
                    {'AttributeName': 'phone_number', 'AttributeType': 'S'},
                    {'AttributeName': 'created_at', 'AttributeType': 'S'},
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'phone-number-index',
                        'KeySchema': [
                            {'AttributeName': 'phone_number', 'KeyType': 'HASH'},
                            {'AttributeName': 'created_at', 'KeyType': 'RANGE'},
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Tabela de mensagens
            self.messages_table = self.dynamodb.create_table(
                TableName='Messages',
                KeySchema=[
                    {'AttributeName': 'message_id', 'KeyType': 'HASH'},
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'message_id', 'AttributeType': 'S'},
                    {'AttributeName': 'conversation_id', 'AttributeType': 'S'},
                    {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'conversation-index',
                        'KeySchema': [
                            {'AttributeName': 'conversation_id', 'KeyType': 'HASH'},
                            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'},
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Tabela de análise de sentimento
            self.sentiment_table = self.dynamodb.create_table(
                TableName='SentimentAnalysis',
                KeySchema=[
                    {'AttributeName': 'analysis_id', 'KeyType': 'HASH'},
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'analysis_id', 'AttributeType': 'S'},
                    {'AttributeName': 'message_id', 'AttributeType': 'S'},
                    {'AttributeName': 'conversation_id', 'AttributeType': 'S'},
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'message-index',
                        'KeySchema': [
                            {'AttributeName': 'message_id', 'KeyType': 'HASH'},
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    },
                    {
                        'IndexName': 'conversation-index',
                        'KeySchema': [
                            {'AttributeName': 'conversation_id', 'KeyType': 'HASH'},
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            print("✅ Tabelas criadas com sucesso!")
            
        except Exception as e:
            if "ResourceInUseException" in str(e):
                print("ℹ️  Tabelas já existem.")
            else:
                print(f"❌ Erro ao criar tabelas: {e}")
        
        # Carrega as tabelas após criação
        self._load_tables()

    def save_message(self, conversation_id: str, phone_number: str, message: str, 
                   sender: str, timestamp: datetime = None) -> str:
        """Salva uma mensagem na conversa."""
        if timestamp is None:
            timestamp = datetime.now()
            
        message_id = f"{conversation_id}_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            # Salva a mensagem
            self.messages_table.put_item(
                Item={
                    'message_id': message_id,
                    'conversation_id': conversation_id,
                    'phone_number': phone_number,
                    'message': message,
                    'sender': sender,  # 'user' ou 'assistant'
                    'timestamp': timestamp.isoformat(),
                    'created_at': timestamp.isoformat()
                }
            )
            
            # Atualiza ou cria a conversa
            self.conversations_table.put_item(
                Item={
                    'conversation_id': conversation_id,
                    'phone_number': phone_number,
                    'last_message': message,
                    'last_activity': timestamp.isoformat(),
                    'created_at': timestamp.isoformat(),
                    'message_count': 1
                }
            )
            
            return message_id
            
        except Exception as e:
            print(f"❌ Erro ao salvar mensagem: {e}")
            return None

    def save_sentiment_analysis(self, message_id: str, conversation_id: str, 
                               sentiment_data: Dict) -> str:
        """Salva análise de sentimento de uma mensagem."""
        analysis_id = f"sentiment_{message_id}"
        
        try:
            # Converte floats para Decimal
            converted_data = self._convert_floats_to_decimal(sentiment_data)
            
            self.sentiment_table.put_item(
                Item={
                    'analysis_id': analysis_id,
                    'message_id': message_id,
                    'conversation_id': conversation_id,
                    'sentiment': converted_data.get('sentiment'),
                    'confidence': converted_data.get('confidence', Decimal('0.0')),
                    'scores': json.dumps(converted_data.get('scores', {}), cls=DecimalEncoder),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return analysis_id
            
        except Exception as e:
            print(f"❌ Erro ao salvar análise de sentimento: {e}")
            return None

    def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
        """Recupera todas as mensagens de uma conversa."""
        try:
            response = self.messages_table.query(
                IndexName='conversation-index',
                KeyConditionExpression='conversation_id = :conv_id',
                ExpressionAttributeValues={':conv_id': conversation_id},
                ScanIndexForward=True  # Ordem cronológica
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            print(f"❌ Erro ao recuperar mensagens: {e}")
            return []

    def get_conversation_sentiment(self, conversation_id: str) -> List[Dict]:
        """Recupera análise de sentimento de uma conversa."""
        try:
            response = self.sentiment_table.query(
                IndexName='conversation-index',
                KeyConditionExpression='conversation_id = :conv_id',
                ExpressionAttributeValues={':conv_id': conversation_id}
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            print(f"❌ Erro ao recuperar análise de sentimento: {e}")
            return []

    def get_all_conversations(self) -> List[Dict]:
        """Recupera todas as conversas."""
        try:
            response = self.conversations_table.scan()
            return response.get('Items', [])
        except Exception as e:
            print(f"❌ Erro ao recuperar todas as conversas: {e}")
            return []

    def get_user_conversations(self, phone_number: str) -> List[Dict]:
        """Recupera todas as conversas de um usuário."""
        try:
            response = self.conversations_table.query(
                IndexName='phone-number-index',
                KeyConditionExpression='phone_number = :phone',
                ExpressionAttributeValues={':phone': phone_number},
                ScanIndexForward=False  # Mais recentes primeiro
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            print(f"❌ Erro ao recuperar conversas do usuário: {e}")
            return []

# Instância global
conversation_manager = ConversationManager()
