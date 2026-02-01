---
name: backend-maintenance
description: Manutenção do backend Flask — rotas, serviços, blueprints, error handling, logging. Use ao adicionar novas rotas, corrigir bugs, melhorar serviços ou debug. Triggers: "nova rota", "endpoint não funciona", "erro backend", "Flask", "blueprint", "services".
---

# Skill: Manutenção do Backend Flask

Como manter, debugar e estender o backend Flask da aplicação.

---

## 1. Estrutura do Backend

### Arquivos Principais

- **`app/main.py`** - Entrypoint Flask, rotas raiz, registro de blueprints, servir frontend
- **`backend/routes.py`** - Rotas da API de demos (`/api/demos/*`)
- **`backend/services.py`** - Serviços de negócio (list_assistants, create_conversation, send_message)
- **`backend/sdr_services.py`** - Serviços do SDR WhatsApp
- **`backend/zapi_webhook.py`** - Webhook Z-API (POST `/api/zapi/webhook`)

---

## 2. Adicionar Nova Rota

### Opção A: Rota na API de Demos

1. Adicionar rota em `backend/routes.py`:

```python
@bp.route('/nova-rota', methods=['GET', 'POST'])
def nova_rota():
    # Lógica aqui
    return jsonify({"status": "ok"})
```

2. A rota estará disponível em `/api/demos/nova-rota`

### Opção B: Rota Global

1. Adicionar em `app/main.py`:

```python
@app.route('/nova-rota', methods=['GET', 'POST'])
def nova_rota():
    # Lógica aqui
    return jsonify({"status": "ok"})
```

2. A rota estará disponível em `/nova-rota`

### Opção C: Novo Blueprint

1. Criar arquivo `backend/novo_blueprint.py`:

```python
from flask import Blueprint, jsonify

bp = Blueprint('novo_blueprint', __name__)

@bp.route('/rota', methods=['GET'])
def rota():
    return jsonify({"status": "ok"})
```

2. Registrar em `app/main.py`:

```python
from backend.novo_blueprint import bp as novo_bp
app.register_blueprint(novo_bp, url_prefix='/api/novo')
```

---

## 3. Error Handling

### Handler Global (app/main.py)

```python
@app.errorhandler(404)
def not_found(error):
    """Para rotas de API, retorna JSON. Para outras, tenta servir frontend."""
    if request.path.startswith('/api/'):
        return jsonify({"error": "Endpoint não encontrado"}), 404
    # Fallback para SPA
    if frontend_dist_exists():
        return send_from_directory(get_frontend_dist_path(), "index.html")
    return jsonify({"error": "Endpoint não encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.exception("Erro interno do servidor")
    return jsonify({"error": "Erro interno do servidor"}), 500
```

### Error Handling em Rotas

```python
@bp.route('/rota', methods=['POST'])
def rota():
    try:
        # Lógica aqui
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.exception(f"Erro em rota: {e}")
        return jsonify({"error": str(e)}), 500
```

---

## 4. Logging

### Configuração

- **Arquivo:** `config/logging_config.py`
- **Função:** `setup_logging()` - Configura logging global
- **Funções:** `log_tool_call()`, `log_error()` - Helpers para logging

### Uso

```python
from config.logging_config import setup_logging

logger = setup_logging()

logger.info("Mensagem informativa")
logger.warning("Aviso")
logger.error("Erro")
logger.exception("Erro com traceback")
```

---

## 5. Servir Frontend

### Verificação Lazy

O código em `app/main.py` verifica se `frontend/dist` existe de forma lazy (apenas quando necessário):

```python
def frontend_dist_exists():
    """Verifica se frontend/dist existe e tem index.html."""
    dist_path = get_frontend_dist_path()
    return os.path.isdir(dist_path) and os.path.isfile(os.path.join(dist_path, "index.html"))
```

### Rotas do Frontend

- **`GET /`** - Serve `index.html` se `frontend/dist` existir
- **`GET /demos`** e **`GET /demos/`** - Serve `index.html`
- **`GET /demos/<path>`** - Serve arquivo estático ou `index.html` (SPA fallback)
- **`GET /assets/<path>`** - Serve assets (JS, CSS)

---

## 6. Integração com Agentes de IA

### Usar Serviços

```python
from backend.services import create_conversation, send_message

# Criar conversa
conversation = create_conversation(agent_id="juridico")

# Enviar mensagem
response = send_message(
    conversation_id=conversation["id"],
    message="Olá",
    agent_id="juridico"
)
```

### Upload de Arquivo

```python
from backend.routes import upload_file_to_openai

# Upload arquivo
file_id = upload_file_to_openai(file_bytes, filename)

# Enviar mensagem com arquivo
response = send_message(
    conversation_id=conversation["id"],
    message="Analise este arquivo",
    agent_id="planilha",
    file_ids=[file_id]
)
```

---

## 7. Debugging

### Logs Locais

```bash
# Subir aplicação com logs
python app/main.py
```

### Testar Rotas Localmente

```bash
# Health check
curl http://localhost:5004/

# Listar assistentes
curl http://localhost:5004/api/demos/assistants

# Criar conversa
curl -X POST http://localhost:5004/api/demos/conversations \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "juridico"}'
```

### Verificar Variáveis de Ambiente

```python
from config.settings import OPENAI_API_KEY, PINECONE_API_KEY

# Verificar se estão configuradas (não mostrar valores)
print(f"OPENAI_API_KEY configurada: {bool(OPENAI_API_KEY)}")
```

---

## 8. Boas Práticas

1. **Sempre retornar JSON em rotas de API**
2. **Usar logging para debug e monitoramento**
3. **Tratar erros com try/except e retornar códigos HTTP apropriados**
4. **Nunca hardcodar credenciais** - usar `config/settings.py`
5. **Validar entrada do usuário** antes de processar
6. **Usar blueprints para organizar rotas relacionadas**

---

## 9. Referências

- **Arquitetura:** `docs/ARCHITECTURE.md`
- **API de Demos:** `.cursor/skills/backend-api-demos/`
- **Serviços:** `.cursor/skills/backend-services-demos/`
- **Flask App:** `.cursor/skills/backend-flask-app/`
- **Nova Rota:** `.cursor/skills/backend-new-route/`
