---
name: frontend-developer
description: Visão geral do frontend de demos do think-tars — React, Vite, UI de chat. Use para contexto geral; para cenários específicos use as skills granulares. Triggers: "frontend", "React", "Vite", "demos", "UI", "chat", "frontend developer".
---

# Skill: Frontend Developer (visão geral)

Guia de **visão geral** do frontend das demos dos assistentes de IA: SPA React + Vite, integração com a API de demos.

---

## 1. Stack e estrutura

- **React** 18, **Vite** 5.
- **Build:** `npm run build` → `frontend/dist`. Base URL: `/demos/`.
- **Dev:** `npm run dev` (Vite em outra porta). Proxy `/api` → Flask (ex.: `http://127.0.0.1:5004`).

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── public/
└── src/
    ├── main.jsx
    ├── App.jsx
    └── index.css
```

---

## 2. Skills granulares (use conforme o cenário)

| Cenário | Skill |
|---------|--------|
| Estrutura de pastas, App.jsx, index.css, variáveis CSS | **frontend-demos-structure** |
| Chamadas fetch à API (assistants, conversations, messages, upload-pdf) | **frontend-api-demos** |
| UI do chat (sidebar, seletor, upload PDF, mensagens, input, toast) | **frontend-ui-chat** |
| Build (npm run build) e servir (Flask /demos, Vite dev, proxy) | **frontend-build-serve** |

---

## 3. App de demos (resumo)

- **Seletor de assistente:** dropdown a partir de `GET /assistants`.
- **Upload PDF (opcional):** antes de iniciar conversa; `POST /upload-pdf` com FormData.
- **Iniciar / Nova conversa:** `POST /conversations` com `agent_id` opcional; guardar `conversation_id`.
- **Chat:** lista de mensagens (user/assistant), input, botão Enviar. Envio via `POST .../messages`; exibir `message` ou `error`.
- **Trocar assistente:** limpar conversa e mensagens; permitir novo `agent_id` e "Iniciar conversa".

---

## 4. Referências

- **Arquitetura:** skill **architecture-guide**, **architecture-overview**.
- **API:** skill **backend-developer**, **backend-api-demos**; `backend/routes.py`, `backend/services.py`.

---

## 5. Respostas

Responder em **português** ao usuário.
