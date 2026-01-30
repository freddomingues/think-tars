---
name: frontend-build-serve
description: Build e servir o frontend de demos do generative-ai — npm run build, Vite, proxy /api, Flask serve /demos. Use ao configurar deploy ou ambiente de desenvolvimento. Triggers: "build frontend", "npm run build", "servir demos", "Vite", "proxy".
---

# Skill: Build e servir o frontend de demos

Como **construir** o frontend e como ele é **servido** em desenvolvimento e produção.

---

## 1. Desenvolvimento (Vite)

- **Comando:** `cd frontend && npm install && npm run dev`.
- **Resultado:** servidor Vite em outra porta (ex.: 5173); hot reload.
- **Proxy:** configurar em `vite.config.js` para que `/api` seja encaminhado ao Flask (ex.: `http://127.0.0.1:5004`). Assim as chamadas `fetch('/api/demos/...')` funcionam sem CORS em dev.
- **Acesso:** abrir a URL do Vite (ex.: `http://localhost:5173/demos/` ou raiz conforme base).

---

## 2. Build de produção

- **Comando:** `cd frontend && npm install && npm run build`.
- **Saída:** diretório `frontend/dist` com `index.html` e assets (JS, CSS).
- **Base:** garantir que a base URL seja `/demos/` (configuração no Vite se necessário para recursos estáticos).

---

## 3. Servir em produção (Flask)

- **Arquivo:** `app/main.py`.
- **Condição:** se existir o diretório `frontend/dist`:
  - `GET /demos` e `GET /demos/` → `send_from_directory(_frontend_dist, "index.html")`.
  - `GET /demos/<path>` → se for arquivo, servir arquivo; senão servir `index.html` (SPA).
- **Sem build:** se `frontend/dist` não existir, apenas log de aviso; `/demos` não funciona até rodar o build.

---

## 4. Ordem de execução típica

1. Backend: `python app/main.py` (Flask na porta 5004).
2. Frontend (opção A — produção): rodar `cd frontend && npm run build` uma vez; acessar `http://...:5004/demos/`.
3. Frontend (opção B — dev): rodar `cd frontend && npm run dev`; configurar proxy para 5004; acessar URL do Vite.

---

## 5. Onde alterar

- **Base URL ou assets:** `vite.config.js` (base, build).
- **Regras de servir:** `app/main.py` (rotas `/demos`, `/demos/<path>`).
- **Proxy em dev:** `vite.config.js` (server.proxy).

---

## 6. Referências

- **Servir no Flask:** skill **backend-flask-app**.
- **Estrutura do frontend:** skill **frontend-demos-structure**.

---

## 7. Respostas

Responder em **português** ao usuário.
