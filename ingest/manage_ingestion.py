#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de gerenciamento para ingestão de documentos.
Permite executar ingestão de forma controlada e monitorada.
"""

import argparse
import sys
import time
from ingest.ingest_contracts import index_all_contracts
from ingest.ingest_faqs import index_all_faqs
from ingest.cache_manager import document_cache
from ingest.async_ingestion import ingest_all_documents
import asyncio

def main():
    parser = argparse.ArgumentParser(description='Gerenciador de Ingestão de Documentos')
    parser.add_argument('--type', choices=['contracts', 'faqs', 'all'], default='all',
                       help='Tipo de documentos para processar')
    parser.add_argument('--async-mode', action='store_true', 
                       help='Executar de forma assíncrona (apenas para --type all)')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Limpar cache antes de processar')
    parser.add_argument('--stats', action='store_true',
                       help='Mostrar estatísticas do cache')
    
    args = parser.parse_args()
    
    # Mostrar estatísticas do cache
    if args.stats:
        stats = document_cache.get_cache_stats()
        print("📊 Estatísticas do Cache:")
        print(f"   Documentos processados: {stats['total_processed']}")
        print(f"   Última atualização: {stats['last_update']}")
        print(f"   Arquivo de cache: {stats['cache_file']}")
        return
    
    # Limpar cache se solicitado
    if args.clear_cache:
        print("🗑️  Limpando cache...")
        document_cache.clear_cache()
    
    start_time = time.time()
    
    try:
        if args.async_mode and args.type == 'all':
            print("🚀 Executando ingestão assíncrona...")
            asyncio.run(ingest_all_documents())
        else:
            if args.type == 'contracts' or args.type == 'all':
                print("📄 Processando contratos...")
                index_all_contracts()
            
            if args.type == 'faqs' or args.type == 'all':
                print("❓ Processando FAQs...")
                index_all_faqs()
        
        elapsed_time = time.time() - start_time
        print(f"✅ Processamento concluído em {elapsed_time:.2f} segundos!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Processamento interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro durante o processamento: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
