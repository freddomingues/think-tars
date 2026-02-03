# Configuração do Google Calendar para SDR Agent

Este guia explica como configurar a integração do Google Calendar com o SDR Agent para gerenciar agendamentos automaticamente.

## Pré-requisitos

1. Conta Google (Gmail)
2. Acesso ao Google Cloud Console
3. Python 3.8+

## Passo 1: Criar Projeto no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Anote o **Project ID** do projeto

## Passo 2: Habilitar Google Calendar API

1. No Google Cloud Console, vá em **APIs & Services** > **Library**
2. Busque por "Google Calendar API"
3. Clique em **Enable** para habilitar a API

## Passo 3: Configurar OAuth Consent Screen

⚠️ **IMPORTANTE:** Este passo é obrigatório antes de criar as credenciais!

1. Vá em **APIs & Services** > **OAuth consent screen**
2. Escolha **External** (para uso pessoal/teste)
3. Preencha as informações obrigatórias:
   - **App name**: `tars-sdr-agent-wpp` (ou outro nome)
   - **User support email**: Seu email (ex: `tars.diretoria@gmail.com`)
   - **Developer contact information**: Seu email
4. Clique em **Save and Continue**
5. Na seção **Scopes**, clique em **Add or Remove Scopes**
   - Adicione: `https://www.googleapis.com/auth/calendar`
   - Clique em **Update** e depois **Save and Continue**
6. Na seção **Test users**, **ADICIONE SEU EMAIL**:
   - Clique em **Add Users**
   - Digite: `tars.diretoria@gmail.com` (ou o email que você vai usar)
   - Clique em **Add**
   - **Clique em "Save and Continue"** até finalizar
7. ⚠️ **CRÍTICO:** Certifique-se de que seu email está na lista de **Test users** antes de continuar!

## Passo 4: Criar Credenciais OAuth 2.0

1. Vá em **APIs & Services** > **Credentials**
2. Clique em **Create Credentials** > **OAuth client ID**
3. Se solicitado a configurar OAuth consent screen, volte ao Passo 3 acima
4. Crie o OAuth client ID:
   - **Application type**: Desktop app
   - **Name**: Think TARS Calendar Client (ou `tars-sdr-agent-wpp`)
5. Clique em **Create**
6. Baixe o arquivo JSON de credenciais (clique no ícone de download)
7. Renomeie o arquivo para `credentials.json`
8. Coloque o arquivo na raiz do projeto (`/Users/freddomingues/Desenvolvimento/think-tars/credentials.json`)

## Passo 4: Configurar Variáveis de Ambiente

Adicione as seguintes variáveis ao arquivo `.env`:

```bash
# Google Calendar API
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json
GOOGLE_CALENDAR_TOKEN_PATH=token.json
GOOGLE_CALENDAR_ID=primary
```

**Nota:** O `GOOGLE_CALENDAR_ID` pode ser:
- `primary` - Calendário principal da conta
- Um ID específico de calendário (ex: `abc123@group.calendar.google.com`)

## Passo 5: Instalar Dependências

```bash
pip install -r requirements.txt
```

As dependências do Google Calendar já estão incluídas:
- `google-api-python-client>=2.100.0`
- `google-auth-httplib2>=0.1.1`
- `google-auth-oauthlib>=1.1.0`

## Passo 6: Autenticação Inicial

Na primeira execução, o sistema abrirá o navegador para autenticação:

1. Execute o sistema normalmente
2. Quando o SDR Agent tentar usar o Google Calendar pela primeira vez, será aberto o navegador
3. Faça login com sua conta Google
4. Autorize o acesso ao Google Calendar
5. O token será salvo automaticamente em `token.json`

**Importante:** O arquivo `token.json` contém credenciais de acesso. Não compartilhe este arquivo publicamente.

## Funcionalidades Disponíveis

O SDR Agent agora pode:

### 1. Consultar Horários Disponíveis
- **Ferramenta**: `check_available_slots`
- **Uso**: Quando o cliente perguntar sobre disponibilidade
- **Exemplo**: "Quais horários você tem disponível na próxima semana?"

### 2. Agendar Reuniões
- **Ferramenta**: `create_calendar_event`
- **Uso**: Quando o cliente confirmar um horário
- **Exemplo**: "Quero agendar para amanhã às 14h"

### 3. Cancelar Reuniões
- **Ferramenta**: `cancel_calendar_event`
- **Uso**: Quando o cliente solicitar cancelamento
- **Exemplo**: "Preciso cancelar a reunião de amanhã"

### 4. Consultar Agenda do Dia
- **Ferramenta**: `get_events_by_date`
- **Uso**: Para verificar eventos de uma data específica
- **Exemplo**: "Quais reuniões temos hoje?"

### 5. Consultar Agenda de Amanhã
- **Ferramenta**: `get_tomorrow_events`
- **Uso**: Para verificar eventos do próximo dia
- **Exemplo**: "O que temos agendado para amanhã?"

### 6. Confirmar Agenda do Próximo Dia
- **Ferramenta**: `confirm_tomorrow_agenda`
- **Uso**: Diariamente para confirmar reuniões com clientes
- **Funcionalidade**: Consulta eventos de amanhã e envia mensagens de confirmação via WhatsApp

## Configuração de Horário de Trabalho

Por padrão, o sistema considera horário de trabalho de **9h às 18h**. Para alterar, edite o método `get_available_slots` em `external_services/google_calendar_client.py`:

```python
# Horário de trabalho padrão (9h às 18h)
work_start = time(9, 0)  # Altere aqui
work_end = time(18, 0)   # Altere aqui
```

## Troubleshooting

### Erro: "Arquivo de credenciais não encontrado"
- Verifique se `credentials.json` está na raiz do projeto
- Verifique a variável `GOOGLE_CALENDAR_CREDENTIALS_PATH` no `.env`

### Erro: "Token expirado"
- Delete o arquivo `token.json`
- Execute o sistema novamente para reautenticar

### Erro: "API não habilitada"
- Verifique se a Google Calendar API está habilitada no Google Cloud Console
- Aguarde alguns minutos após habilitar a API

### Erro: "Permissão negada"
- Verifique se autorizou todos os escopos necessários
- Verifique se o email está na lista de test users (OAuth consent screen)

## Segurança

⚠️ **Importante:**
- Nunca commite `credentials.json` ou `token.json` no Git
- Adicione estes arquivos ao `.gitignore`
- Use variáveis de ambiente para caminhos sensíveis
- Em produção, considere usar Service Account ao invés de OAuth 2.0

## Próximos Passos

1. Configure um calendário específico para reuniões (opcional)
2. Configure notificações automáticas
3. Integre com sistema de CRM (se aplicável)
4. Configure confirmações automáticas diárias via cron job

## Suporte

Para dúvidas ou problemas, consulte:
- [Google Calendar API Documentation](https://developers.google.com/calendar/api/guides/overview)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
