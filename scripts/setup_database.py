#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de setup (compatibilidade).
O projeto não usa mais DynamoDB; threads e conversas ficam em memória.
Execute na raiz do projeto: python scripts/setup_database.py
"""

def main():
    print("✅ O projeto não usa mais banco de dados AWS.")
    print("   Threads e conversas são armazenados em memória.")
    print("   Base de conhecimento: arquivos enviados pelos clientes + Pinecone.")
    print()
    print("🚀 O sistema está pronto para uso!")


if __name__ == "__main__":
    main()
