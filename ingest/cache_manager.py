#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de cache para verificar documentos já processados.
Evita reprocessar documentos que já foram indexados.
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Set
import boto3
from config import settings

class DocumentCache:
    def __init__(self, cache_file: str = "document_cache.json"):
        self.cache_file = cache_file
        self.cache_data = self._load_cache()
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    def _load_cache(self) -> Dict:
        """Carrega cache do arquivo JSON."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar cache: {e}")
        return {"processed_docs": {}, "last_update": None}
    
    def _save_cache(self):
        """Salva cache no arquivo JSON."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
    
    def _get_file_hash(self, bucket: str, key: str) -> str:
        """Calcula hash do arquivo no S3."""
        try:
            response = self.s3_client.head_object(Bucket=bucket, Key=key)
            etag = response.get('ETag', '').strip('"')
            last_modified = response.get('LastModified', '').isoformat()
            return hashlib.md5(f"{etag}{last_modified}".encode()).hexdigest()
        except Exception as e:
            print(f"Erro ao calcular hash de {key}: {e}")
            return None
    
    def is_processed(self, s3_key: str) -> bool:
        """Verifica se documento já foi processado."""
        current_hash = self._get_file_hash(settings.S3_BUCKET_NAME, s3_key)
        if not current_hash:
            return False
        
        cached_hash = self.cache_data["processed_docs"].get(s3_key)
        return cached_hash == current_hash
    
    def mark_processed(self, s3_key: str):
        """Marca documento como processado."""
        current_hash = self._get_file_hash(settings.S3_BUCKET_NAME, s3_key)
        if current_hash:
            self.cache_data["processed_docs"][s3_key] = current_hash
            self.cache_data["last_update"] = datetime.now().isoformat()
            self._save_cache()
    
    def get_unprocessed_docs(self, doc_keys: list) -> list:
        """Retorna lista de documentos não processados."""
        unprocessed = []
        for key in doc_keys:
            if not self.is_processed(key):
                unprocessed.append(key)
        return unprocessed
    
    def clear_cache(self):
        """Limpa cache completamente."""
        self.cache_data = {"processed_docs": {}, "last_update": None}
        self._save_cache()
        print("Cache limpo com sucesso!")
    
    def force_clear_cache(self):
        """Força limpeza completa do cache."""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        self.cache_data = {"processed_docs": {}, "last_update": None}
        print("Cache forçadamente limpo!")
    
    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache."""
        total_docs = len(self.cache_data["processed_docs"])
        last_update = self.cache_data.get("last_update", "Nunca")
        return {
            "total_processed": total_docs,
            "last_update": last_update,
            "cache_file": self.cache_file
        }

# Instância global do cache
document_cache = DocumentCache()
