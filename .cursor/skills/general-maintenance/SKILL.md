---
name: general-maintenance
description: Manutenção geral da aplicação — estrutura, debugging, testes, troubleshooting. Use para entender a aplicação como um todo, resolver problemas gerais ou fazer melhorias estruturais. Triggers: "bug geral", "não funciona", "estrutura", "debug", "teste", "troubleshooting".
---

# Skill: Manutenção Geral da Aplicação

Visão geral da aplicação, debugging, testes e troubleshooting.

---

## 1. Estrutura Geral

### Camadas da Aplicação

1. **Entrypoint:** `app/main.py` - Flask app, rotas raiz, registro de blueprints
2. **Backend:** `backend/` - APIs, serviços, webhooks
3. **Frontend:** `frontend/` - React SPA, site e Playground
4. **AI:** `ai/` - Agentes, prompts, tools, manager
5. **Config:** `config/` - Settings, logging, agents
6. **Scripts:** `scripts/` - Utilitários, testes, updates

### Fluxo de Dados

```
Cliente (Browser)
    ↓
Frontend (React)
    ↓
Backend API (/api/demos/*)
    ↓
Services (backend/services.py)
    ↓
AI Manager (ai/assistant_manager.py)
    ↓
OpenAI Assistant API
    ↓
Tools (ai/tools/)
    ↓
Resposta → Cliente
```

---

## 2. Comandos Úteis

### Desenvolvimento Local

```bash
# Subir aplicação
python app/main.py

# Buildar frontend
cd frontend && npm install && npm run build && cd ..

# Testar agentes
python scripts/test_agents.py

# Atualizar assistente
python scripts/update_assistant.py
```

### Verificar Estrutura

```bash
# Verificar se frontend/dist existe
ls -la frontend/dist

# Verificar Procfile
cat Procfile

# Verificar requirements
cat requirements.txt
```

---

## 3. Debugging

### Logs Locais

```bash
# Subir com logs
python app/main.py
```

### Verificar Variáveis de Ambiente

```python
from config.settings import OPENAI_API_KEY, PINECONE_API_KEY

# Verificar se estão configuradas (sem mostrar valores)
print(f"OPENAI_API_KEY: {'✓' if OPENAI_API_KEY else '✗'}")
print(f"PINECONE_API_KEY: {'✓' if PINECONE_API_KEY else '✗'}")
```

### Testar Endpoints

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

### Verificar Frontend

```bash
# Build local
cd frontend && npm run build

# Servir localmente (após build)
cd .. && python app/main.py
# Acessar http://localhost:5004/
```

---

## 4. Problemas Comuns

### Frontend não aparece

1. Verificar se `frontend/dist` existe
2. Verificar se build foi executado
3. Verificar logs do backend
4. Verificar `vite.config.js` (base URL)

### Agente não funciona

1. Verificar se agente está no registry (`ai/agents.py`)
2. Verificar se prompt existe (`ai/prompts/`)
3. Verificar se tools existem (`ai/tools/`)
4. Testar carregamento: `python scripts/test_agents.py`

### API retorna erro

1. Verificar logs do backend
2. Verificar variáveis de ambiente
3. Verificar se endpoint existe
4. Verificar payload da requisição

### Deploy falha

1. **Usar MCP do Render para diagnosticar:**
   - `mcp_render_list_services()` - Identificar service ID
   - `mcp_render_list_logs(resource=[service_id])` - Verificar logs de build e runtime
   - `mcp_render_get_service(serviceId=service_id)` - Verificar configuração
2. Verificar Build Command no Render (via MCP ou painel)
3. Verificar logs de build (via MCP: filtrar por `type=['build']`)
4. Verificar Procfile
5. Verificar variáveis de ambiente

---

## 5. Testes

### Testar Agentes

```bash
python scripts/test_agents.py
```

### Testar Localmente

1. Subir backend: `python app/main.py`
2. Buildar frontend: `cd frontend && npm run build && cd ..`
3. Acessar: `http://localhost:5004/`
4. Testar Playground
5. Testar upload de arquivo
6. Testar diferentes agentes

### Testar Webhook SDR

```bash
# Ver skill testing-local-backend
bash scripts/test_sdr_webhook.sh
```

---

## 6. Melhorias Estruturais

### Adicionar Nova Feature

1. **Backend:** Adicionar rota em `backend/routes.py` ou criar novo blueprint
2. **Frontend:** Adicionar componente/seção em `frontend/src/App.jsx`
3. **Estilos:** Adicionar CSS em `frontend/src/index.css`
4. **Testar:** Testar localmente antes de fazer deploy

### Refatorar Código

1. Verificar se não quebra funcionalidades existentes
2. Manter isolamento de agentes
3. Manter estrutura de pastas
4. Atualizar documentação se necessário

---

## 7. Documentação

### Arquivos de Documentação

- **`AGENTS.md`** - Instruções para agentes de IA, estrutura, regras
- **`docs/ARCHITECTURE.md`** - Arquitetura detalhada
- **`docs/COMO_USAR_DEMOS.md`** - Guia de uso
- **`docs/CONFIGURAR_RENDER.md`** - Guia de deploy no Render
- **`.cursor/skills/`** - Skills para manutenção

### Atualizar Documentação

Ao fazer mudanças significativas:
1. Atualizar `AGENTS.md` se mudar estrutura de agentes
2. Atualizar `docs/ARCHITECTURE.md` se mudar arquitetura
3. Criar/atualizar skills se necessário

---

## 8. Checklist de Manutenção

### Antes de Fazer Mudanças

- [ ] Entender estrutura atual
- [ ] Verificar documentação relevante
- [ ] Testar funcionalidade atual
- [ ] Fazer backup (commit) se necessário

### Durante Desenvolvimento

- [ ] Seguir padrões do projeto
- [ ] Manter isolamento de agentes
- [ ] Não hardcodar credenciais
- [ ] Adicionar logging quando necessário
- [ ] Tratar erros adequadamente

### Após Mudanças

- [ ] Testar localmente
- [ ] Verificar logs
- [ ] Testar diferentes cenários
- [ ] Atualizar documentação se necessário
- [ ] Fazer commit com mensagem clara

---

## 9. Referências

- **Arquitetura:** `docs/ARCHITECTURE.md`
- **Agentes:** `AGENTS.md`
- **Deploy:** `docs/CONFIGURAR_RENDER.md`
- **Skills:** `.cursor/skills/`

---

## 10. Contato

- **Comercial:** +55 41 8749-7364
- **Repositório:** GitHub (ver URL no Render)
