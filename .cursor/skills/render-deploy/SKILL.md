---
name: render-deploy
description: Deploy e manutenção no Render.com — build commands, Procfile, variáveis de ambiente, troubleshooting, logs, MCP Render. Use ao configurar deploy, resolver problemas de build ou runtime, verificar logs via MCP. Triggers: "deploy render", "build command", "gunicorn not found", "frontend não buildado", "logs render", "analisar logs render", "verificar deploy".
---

# Skill: Deploy e Manutenção no Render.com

Como fazer deploy, configurar build commands, resolver problemas comuns e monitorar a aplicação no Render.

---

## 1. Configuração Básica

### Build Command (OBRIGATÓRIO)

No painel do Render → Settings → **Build & Deploy** → **Build Command**:

```bash
pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..
```

**Ordem importante:**
1. Instala dependências Python (incluindo gunicorn)
2. Instala dependências do frontend
3. Builda o frontend (gera `frontend/dist`)

### Start Command

Deixe **vazio** (usa o `Procfile`) OU configure:

```
gunicorn --bind 0.0.0.0:$PORT app.main:app
```

### Root Directory

Deixe **vazio** (o Procfile está na raiz)

### Environment

**Environment:** Python 3

---

## 2. Variáveis de Ambiente

Adicionar em **Settings** → **Environment**:

- `OPENAI_API_KEY` - Chave da OpenAI
- `PINECONE_API_KEY` - Chave do Pinecone
- `PINECONE_ENVIRONMENT` - Ambiente (ex: us-east-1)
- `PINECONE_INDEX_NAME` - Nome do índice
- `ZAPI_INSTANCE_ID` - ID da instância Z-API
- `ZAPI_TOKEN_INSTANCE` - Token da instância Z-API
- `ZAPI_CLIENT_TOKEN` - Token de segurança (se necessário)
- `SDR_WHATSAPP_NUMBER` - Número do WhatsApp do SDR

**NUNCA** hardcodar credenciais no código.

---

## 3. Procfile

Arquivo na raiz: `Procfile`

```
web: gunicorn --bind 0.0.0.0:$PORT app.main:app
```

**Importante:** Deve ter uma nova linha no final do arquivo.

---

## 4. Problemas Comuns e Soluções

### Diagnóstico Automático com MCP

**SEMPRE use MCP do Render para diagnosticar problemas antes de sugerir soluções:**

1. **Listar serviços e obter service ID:**
   ```python
   services = mcp_render_list_services()
   service_id = next(s['id'] for s in services if s['name'] == 'think-tars')
   ```

2. **Verificar logs recentes:**
   ```python
   logs = mcp_render_list_logs(
       resource=[service_id],
       limit=100,
       direction='backward'
   )
   ```

3. **Verificar configuração do serviço:**
   ```python
   service = mcp_render_get_service(serviceId=service_id)
   build_cmd = service['serviceDetails']['envSpecificDetails']['buildCommand']
   ```

### Problema: "gunicorn: command not found"

**Causa:** Dependências Python não foram instaladas durante o build

**Diagnóstico com MCP:**
1. Verificar logs de build para "Installing collected packages"
2. Verificar se Build Command inclui `pip install -r requirements.txt`
3. Verificar se há erros de instalação

**Solução:**
1. Verificar se o Build Command inclui `pip install -r requirements.txt`
2. Verificar se `requirements.txt` está na raiz
3. Fazer novo deploy

### Problema: "frontend/dist não encontrado"

**Causa:** Frontend não foi buildado durante o deploy

**Diagnóstico com MCP:**
1. Verificar logs de build para "✓ built in X.XXs"
2. Verificar se Build Command inclui `npm run build`
3. Verificar se há erros de build do frontend

**Solução:**
1. Verificar se o Build Command inclui `cd frontend && npm install && npm run build`
2. Verificar logs de build no Render (via MCP ou painel)
3. Certificar-se de que Node.js está disponível

### Problema: Render detecta Poetry mas não instala dependências

**Causa:** Render detecta Poetry automaticamente, mas o projeto usa `requirements.txt`

**Solução:**
1. Adicionar `pip install -r requirements.txt` no início do Build Command
2. Isso força a instalação das dependências Python antes do build do frontend

### Problema: "Endpoint não encontrado" ao acessar a raiz

**Causa:** Frontend não foi buildado ou rota não configurada

**Diagnóstico com MCP:**
1. Verificar logs de runtime para "✅ Frontend estático configurado"
2. Verificar logs de build para confirmação de build do frontend
3. Verificar se há erros 404 nos logs de request

**Solução:**
1. Verificar se `frontend/dist` existe após o build (via logs)
2. Verificar logs do Render (via MCP: `mcp_render_list_logs` com filtro `text=['Frontend estático']`)
3. Certificar-se de que a rota `/` está servindo o frontend (verificação lazy em `app/main.py`)

### Problema: Tela branca com mensagem de texto

**Causa:** Frontend não está sendo servido na raiz

**Diagnóstico com MCP:**
1. Verificar logs de runtime para "✅ Frontend estático configurado"
2. Verificar logs de build para "Build successful 🎉"
3. Verificar se há warnings sobre `frontend/dist` não encontrado

**Solução:**
1. Verificar se o build do frontend foi bem-sucedido (via MCP logs)
2. Verificar se `vite.config.js` tem `base: '/'`
3. Verificar logs do Render para "✅ Frontend estático configurado" (via MCP: `mcp_render_list_logs` com filtro `text=['Frontend estático']`)

---

## 5. Monitoramento e Logs

### Acessar Logs via MCP (Recomendado para Agentes de IA)

**Use as ferramentas MCP do Render para verificar logs e status programaticamente:**

1. **Listar serviços:**
   - `mcp_render_list_services` - Lista todos os serviços do workspace
   - Identificar o service ID (ex: `srv-d5veps14tr6s739loe7g`)

2. **Verificar logs:**
   - `mcp_render_list_logs(resource=['service_id'])` - Lista logs recentes
   - Filtrar por tipo: `type=['app', 'build']`
   - Filtrar por texto: `text=['gunicorn', 'frontend', 'error']`
   - Direção: `direction='backward'` (mais recentes primeiro)

3. **Verificar status do serviço:**
   - `mcp_render_get_service(serviceId='service_id')` - Detalhes do serviço
   - Verificar `serviceDetails.envSpecificDetails.buildCommand` e `startCommand`

4. **Verificar deploys:**
   - `mcp_render_list_deploys(serviceId='service_id')` - Lista deploys recentes
   - `mcp_render_get_deploy(serviceId='service_id', deployId='deploy_id')` - Detalhes de um deploy

5. **Verificar métricas:**
   - `mcp_render_get_metrics(resourceId='service_id', metricTypes=['cpu_usage', 'memory_usage'])` - Métricas de performance

### Acessar Logs via Painel

No painel do Render → **Logs**

### Logs Importantes

- **Build:** "Installing collected packages: ... gunicorn"
- **Build:** "✓ built in X.XXs" (frontend)
- **Build:** "Build successful 🎉"
- **Runtime:** "Starting gunicorn"
- **Runtime:** "✅ Frontend estático configurado"
- **Runtime:** "✅ API de demos (Playground) registrada em /api/demos"

### Verificar Status

1. **Build bem-sucedido:** Logs mostram "Build successful 🎉"
2. **Aplicação rodando:** Logs mostram "Starting gunicorn" (não "command not found")
3. **Frontend disponível:** Logs mostram "✅ Frontend estático configurado"

### Troubleshooting com MCP

**Quando o usuário reportar problemas, use MCP para diagnosticar:**

1. **Problema: "gunicorn: command not found"**
   ```python
   # Verificar logs de build
   logs = mcp_render_list_logs(
       resource=['srv-d5veps14tr6s739loe7g'],
       type=['build', 'app'],
       text=['gunicorn', 'pip install'],
       limit=50
   )
   # Procurar por "Installing collected packages: ... gunicorn"
   ```

2. **Problema: "frontend/dist não encontrado"**
   ```python
   # Verificar logs de build do frontend
   logs = mcp_render_list_logs(
       resource=['srv-d5veps14tr6s739loe7g'],
       text=['frontend', 'npm run build', 'dist'],
       limit=50
   )
   # Procurar por "✓ built in X.XXs"
   ```

3. **Problema: "Endpoint não encontrado"**
   ```python
   # Verificar logs de runtime
   logs = mcp_render_list_logs(
       resource=['srv-d5veps14tr6s739loe7g'],
       type=['app'],
       text=['404', 'Frontend estático', 'API de demos'],
       limit=30
   )
   ```

4. **Verificar configuração do serviço:**
   ```python
   service = mcp_render_get_service(serviceId='srv-d5veps14tr6s739loe7g')
   build_cmd = service['serviceDetails']['envSpecificDetails']['buildCommand']
   start_cmd = service['serviceDetails']['envSpecificDetails']['startCommand']
   # Verificar se build_cmd inclui "pip install -r requirements.txt"
   ```

---

## 6. Deploy Manual

1. Vá para **Manual Deploy**
2. Clique em **Deploy latest commit**
3. Aguarde build e deploy completarem
4. Verifique logs para erros

---

## 7. Domínio Customizado

### Configurar Domínio

1. Vá em **Settings** → **Custom Domains**
2. Clique em **Add Custom Domain**
3. Digite o domínio (ex: `thinktars.tech`)
4. Siga as instruções de DNS do Render
5. Configure DNS na Hostinger conforme instruções

**Guia completo:** Ver `docs/CONFIGURAR_DOMINIO_HOSTINGER.md` para passo a passo detalhado.

### Configuração DNS na Hostinger

**Para domínio raiz (`thinktars.tech`):**
- **Opção A (Recomendado):** `ALIAS` `@` → `think-tars.onrender.com`
- **Opção B:** `A` `@` → `216.24.57.1`

**Para subdomínio `www`:**
- `CNAME` `www` → `think-tars.onrender.com`

**Importante:**
- Remover registros antigos que apontam para `connect.hostinger.com`
- Manter registros CAA (certificados SSL)
- Aguardar propagação DNS (1-48 horas)

### HTTPS

- Render emite certificado SSL automaticamente
- Pode levar alguns minutos após configurar DNS e verificação
- Se não funcionar, verificar DNS e aguardar propagação
- Verificar status no Render Dashboard → Custom Domains

### Problema: "Certificate Error" com "Domain Verified"

**Sintomas:** Domínio verificado mas certificado SSL não é emitido.

**Causas:**
1. Registros CAA bloqueando Let's Encrypt
2. DNS ainda não propagou completamente
3. Registros CAA conflitantes

**Soluções:**
1. **Verificar registros CAA na Hostinger:**
   - Devem incluir `letsencrypt.org`
   - Adicionar: `CAA` `@` → `0 issue "letsencrypt.org"`

2. **Aguardar 1-2 horas** após verificação do domínio

3. **Verificar DNS:**
   ```bash
   dig CAA thinktars.tech
   dig thinktars.tech
   ```

4. **Se persistir:** Contatar suporte Render via link na mensagem de erro

**Guia completo:** Ver `docs/CONFIGURAR_DOMINIO_HOSTINGER.md` seção "Troubleshooting: Erro de Certificado SSL"

---

## 8. Checklist de Deploy

- [ ] Build Command inclui `pip install -r requirements.txt`
- [ ] Build Command inclui build do frontend
- [ ] Start Command vazio (usa Procfile) OU configurado
- [ ] Todas as variáveis de ambiente adicionadas
- [ ] Root Directory vazio
- [ ] Procfile na raiz com nova linha no final
- [ ] `vite.config.js` com `base: '/'`
- [ ] Frontend buildado localmente para testar
- [ ] Domínio customizado configurado (se aplicável)
- [ ] DNS configurado (se aplicável)

---

## 9. Uso do MCP do Render para Verificações Automáticas

### Workflow Recomendado

**Quando o usuário reportar problemas ou pedir verificação:**

1. **Identificar o serviço:**
   ```python
   services = mcp_render_list_services()
   service = next(s for s in services if s['name'] == 'think-tars')
   service_id = service['id']
   ```

2. **Verificar status atual:**
   ```python
   service = mcp_render_get_service(serviceId=service_id)
   # Verificar: suspended, buildCommand, startCommand
   ```

3. **Analisar logs recentes:**
   ```python
   logs = mcp_render_list_logs(
       resource=[service_id],
       limit=100,
       direction='backward',
       type=['app', 'build']
   )
   # Procurar por erros, warnings, mensagens de sucesso
   ```

4. **Verificar deploys recentes:**
   ```python
   deploys = mcp_render_list_deploys(serviceId=service_id, limit=5)
   latest_deploy = deploys[0] if deploys else None
   # Verificar status do deploy mais recente
   ```

5. **Verificar métricas (se necessário):**
   ```python
   metrics = mcp_render_get_metrics(
       resourceId=service_id,
       metricTypes=['cpu_usage', 'memory_usage'],
       startTime='2026-02-01T00:00:00Z',
       endTime='2026-02-01T23:59:59Z'
   )
   ```

### Exemplos de Uso

**Verificar se build foi bem-sucedido:**
```python
logs = mcp_render_list_logs(
    resource=[service_id],
    text=['Build successful', 'built in'],
    type=['app'],
    limit=20
)
# Procurar por "Build successful 🎉"
```

**Verificar se aplicação está rodando:**
```python
logs = mcp_render_list_logs(
    resource=[service_id],
    text=['Starting gunicorn', 'gunicorn: command not found'],
    type=['app'],
    limit=10
)
# Se encontrar "command not found", problema de dependências
```

**Verificar se frontend foi buildado:**
```python
logs = mcp_render_list_logs(
    resource=[service_id],
    text=['npm run build', 'built in', 'dist/'],
    type=['app'],
    limit=30
)
# Procurar por "✓ built in X.XXs"
```

---

## 10. Referências

- **Documentação:** `docs/CONFIGURAR_RENDER.md`
- **Procfile:** `Procfile`
- **Build Script:** `build.sh` (opcional)
- **Render Docs:** https://render.com/docs
- **MCP Render Tools:** Use `mcp_render_*` para verificações programáticas
- **Workflow MCP:** `.cursor/skills/render-deploy/references/mcp-workflow.md` - Guia completo de uso do MCP do Render

---

## 11. Comandos Úteis

### Testar Build Localmente

```bash
# Instalar dependências Python
pip install -r requirements.txt

# Buildar frontend
cd frontend && npm install && npm run build && cd ..

# Testar servidor local
python app/main.py
```

### Verificar Procfile

```bash
cat Procfile
# Deve mostrar: web: gunicorn --bind 0.0.0.0:$PORT app.main:app
```
