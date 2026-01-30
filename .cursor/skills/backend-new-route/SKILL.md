---
name: backend-new-route
description: Como adicionar nova rota ou serviço no backend do generative-ai — blueprint demos vs novo blueprint, onde colocar lógica. Use ao criar nova funcionalidade HTTP no backend. Triggers: "nova rota", "novo endpoint", "adicionar rota", "novo serviço backend".
---

# Skill: Adicionar nova rota ou serviço (backend)

Passos para **adicionar uma nova rota ou serviço** no backend do generative-ai.

---

## 1. Decidir onde colocar

- **Rota de demos (assistentes, conversas, mensagens, PDF):** em `backend/routes.py` no Blueprint existente (`bp`) e lógica em `backend/services.py`. Ver **backend-api-demos** e **backend-services-demos**.
- **Rota de outro domínio:** criar novo Blueprint em `backend/` (ou em `app/`) e registrar em `app/main.py`. Ver **backend-flask-app**.

---

## 2. Nova rota dentro da API de demos

1. **Serviço:** em `backend/services.py`, criar função que recebe parâmetros claros e retorna dict ou None (ex.: `get_conversation_info(conversation_id)`).
2. **Rota:** em `backend/routes.py`, novo `@bp.route("/caminho", methods=["GET","POST",...])` que chama a função de services e retorna `jsonify(...)` com códigos adequados (200, 201, 400, 404, 500).
3. **Contrato:** documentar em `.cursor/skills/backend-developer/references/api-demos.md` (e na skill **backend-api-demos**).
4. **Frontend:** se o frontend precisar consumir, atualizar chamadas (skill **frontend-api-demos**).

---

## 3. Novo Blueprint (outro prefixo)

1. Criar arquivo ex.: `backend/meu_modulo.py` com `bp = Blueprint("meu", __name__, url_prefix="/api/meu")` e rotas.
2. Em `app/main.py`: `from backend.meu_modulo import bp` e `app.register_blueprint(bp)`.
3. Se precisar de CORS, usar `flask_cors` no registro ou em `register_demo_routes` como referência.

---

## 4. Convenções

- Config e secrets em `config.settings`; nada hardcoded.
- Logging via `logging` ou `config.logging_config`.
- Respostas JSON; erros com mensagem clara e código HTTP adequado.
- Manter compatibilidade com frontend de demos quando alterar contratos existentes.

---

## 5. Referências

- **Endpoints atuais:** skill **backend-api-demos**.
- **Serviços atuais:** skill **backend-services-demos**.
- **Registro no Flask:** skill **backend-flask-app**.

---

## 6. Respostas

Responder em **português** ao usuário.
