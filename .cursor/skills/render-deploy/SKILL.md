---
name: render-deploy
description: Deploy e manutenção no Render.com — build commands, Procfile, variáveis de ambiente, troubleshooting, logs. Use ao configurar deploy, resolver problemas de build ou runtime. Triggers: "deploy render", "build command", "gunicorn not found", "frontend não buildado", "logs render".
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

### Problema: "gunicorn: command not found"

**Causa:** Dependências Python não foram instaladas durante o build

**Solução:**
1. Verificar se o Build Command inclui `pip install -r requirements.txt`
2. Verificar se `requirements.txt` está na raiz
3. Fazer novo deploy

### Problema: "frontend/dist não encontrado"

**Causa:** Frontend não foi buildado durante o deploy

**Solução:**
1. Verificar se o Build Command inclui `cd frontend && npm install && npm run build`
2. Verificar logs de build no Render
3. Certificar-se de que Node.js está disponível

### Problema: Render detecta Poetry mas não instala dependências

**Causa:** Render detecta Poetry automaticamente, mas o projeto usa `requirements.txt`

**Solução:**
1. Adicionar `pip install -r requirements.txt` no início do Build Command
2. Isso força a instalação das dependências Python antes do build do frontend

### Problema: "Endpoint não encontrado" ao acessar a raiz

**Causa:** Frontend não foi buildado ou rota não configurada

**Solução:**
1. Verificar se `frontend/dist` existe após o build
2. Verificar logs do Render
3. Certificar-se de que a rota `/` está servindo o frontend (verificação lazy em `app/main.py`)

### Problema: Tela branca com mensagem de texto

**Causa:** Frontend não está sendo servido na raiz

**Solução:**
1. Verificar se o build do frontend foi bem-sucedido
2. Verificar se `vite.config.js` tem `base: '/'`
3. Verificar logs do Render para "✅ Frontend estático configurado"

---

## 5. Monitoramento e Logs

### Acessar Logs

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

### HTTPS

- Render emite certificado SSL automaticamente
- Pode levar alguns minutos após configurar DNS
- Se não funcionar, verificar DNS e aguardar propagação

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

## 9. Referências

- **Documentação:** `docs/CONFIGURAR_RENDER.md`
- **Procfile:** `Procfile`
- **Build Script:** `build.sh` (opcional)
- **Render Docs:** https://render.com/docs

---

## 10. Comandos Úteis

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
