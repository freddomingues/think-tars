---
name: sdr-zapi
description: Assistente SDR no WhatsApp via Z-API — webhook, envio de mensagem, agente interno. Use ao alterar fluxo SDR, payload Z-API ou ferramentas do SDR. Triggers: "SDR", "Z-API", "WhatsApp", "webhook Z-API", "agente interno", "schedule_meeting".
---

# Skill: SDR e Z-API (WhatsApp — uso interno)

Referência para o **assistente SDR** integrado ao WhatsApp via **Z-API**: agente de uso interno (não aparece no Playground), webhook de mensagens recebidas e envio de respostas.

---

## 1. Visão geral

- **SDR:** Agente que atende leads vindos do site no WhatsApp. Objetivo: qualificar, tirar dúvidas, fechar para reunião com especialista (IA ou automação).
- **Z-API:** Ferramenta de integração WhatsApp. Webhook recebe mensagens; API envia respostas.
- **Uso interno:** O agente SDR **não** está listado no Playground; está em `INTERNAL_AGENTS_REGISTRY` em `ai/agents.py`.

---

## 2. Onde está cada coisa

| Objetivo | Onde |
|----------|------|
| Registry do SDR (interno) | `ai/agents.py` — `INTERNAL_AGENTS_REGISTRY` (id: `sdr`). |
| Instruções do SDR | `ai/prompts/sdr.py` — `SDR_ASSISTANT_INSTRUCTIONS`. |
| Tools do SDR | `ai/tools/sdr.py` — `TOOLS_DEFINITION` (schedule_meeting); implementação em `schedule_meeting()`. |
| Cliente Z-API (enviar mensagem) | `external_services/zapi_client.py` — `send_text(phone, message)`, `parse_webhook_message(payload)`. |
| Config Z-API | `config/settings.py` — `ZAPI_BASE_URL`, `ZAPI_INSTANCE_ID`, `ZAPI_TOKEN_INSTANCE`. |
| Serviços SDR (thread por telefone, run_turn) | `backend/sdr_services.py` — `get_or_create_sdr_thread(phone)`, `run_sdr_turn(phone, user_message)`. |
| Webhook Z-API | `backend/zapi_webhook.py` — `POST /api/zapi/webhook`. |
| Registro do webhook | `app/main.py` — `app.register_blueprint(zapi_bp)`. |
| **Log de todas as mensagens** | `logs/zapi_webhook.log` — cada POST recebido (payload), parse (phone, text) e reply (sent/erro). Gerado por `backend/webhook_logger.py`. |
| Webhook local (tunnel) | `scripts/run_webhook_local.sh` + ngrok/cloudflared; ver `docs/WEBHOOK_LOCAL.md`. |

---

## 3. Fluxo (mensagem recebida)

1. Z-API envia `POST /api/zapi/webhook` com o payload da mensagem recebida.
2. `parse_webhook_message(payload)` extrai `(phone, text)`; ignora mensagens `fromMe`.
3. `run_sdr_turn(phone, text)` obtém/cria thread para o telefone, chama `run_turn` do agente SDR com `allowed_tool_names` (schedule_meeting).
4. Resposta do SDR é enviada via `send_text(phone, reply)` (Z-API).

---

## 4. Tool do SDR: schedule_meeting

- **Nome:** `schedule_meeting`.
- **Parâmetros:** `lead_name`, `lead_phone`, `interest`, `preferred_schedule` (opcional), `notes` (opcional).
- **Implementação:** `ai/tools/sdr.schedule_meeting()` — por ora retorna mensagem de confirmação; pode integrar com CRM/calendário depois.
- **Registro:** `ai/tools/base.py` — `AVAILABLE_FUNCTIONS["schedule_meeting"]`.

---

## 5. Configuração Z-API

- **.env:** `ZAPI_INSTANCE_ID`, `ZAPI_TOKEN_INSTANCE`, `ZAPI_BASE_URL` (opcional; default `https://api.z-api.io`).
- **Z-API Dashboard:** Configurar a URL do webhook para `https://seu-dominio/api/zapi/webhook` e o evento "Ao receber mensagem" (on-message-received).

---

## 6. Alterar o SDR

- **Mudar instruções:** editar `ai/prompts/sdr.py`.
- **Nova tool:** adicionar em `ai/tools/sdr.py` (TOOLS_DEFINITION + função), registrar em `ai/tools/base.py` e em `get_agent_tool_names` (SDR já usa o registry).
- **Mudar payload do webhook:** ajustar `parse_webhook_message` em `external_services/zapi_client.py` conforme a documentação Z-API.

---

## 7. Referências

- **Z-API:** https://developer.z-api.io/ (webhooks, envio de texto).
- **Playground vs interno:** skill **architecture-registries**, **AGENTS.md**.

---

## 8. Respostas

Responder em **português** ao usuário.
