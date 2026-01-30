# Webhook Z-API local (ngrok)

Para o SDR responder quando você envia mensagem **do seu WhatsApp** para o número da empresa (554187497364), a Z-API precisa chamar o seu backend. Localmente isso é feito com **ngrok** (o script não usa mais cloudflared nem pede "Enter").

---

## Resumo em 3 passos

| # | Onde | O que fazer |
|---|------|-------------|
| 1 | **Terminal 1** | `python app/main.py` (deixe rodando) |
| 2 | **Terminal 2** | `./scripts/run_webhook_local.sh` → tunnel sobe e mostra uma URL. Se ngrok crashar, use `--lt` ou `--localhost-run` (ver abaixo). |
| 3 | **Painel Z-API** | Webhook **URL:** `https://abc123.ngrok-free.app/api/zapi/webhook` | **Evento:** ao receber mensagem → Salvar |

Depois envie uma mensagem do seu WhatsApp para 554187497364 e você deve receber a resposta do SDR.

Se o ngrok não estiver instalado: [ngrok.com/download](https://ngrok.com/download) → depois `ngrok config add-authtoken SEU_TOKEN`.

**Se o ngrok crashar no seu Mac** (erro Go / runtime asm_amd64):

- **Opção A — localtunnel** (precisa Node/npx):
  ```bash
  ./scripts/run_webhook_local.sh --lt
  ```
  Copie a URL exibida (ex.: `https://xxx.loca.lt`) e na Z-API use: `https://xxx.loca.lt/api/zapi/webhook`.

- **Opção B — localhost.run** (só ssh, nada a instalar):
  ```bash
  ./scripts/run_webhook_local.sh --localhost-run
  ```
  Copie a URL exibida e na Z-API use: `https://<URL>/api/zapi/webhook`.

---

## Rodar com ngrok (detalhes)

### 0. Credenciais Z-API no `.env`

Para o backend **enviar** a resposta de volta pelo WhatsApp, configure no `.env` (copie do painel da Z-API):

```env
ZAPI_INSTANCE_ID=seu_instance_id
ZAPI_TOKEN_INSTANCE=seu_token
```

Se a Z-API retornar **"your client-token is not configured"** (400), adicione também o token de segurança da conta:

```env
ZAPI_CLIENT_TOKEN=seu_client_token
```

O Client-Token fica no painel da Z-API em **Segurança** / **Token da conta** ([documentação](https://developer.z-api.io/en/security/client-token)). Depois reinicie o Flask.

Se esses valores estiverem vazios ou incorretos, o SDR até gera a resposta, mas `send_text` falha e você vê `sent_via_zapi: false` ou erro 400 e não recebe nada no WhatsApp.

### 1. Terminal 1 — Subir o backend

```bash
cd /caminho/do/generative-ai
source venv/bin/activate   # ou: . venv/bin/activate
python app/main.py
```

Deixe esse terminal aberto. O Flask sobe em **http://127.0.0.1:5004**.

### 2. Terminal 2 — Expor a porta com ngrok

Abra **outro** terminal no mesmo projeto:

```bash
cd /caminho/do/generative-ai
./scripts/run_webhook_local.sh
```

- Se tiver **ngrok** instalado: ele vai abrir o tunnel e mostrar uma URL, por exemplo:
  - `https://abc123.ngrok-free.app` (ou `https://xxxx.ngrok.io`)
- Se pedir authtoken: crie conta em [ngrok.com](https://ngrok.com), depois:
  - `ngrok config add-authtoken SEU_TOKEN`
- **Copie a URL que aparecer** (só a base, ex.: `https://abc123.ngrok-free.app`).

### 3. Configurar o webhook na Z-API

1. Acesse o **painel da Z-API** (onde você gerencia a instância do WhatsApp).
2. Procure a opção de **Webhook** / **URL de retorno** / **Callbacks**.
3. Configure:
   - **URL:** `https://SUA-URL-DO-NGROK/api/zapi/webhook`  
     Exemplo: `https://abc123.ngrok-free.app/api/zapi/webhook`
   - **Evento:** ao receber mensagem (on-message-received / message-received).
4. Salve.

### 4. Testar no WhatsApp

1. No **seu** celular, abra o WhatsApp.
2. Envie uma mensagem **para** o número da empresa (554187497364), por exemplo: *"Olá, quero saber sobre IA"*.
3. A Z-API recebe essa mensagem, envia um POST para a URL do ngrok → seu Flask processa com o SDR → o Flask chama a Z-API para enviar a resposta → você deve receber a resposta no WhatsApp.

Se nada chegar:

- **Terminal 1 (Flask):** veja se apareceu algum log de "Webhook Z-API" ou "SDR: mensagem de...". Se não aparecer nada, a Z-API não está chamando a URL (confira a URL no painel e se o ngrok está rodando).
- **Terminal 2 (ngrok):** deve mostrar as requisições HTTP quando a Z-API chamar.
- **Arquivo** `logs/zapi_webhook.log`: mostra payload recebido e se a resposta foi enviada (`sent: true/false`). Se `sent: false`, confira `ZAPI_INSTANCE_ID` e `ZAPI_TOKEN_INSTANCE` no `.env`.

### 5. Ver os logs

- **Console (Flask):** cada POST no webhook e o resultado do parse/resposta.
- **Arquivo:** `logs/zapi_webhook.log` — payload completo, telefone, texto e se a resposta foi enviada.

Se o SDR não responder:

1. Abra `logs/zapi_webhook.log` e veja o último `webhook_received`: é o JSON que a Z-API enviou.
2. Se aparecer `webhook_parse_failed`, o parser não achou telefone/texto; ajuste `external_services/zapi_client.parse_webhook_message` para as chaves do payload.
3. Se aparecer `webhook_parsed` e depois `webhook_reply` com `sent: false`, o problema é no envio (Z-API: confira instance id e token no `.env`).

## Sem tunnel (apenas teste local)

Para testar o fluxo SDR **sem** receber callbacks da Z-API:

```bash
# Use aspas SIMPLES no JSON; no zsh, aspas duplas fazem $55 virar "parâmetro 55" e geram "zsh: number expected"
curl -X POST http://127.0.0.1:5004/api/zapi/test-webhook \
  -H "Content-Type: application/json" \
  -d '{"phone":"5514998309606","message":"Olá, quero saber sobre IA"}'
```

Isso processa com o SDR e envia a resposta via Z-API para o número informado. Troque o `phone` pelo seu número (com DDI 55) para receber a resposta no WhatsApp.

Se a resposta for `{"error":"run_sdr_turn retornou None","phone":"..."}`:

1. Veja o **terminal do Flask**: agora há logs indicando se falhou em `get_or_create_sdr_thread`, `_get_sdr_assistant_id` ou em `run_turn` (status do run ou "nenhuma mensagem do assistente").
2. Confirme que `OPENAI_API_KEY` está definida no ambiente (ou no `.env`).
3. Se aparecer `run status failed`, verifique créditos/modelo da OpenAI.
