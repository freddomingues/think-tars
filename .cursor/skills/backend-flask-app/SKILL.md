---
name: backend-flask-app
description: App Flask do think-tars — app/main.py, registro de blueprints, servir frontend em /demos, inicialização do assistente. Use ao alterar entrypoint HTTP ou registrar novos blueprints. Triggers: "app main", "Flask", "register blueprint", "servir demos", "entrypoint".
---

# Skill: App Flask (entrypoint)

Entrypoint HTTP do projeto: `app/main.py` — Flask, registro da API de demos, servir frontend em `/demos`, inicialização do assistente padrão.

---

## 1. Estrutura do app

- **Arquivo:** `app/main.py`
- **PYTHONPATH:** raiz do projeto adicionada ao `sys.path` no início.
- **Config e logging:** `config.settings`, `config.logging_config` (setup_logging, log_tool_call, log_error).

---

## 2. Inicialização

- **`initialize_application()`:** chama `create_or_get_assistant_from_registry(DEFAULT_AGENT_ID)` e guarda em `ASSISTANT_ID`. Se falhar, encerra o processo.
- **Rota `/`:** mensagem de boas-vindas + link para `/demos/`.

---

## 3. API de demos e frontend

- **Blueprint de demos:** `from backend.routes import register_demo_routes` → `register_demo_routes(app)`. Registra rotas em `/api/demos` e CORS para `/api/demos/*`.
- **Frontend em `/demos`:** se existir `frontend/dist`, registra:
  - `GET /demos` e `GET /demos/` → `index.html`
  - `GET /demos/<path>` → arquivo estático ou `index.html` (SPA).
- Se `frontend/dist` não existir, apenas log de aviso (rodar `cd frontend && npm run build`).

---

## 4. Rotas legadas (API de tools)

- `POST /api/tools/search_contracts` e `POST /api/tools/search_faqs` — usam Chroma/Pinecone; podem ser migradas para uso apenas via assistentes no futuro.

---

## 5. Como adicionar novo blueprint

1. Criar módulo (ex.: `backend/outro.py`) com Blueprint e rotas.
2. Em `app/main.py`: `from backend.outro import register_outro_routes` e `register_outro_routes(app)` (ou `app.register_blueprint(bp)`).
3. Documentar em **backend-new-route** ou nesta skill se for rota de demos.

---

## 6. Referências

- **Rotas de demos:** skill **backend-api-demos**.
- **Servir build:** skill **frontend-build-serve**.

---

## 7. Respostas

Responder em **português** ao usuário.
