# Configuração do Render.com para Think TARS

## 📋 Problema Identificado

O Render está tentando usar Poetry, mas o projeto usa `requirements.txt`. O build command atual só builda o frontend e não instala as dependências Python.

## ✅ Solução

### Build Command Correto

No painel do Render → Settings → **Build & Deploy** → **Build Command**:

```bash
pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..
```

Isso irá:
1. Instalar todas as dependências Python (incluindo gunicorn)
2. Instalar dependências do frontend
3. Buildar o frontend

### Start Command

Deixe **vazio** (o Render usa o `Procfile` automaticamente) OU configure manualmente:

```
gunicorn --bind 0.0.0.0:$PORT app.main:app
```

### Root Directory

Deixe **vazio** (o Procfile está na raiz do projeto)

### Environment

**Environment:** Python 3

### Variáveis de Ambiente

Adicione todas as variáveis do seu `.env`:

- `OPENAI_API_KEY` - Sua chave da OpenAI
- `PINECONE_API_KEY` - Chave do Pinecone
- `PINECONE_ENVIRONMENT` - Ambiente do Pinecone (ex: us-east-1)
- `PINECONE_INDEX_NAME` - Nome do índice (ex: genai-documents)
- `ZAPI_INSTANCE_ID` - ID da instância Z-API
- `ZAPI_TOKEN_INSTANCE` - Token da instância Z-API
- `ZAPI_CLIENT_TOKEN` - Token de segurança (se necessário)
- `SDR_WHATSAPP_NUMBER` - Número do WhatsApp do SDR

---

## 🔧 Passo a Passo no Render

### 1. Acessar Configurações

1. Acesse: https://dashboard.render.com
2. Vá para o serviço `think-tars`
3. Clique em **Settings**

### 2. Atualizar Build Command

1. Role até **Build & Deploy**
2. No campo **Build Command**, substitua por:

```bash
pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..
```

3. Clique em **Save Changes**

### 3. Verificar Start Command

1. No campo **Start Command**, deixe **vazio** (usa o Procfile)
2. OU configure manualmente: `gunicorn --bind 0.0.0.0:$PORT app.main:app`

### 4. Fazer Novo Deploy

1. Vá para a aba **Manual Deploy**
2. Clique em **Deploy latest commit**
3. Aguarde o build e deploy completarem

---

## 🚨 Problemas Comuns

### Problema 1: "gunicorn: command not found"

**Causa:** Dependências Python não foram instaladas durante o build

**Solução:**
1. Verifique se o **Build Command** inclui `pip install -r requirements.txt`
2. Certifique-se de que `requirements.txt` está na raiz do projeto
3. Faça um novo deploy

### Problema 2: "frontend/dist não encontrado"

**Causa:** Frontend não foi buildado durante o deploy

**Solução:**
1. Verifique se o **Build Command** inclui `cd frontend && npm install && npm run build`
2. Verifique os logs de build no Render
3. Certifique-se de que Node.js está disponível

### Problema 3: "Endpoint não encontrado" ao acessar a raiz

**Causa:** Frontend não foi buildado ou rota não configurada

**Solução:**
1. Verifique se `frontend/dist` existe após o build
2. Verifique os logs do Render para ver se o build foi bem-sucedido
3. Certifique-se de que a rota `/` está servindo o frontend

### Problema 4: Render detecta Poetry mas não instala dependências

**Causa:** Render detecta Poetry automaticamente, mas o projeto usa `requirements.txt`

**Solução:**
1. Adicione `pip install -r requirements.txt` no início do **Build Command**
2. Isso força a instalação das dependências Python antes do build do frontend

---

## ✅ Checklist de Deploy

- [ ] Build Command inclui `pip install -r requirements.txt`
- [ ] Build Command inclui build do frontend (`cd frontend && npm install && npm run build`)
- [ ] Start Command vazio (usa Procfile) OU configurado manualmente
- [ ] Todas as variáveis de ambiente adicionadas
- [ ] Root Directory vazio
- [ ] Procfile na raiz do projeto
- [ ] `vite.config.js` com `base: '/'`
- [ ] Frontend buildado localmente para testar (`cd frontend && npm run build`)
- [ ] Domínio customizado configurado (se aplicável)
- [ ] DNS configurado na Hostinger (se aplicável)

---

## 🔄 Após o Deploy

1. **Verificar Logs:**
   - No painel do Render → **Logs**
   - Procure por "✅ Frontend estático configurado"
   - Procure por "Starting gunicorn" (não "gunicorn: command not found")

2. **Testar a Aplicação:**
   - Acesse a URL do Render
   - Deve abrir o site diretamente (não a mensagem de texto)
   - Teste o Playground
   - Teste as rotas de API

3. **Verificar Build:**
   - Nos logs, procure por "Installing collected packages: ... gunicorn"
   - Procure por "Build do frontend concluído"
   - Verifique se não há erros de build

---

## 📚 Recursos

- [Render Docs - Build & Deploy](https://render.com/docs/build-and-deploy)
- [Render Docs - Environment Variables](https://render.com/docs/environment-variables)
- [Render Docs - Custom Domains](https://render.com/docs/custom-domains)

---

**Última atualização:** 2024
