import boto3
import os
import time # Importar time para o timestamp
import logging
from botocore.exceptions import ClientError
from config.settings import DYNAMODB_TABLE_NAME, AWS_REGION

logger = logging.getLogger(__name__)

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

def get_user_thread_id(phone_number: str) -> str | None:
    """
    Recupera o thread_id do usuário do DynamoDB.
    Retorna o thread_id se encontrado, None caso contrário ou em caso de erro.
    """
    try:
        response = table.get_item(Key={'phone_number': phone_number})
        item = response.get('Item')
        if item:
            logger.info(f"💾 [DYNAMODB] Thread ID encontrado para {phone_number}: {item['thread_id']}")
            return item['thread_id']
        logger.info(f"💾 [DYNAMODB] Nenhuma Thread ID encontrada para {phone_number}.")
        return None
    except ClientError as e:
        # Erros específicos do cliente Boto3, como permissão negada, etc.
        logger.error(f"❌ [DYNAMODB] Erro ao buscar thread ID no DynamoDB para {phone_number}: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        # Outros erros inesperados
        logger.error(f"❌ [DYNAMODB] Erro inesperado ao buscar thread ID: {e}")
        return None

def save_user_thread_id(phone_number: str, thread_id: str):
    """
    Salva ou atualiza o thread_id do usuário no DynamoDB.
    """
    try:
        table.put_item(
            Item={
                'phone_number': phone_number,
                'thread_id': thread_id,
                'last_updated': int(time.time()) # Timestamp Unix para rastrear a última atualização
            }
        )
        logger.info(f"💾 [DYNAMODB] Thread ID {thread_id} salvo/atualizado para {phone_number} no DynamoDB.")
    except ClientError as e:
        # Erros específicos do cliente Boto3
        logger.error(f"❌ [DYNAMODB] Erro ao salvar thread ID no DynamoDB para {phone_number}: {e.response['Error']['Message']}")
    except Exception as e:
        # Outros erros inesperados
        logger.error(f"❌ [DYNAMODB] Erro inesperado ao salvar thread ID: {e}")