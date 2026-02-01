# Workflow de Uso do MCP do Render

Guia rápido para usar MCP do Render em verificações e correções automáticas.

---

## 1. Identificar o Serviço

```python
# Listar todos os serviços
services = mcp_render_list_services()

# Encontrar o serviço "think-tars"
service = next(s for s in services if s['name'] == 'think-tars')
service_id = service['id']  # Ex: 'srv-d5veps14tr6s739loe7g'
```

---

## 2. Verificar Status do Serviço

```python
# Obter detalhes do serviço
service = mcp_render_get_service(serviceId=service_id)

# Verificar configuração
build_cmd = service['serviceDetails']['envSpecificDetails']['buildCommand']
start_cmd = service['serviceDetails']['envSpecificDetails']['startCommand']
suspended = service['suspended']  # 'not_suspended' = OK
```

---

## 3. Analisar Logs

### Logs Gerais

```python
# Últimos 100 logs
logs = mcp_render_list_logs(
    resource=[service_id],
    limit=100,
    direction='backward'
)
```

### Filtrar por Tipo

```python
# Apenas logs de build e app
logs = mcp_render_list_logs(
    resource=[service_id],
    type=['build', 'app'],
    limit=50
)
```

### Filtrar por Texto

```python
# Logs relacionados a gunicorn
logs = mcp_render_list_logs(
    resource=[service_id],
    text=['gunicorn', 'Starting gunicorn', 'command not found'],
    limit=30
)
```

### Filtrar por Período

```python
from datetime import datetime, timedelta

end_time = datetime.utcnow()
start_time = end_time - timedelta(hours=1)

logs = mcp_render_list_logs(
    resource=[service_id],
    startTime=start_time.isoformat() + 'Z',
    endTime=end_time.isoformat() + 'Z',
    limit=100
)
```

---

## 4. Verificar Deploys

```python
# Listar deploys recentes
deploys = mcp_render_list_deploys(
    serviceId=service_id,
    limit=5
)

# Detalhes do deploy mais recente
if deploys:
    latest_deploy = deploys[0]
    deploy_id = latest_deploy['id']
    
    deploy_details = mcp_render_get_deploy(
        serviceId=service_id,
        deployId=deploy_id
    )
```

---

## 5. Verificar Métricas

```python
# Métricas de CPU e memória
metrics = mcp_render_get_metrics(
    resourceId=service_id,
    metricTypes=['cpu_usage', 'memory_usage'],
    startTime='2026-02-01T00:00:00Z',
    endTime='2026-02-01T23:59:59Z',
    resolution=300  # 5 minutos
)
```

---

## 6. Casos de Uso Comuns

### Verificar se Build Foi Bem-Sucedido

```python
logs = mcp_render_list_logs(
    resource=[service_id],
    text=['Build successful', 'built in'],
    type=['app'],
    limit=20
)

# Procurar por "Build successful 🎉"
build_success = any('Build successful' in log['message'] for log in logs)
```

### Verificar se Aplicação Está Rodando

```python
logs = mcp_render_list_logs(
    resource=[service_id],
    text=['Starting gunicorn', 'gunicorn: command not found'],
    type=['app'],
    limit=10
)

# Se encontrar "command not found", problema de dependências
has_error = any('command not found' in log['message'] for log in logs)
is_running = any('Starting gunicorn' in log['message'] for log in logs)
```

### Verificar se Frontend Foi Buildado

```python
logs = mcp_render_list_logs(
    resource=[service_id],
    text=['npm run build', 'built in', 'dist/'],
    type=['app'],
    limit=30
)

# Procurar por "✓ built in X.XXs"
frontend_built = any('built in' in log['message'] for log in logs)
```

### Verificar Configuração do Build Command

```python
service = mcp_render_get_service(serviceId=service_id)
build_cmd = service['serviceDetails']['envSpecificDetails']['buildCommand']

# Verificar se inclui pip install
has_pip = 'pip install -r requirements.txt' in build_cmd
has_frontend_build = 'npm run build' in build_cmd
```

---

## 7. Workflow Completo de Diagnóstico

```python
# 1. Identificar serviço
services = mcp_render_list_services()
service = next(s for s in services if s['name'] == 'think-tars')
service_id = service['id']

# 2. Verificar configuração
service_details = mcp_render_get_service(serviceId=service_id)
build_cmd = service_details['serviceDetails']['envSpecificDetails']['buildCommand']

# 3. Verificar logs recentes
logs = mcp_render_list_logs(
    resource=[service_id],
    limit=100,
    direction='backward',
    type=['app', 'build']
)

# 4. Analisar problemas
issues = []
if 'pip install -r requirements.txt' not in build_cmd:
    issues.append("Build Command não inclui pip install")

if not any('Build successful' in log['message'] for log in logs):
    issues.append("Build não foi bem-sucedido")

if any('command not found' in log['message'] for log in logs):
    issues.append("Gunicorn não encontrado - dependências não instaladas")

if not any('Frontend estático configurado' in log['message'] for log in logs):
    issues.append("Frontend não está sendo servido")

# 5. Sugerir correções baseadas em issues
```

---

## 8. Referências

- **Skill principal:** `.cursor/skills/render-deploy/SKILL.md`
- **AGENTS.md:** Seção "Uso do MCP do Render para Verificações Automáticas"
