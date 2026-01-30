# Uso da API de demos no frontend

## Fluxo típico

1. **Carregar assistentes:** `GET /api/demos/assistants` → preencher dropdown.
2. **Iniciar conversa:** `POST /api/demos/conversations` com `{ agent_id }` → guardar `conversation_id`.
3. **Enviar mensagem:** `POST /api/demos/conversations/:id/messages` com `{ content }` → exibir `message` ou `error`.

## Exemplo (fetch)

```js
const res = await fetch('/api/demos/assistants');
const { assistants } = await res.json();

const create = await fetch('/api/demos/conversations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ agent_id: 'juridico' }),
});
const { conversation_id } = await create.json();

const msg = await fetch(`/api/demos/conversations/${conversation_id}/messages`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ content: 'Olá!' }),
});
const { message, error } = await msg.json();
```

## Tratamento de erros

- `!res.ok`: verificar `res.status` e corpo `{ error }`.
- 502: `{ error }` com mensagem do run do assistente.
