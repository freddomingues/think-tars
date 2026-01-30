# Z-API — Webhook (on-message-received)

## Documentação oficial

- **Webhooks:** https://developer.z-api.io/webhooks/introduction
- **Ao receber mensagem:** https://developer.z-api.io/webhooks/on-message-received

## Onde ajustar o payload

O parser está em **`external_services/zapi_client.parse_webhook_message(payload)`**.

A Z-API pode enviar **phoneId**, **phone**, **from**, **participant**; texto em **message**, **text**, **body**, **content**. O parser já tenta essas chaves (em `data` e no root). Se o SDR não responder:

1. Ver os **logs do backend** ao receber uma mensagem no WhatsApp: o webhook loga o payload (truncado) quando o parse falha ("payload sem telefone/texto válido").
2. Ajustar o parser para as chaves que aparecem nesse payload.
3. Testar localmente: **POST /api/zapi/test-webhook** com `phone` e `message`; ou **POST /api/zapi/webhook** com um JSON igual ao que a Z-API envia (ver skill **testing-local-backend**).

## Envio de texto

- **Endpoint:** `POST {ZAPI_BASE_URL}/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN_INSTANCE}/send-text`
- **Body:** `{ "phone": "5541999999999", "message": "texto" }`
- **Config:** `config/settings.py` — ZAPI_BASE_URL, ZAPI_INSTANCE_ID, ZAPI_TOKEN_INSTANCE.
