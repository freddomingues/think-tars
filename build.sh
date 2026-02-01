#!/bin/bash
# Script de build para Render.com
# Este script é executado durante o deploy para buildar o frontend

set -e

echo "🔨 Iniciando build do frontend..."

# Verifica se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Instalando..."
    # Render geralmente tem Node.js, mas se não tiver, tenta instalar
    exit 1
fi

# Navega para o diretório do frontend
cd frontend

# Instala dependências
echo "📦 Instalando dependências do frontend..."
npm install

# Build do frontend
echo "🏗️  Buildando frontend..."
npm run build

echo "✅ Build do frontend concluído!"

# Volta para o diretório raiz
cd ..

echo "✅ Build completo! Frontend disponível em frontend/dist"
