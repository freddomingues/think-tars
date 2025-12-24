#!/bin/bash
# Script para configurar o cron job do trading automático

# Diretório do projeto
PROJECT_DIR="/Users/freddomingues/Desenvolvimento/generative-ai"
VENV_PATH="$PROJECT_DIR/venv/bin/python"
SCRIPT_PATH="$PROJECT_DIR/trading/auto_trader.py"
LOG_DIR="$PROJECT_DIR/trading"

# Cria diretório de logs se não existir
mkdir -p "$LOG_DIR"

# Cria arquivo de cron temporário
CRON_FILE=$(mktemp)

# Obtém crontab atual
crontab -l > "$CRON_FILE" 2>/dev/null || true

# Remove entradas antigas do auto_trader se existirem
sed -i.bak '/auto_trader.py/d' "$CRON_FILE"

# Adiciona nova entrada (executa a cada 3 horas)
echo "# Trading Automático Bitcoin - Executa a cada 3 horas" >> "$CRON_FILE"
echo "0 */3 * * * cd $PROJECT_DIR && $VENV_PATH $SCRIPT_PATH >> $LOG_DIR/cron.log 2>&1" >> "$CRON_FILE"

# Instala o novo crontab
crontab "$CRON_FILE"

# Remove arquivo temporário
rm -f "$CRON_FILE" "$CRON_FILE.bak"

echo "✅ Cron job configurado com sucesso!"
echo ""
echo "📋 Configuração:"
echo "   - Execução: A cada 3 horas"
echo "   - Script: $SCRIPT_PATH"
echo "   - Logs: $LOG_DIR/cron.log"
echo ""
echo "Para visualizar o cron job:"
echo "   crontab -l"
echo ""
echo "Para remover o cron job:"
echo "   crontab -e  # e remova a linha do auto_trader.py"

