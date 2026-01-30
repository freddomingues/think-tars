#!/usr/bin/env bash
# Testa o fluxo SDR localmente (sem Z-API chamar o servidor).
# Uso: ./scripts/test_sdr_webhook.sh [phone] [message]
# Exemplo: ./scripts/test_sdr_webhook.sh 554187497364 "Olá, quero saber sobre automação"

set -e
BASE_URL="${BASE_URL:-http://127.0.0.1:5004}"
PHONE="${1:-554187497364}"
MESSAGE="${2:-Olá, quero saber mais sobre soluções em IA}"

echo "POST $BASE_URL/api/zapi/test-webhook"
echo "Body: phone=$PHONE message=$MESSAGE"
echo "---"
curl -s -X POST "$BASE_URL/api/zapi/test-webhook" \
  -H "Content-Type: application/json" \
  -d "{\"phone\":\"$PHONE\",\"message\":\"$MESSAGE\"}" | python3 -m json.tool
