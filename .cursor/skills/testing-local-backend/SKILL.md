---
name: testing-local-backend
description: Testes locais do backend — como rodar o Flask, testar webhook Z-API/SDR, Playground e novas implementações. Use após novas implementações no backend para validar localmente. Triggers: "testar local", "teste local", "rodar testes", "webhook SDR", "test SDR", "curl webhook".
---

# Skill: Testes locais do backend

Guia para **testar o backend localmente** sempre que houver nova implementação (webhook Z-API, SDR, rotas de demos, etc.).

---

## 1. Subir o backend

```bash
# Na raiz do projeto (com PYTHONPATH/venv ok)
python app/main.py
```

- Servidor sobe em **http://127.0.0.1:5004** (ou porta configurada).
- Logs aparecem no terminal; erros de import ou config quebram a subida.

---

## 2. Testar o webhook SDR (sem Z-API chamar o servidor)

O endpoint **POST /api/zapi/test-webhook** simula uma mensagem recebida: processa com o SDR e envia a resposta via Z-API para o número informado.

### Via curl

```bash
curl -X POST http://127.0.0.1:5004/api/zapi/test-webhook \
  -H "Content-Type: application/json" \
  -d '{"phone":"554187497364","message":"Olá, quero saber sobre automação"}'
```

- **phone:** número com DDI (ex.: 554187497364).
- **message:** texto da “mensagem do cliente”.
- Resposta esperada: `{ "ok": true, "phone": "...", "reply_preview": "...", "sent_via_zapi": true }`.
- Se `run_sdr_turn` falhar: 502 com `reply` None; se Z-API falhar: `sent_via_zapi: false`.

### Via script

```bash
chmod +x scripts/test_sdr_webhook.sh   # uma vez, se necessário
./scripts/test_sdr_webhook.sh 554187497364 "Olá, quero saber sobre IA"
```

Ou com variáveis de ambiente:

```bash
BASE_URL=http://127.0.0.1:5004 ./scripts/test_sdr_webhook.sh 5541999999999 "Teste"
```

---

## 3. Log de webhook (todas as mensagens SDR)

Todas as mensagens recebidas no **POST /api/zapi/webhook** são registradas em **`logs/zapi_webhook.log`** (um JSON por linha):

- `webhook_received` — payload completo recebido
- `webhook_parsed` — phone e text extraídos
- `webhook_parse_failed` — parse falhou (payload para ajustar o parser)
- `webhook_reply` — resposta enviada (sent: true/false, error se houver)

Use esse arquivo para ver exatamente o que a Z-API envia e debugar quando o SDR não responder.

## 4. Webhook local (Z-API chamar sua máquina)

Para receber callbacks da Z-API no seu PC:

1. **Terminal 1:** `python app/main.py`
2. **Terminal 2:** `./scripts/run_webhook_local.sh` (usa ngrok ou cloudflared)
3. Configure na Z-API a URL exibida pelo tunnel + `/api/zapi/webhook`
4. Envie mensagem do seu WhatsApp para o número da empresa e confira `logs/zapi_webhook.log`

Ver **`docs/WEBHOOK_LOCAL.md`** para o passo a passo completo.

## 5. Se o SDR não responder no WhatsApp

1. **Ver `logs/zapi_webhook.log`:** o último `webhook_received` mostra o JSON que a Z-API enviou. Se houver `webhook_parse_failed`, o parser não reconheceu; ajuste **`external_services/zapi_client.parse_webhook_message`** para as chaves desse payload.
2. **Webhook acessível:** em localhost a Z-API não alcança o servidor; use tunnel (ngrok/cloudflared) e configure essa URL na Z-API. Em produção, use a URL pública do backend.
3. **Testar parse localmente:** envie POST para **/api/zapi/webhook** com um JSON igual ao que aparece em `webhook_received` e veja se passa a dar `webhook_parsed` e `webhook_reply`.

---

## 6. Testar API do Playground (demos)

```bash
# Listar assistentes
curl -s http://127.0.0.1:5004/api/demos/assistants | python3 -m json.tool

# Criar conversa
curl -s -X POST http://127.0.0.1:5004/api/demos/conversations \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"juridico"}' | python3 -m json.tool

# Enviar mensagem (substituir CONVERSATION_ID)
curl -s -X POST http://127.0.0.1:5004/api/demos/conversations/CONVERSATION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"content":"Olá"}' | python3 -m json.tool
```

---

## 7. Checklist após nova implementação no backend

- [ ] Subir o app: `python app/main.py` (sem erro de import/config).
- [ ] Se mexeu em Z-API/SDR: rodar `./scripts/test_sdr_webhook.sh` ou curl em **/api/zapi/test-webhook** e conferir resposta e logs.
- [ ] Se mexeu em demos: testar **GET /api/demos/assistants** e, se aplicável, criar conversa e enviar mensagem.
- [ ] Ver logs no terminal (erros, "parse falhou", "run_sdr_turn retornou None", "falha ao enviar via Z-API").

---

## 8. Referências

- **SDR / Z-API:** skill **sdr-zapi**; `backend/zapi_webhook.py`, `external_services/zapi_client.py`.
- **Payload Z-API:** `.cursor/skills/sdr-zapi/references/zapi-webhook-payload.md`.
- **API Playground:** skill **backend-api-demos**; `backend/routes.py`, `backend/services.py`.

---

## 9. Respostas

Responder em **português** ao usuário.
