# Exemplos de curl para testes locais

Base URL: `http://127.0.0.1:5004` (ou a porta do Flask).

## SDR / Z-API

### Teste local do fluxo SDR (sem Z-API chamar o webhook)

```bash
curl -X POST http://127.0.0.1:5004/api/zapi/test-webhook \
  -H "Content-Type: application/json" \
  -d '{"phone":"554187497364","message":"Olá, quero saber sobre automação"}'
```

Resposta esperada: `{ "ok": true, "phone": "554187497364", "reply_preview": "...", "sent_via_zapi": true }`.

### Simular o webhook real (para debugar payload Z-API)

Se a Z-API envia um payload com estrutura diferente, teste enviando um JSON igual ao que a Z-API envia:

```bash
# Exemplo com phone e text
curl -X POST http://127.0.0.1:5004/api/zapi/webhook \
  -H "Content-Type: application/json" \
  -d '{"phone":"554187497364","text":{"message":"Olá"}}'

# Exemplo com phoneId e message
curl -X POST http://127.0.0.1:5004/api/zapi/webhook \
  -H "Content-Type: application/json" \
  -d '{"phoneId":"554187497364","message":"Olá"}'
```

O backend loga o payload quando o parse falha; use esse log para ajustar `parse_webhook_message` em `external_services/zapi_client.py`.

## Playground (demos)

```bash
# Listar assistentes
curl -s http://127.0.0.1:5004/api/demos/assistants

# Criar conversa
curl -s -X POST http://127.0.0.1:5004/api/demos/conversations \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"juridico"}'

# Enviar mensagem
curl -s -X POST http://127.0.0.1:5004/api/demos/conversations/CONVERSATION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"content":"Olá"}'
```
