#!/usr/bin/env bash
# Expõe o webhook Z-API localmente via tunnel. A Z-API chama: https://SUA-URL/api/zapi/webhook
#
# Uso:
#   Terminal 1: python app/main.py
#   Terminal 2: ./scripts/run_webhook_local.sh              # tenta ngrok
#   Terminal 2: ./scripts/run_webhook_local.sh --lt        # localtunnel (se ngrok crashar no Mac)
#   Terminal 2: ./scripts/run_webhook_local.sh --localhost-run  # ssh (não precisa instalar nada)
#
# Na Z-API: URL = https://<URL-EXIBIDA-ABAIXO>/api/zapi/webhook | Evento: ao receber mensagem
# Logs: logs/zapi_webhook.log

set -e
PORT="${PORT:-5004}"
WEBHOOK_PATH="/api/zapi/webhook"

echo "=== Webhook local (tunnel) ==="
echo "Flask deve estar rodando em http://127.0.0.1:${PORT}"
echo "Se não estiver, em outro terminal: python app/main.py"
echo ""
echo "Na Z-API use: https://<URL-ABAIXO>${WEBHOOK_PATH}"
echo ""

case "${1:-}" in
  --lt|--localtunnel)
    if ! command -v npx >/dev/null 2>&1; then
      echo "npx não encontrado. Instale Node.js (https://nodejs.org) ou use: ./scripts/run_webhook_local.sh --localhost-run"
      exit 1
    fi
    echo "Usando localtunnel (npx)..."
    exec npx --yes localtunnel --port "$PORT"
    ;;
  --localhost-run)
    echo "Usando localhost.run (ssh)..."
    echo "A URL será exibida abaixo. Use-a na Z-API + ${WEBHOOK_PATH}"
    echo ""
    exec ssh -R 80:localhost:"$PORT" nokey@localhost.run
    ;;
  *)
    if command -v ngrok >/dev/null 2>&1; then
      echo "Usando ngrok..."
      exec ngrok http "$PORT"
    fi
    echo "ngrok não encontrado ou use alternativas:"
    echo "  ./scripts/run_webhook_local.sh --lt           # localtunnel (precisa Node/npx)"
    echo "  ./scripts/run_webhook_local.sh --localhost-run   # localhost.run (só ssh)"
    echo ""
    echo "Se o ngrok crashar no seu Mac, use: ./scripts/run_webhook_local.sh --lt"
    exit 1
    ;;
esac
