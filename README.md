# 🚀 Sistema de Assistente Jurídico Inteligente com IA

> **Nota:** Este projeto **não utiliza mais AWS** (S3, DynamoDB). A base de conhecimento vem dos **arquivos que os clientes fazem upload na aplicação** (demos) e do **Pinecone**. Threads e conversas são armazenados **em memória**.

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Subprojetos](#subprojetos)
   - [3.1. Agente de IA para Dúvidas de Contratos](#31-agente-de-ia-para-dúvidas-de-contratos)
   - [3.2. Agente de IA para Dúvidas e Atendimento do FAQ](#32-agente-de-ia-para-dúvidas-e-atendimento-do-faq)
   - [3.3. Agente de IA para Análise de Dados](#33-agente-de-ia-para-análise-de-dados)
   - [3.4. Sistema de Análise de Sentimento](#34-sistema-de-análise-de-sentimento)
4. [Componentes Técnicos](#componentes-técnicos)
5. [Fluxos Operacionais](#fluxos-operacionais)
6. [Infraestrutura e Deploy](#infraestrutura-e-deploy)
7. [Configuração](#configuração)

---

## 🎯 Visão Geral

Este projeto implementa um **sistema de assistentes de IA** com múltiplos agentes. Utiliza **Large Language Models (LLMs)** da OpenAI, busca vetorial com **Pinecone**, e os **arquivos enviados pelos clientes na aplicação** como base de conhecimento. Deploy na Render.

### Objetivos Principais

- **Assistentes conversacionais**: Múltiplos agentes especializados (jurídico, investimento, etc.)
- **Base de Conhecimento Privada**: Utilizar documentos internos (contratos e FAQs) como fonte de verdade
- **Análise Inteligente**: Prover análises de dados e métricas através de linguagem natural
- **Monitoramento de Sentimento**: Analisar o estado emocional das conversas para melhorar o atendimento
- **Escalabilidade**: Arquitetura preparada para alto volume de requisições simultâneas

### Tecnologias Principais

- **LLM**: OpenAI GPT-4o (Assistant API)
- **Busca Vetorial**: Pinecone (namespaces separados para contratos e FAQs)
- **Armazenamento**: AWS S3 (documentos), AWS DynamoDB (conversas e threads)
- **Processamento**: Python 3.12, Flask, asyncio
- **Deploy**: Render (aplicação principal)

---

## 🏗️ Arquitetura do Sistema

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                  Render (Aplicação Flask)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  app/main.py                                              │  │
│  │  ├── API de demos (/api/demos)                            │  │
│  │  ├── Tools HTTP (search_contracts, search_faqs)           │  │
│  │  └── Frontend em /demos                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  OpenAI Assistant API                                     │  │
│  │  ├── Thread Management (contexto de conversa)             │  │
│  │  ├── Tool Selection (decide qual tool usar)               │  │
│  │  └── Response Generation                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
┌───────────────────────────┐  ┌──────────────────────────┐
│  Pinecone (Vector DB)     │  │  Upload de PDF (demos)   │
│  ├── namespace: contracts │  │  Arquivos dos clientes   │
│  └── namespace: faqs      │  │  → OpenAI File Search    │
└───────────────────────────┘  └──────────────────────────┘
```

### Fluxo de Dados Global

1. **Base de conhecimento**: Arquivos enviados pelos clientes na aplicação (upload de PDF) + Pinecone
2. **Demos**: Frontend em `/demos` → API de demos → OpenAI Assistant → resposta no chat
3. **Tools**: Assistant usa search_contracts e search_faqs (Pinecone) quando necessário

---

## 🔧 Subprojetos

O sistema é composto por **4 subprojetos principais**, cada um com responsabilidades específicas:

---

### 3.1. Agente de IA para Dúvidas de Contratos

#### Visão Geral

Agente especializado em responder perguntas específicas sobre **termos, cláusulas e detalhes de contratos jurídicos**. Utiliza busca vetorial em um namespace dedicado no Pinecone que contém embeddings de documentos contratuais processados.

#### Componentes Principais

**3.1.1. Pipeline de Ingestão de Contratos**

```12:87:ingest/ingest_contracts.py
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Inicializa cliente S3
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

def list_pdfs_in_bucket(prefix: str = None) -> list[str]:
    """Lista todos os PDFs do bucket com prefixo opcional."""
    # ... implementação ...

def index_pdf_from_s3(s3_key: str):
    """Baixa PDF do S3, extrai texto e indexa no Pinecone."""
    # ... implementação ...

def index_all_contracts():
    """Indexa todos os contratos da raiz do bucket S3."""
    # ... implementação ...
```

**Arquivos:**
- `ingest/ingest_contracts.py`: Lógica de ingestão e indexação
- `ingest/cache_manager.py`: Sistema de cache para evitar reprocessamento
- `data_ingestion/pdf_processor.py`: Extração de texto de PDFs

**Processo:**
1. Lista PDFs na raiz do bucket S3 (excluindo `faqs/`)
2. Verifica cache para identificar documentos novos/atualizados
3. Para cada PDF:
   - Baixa do S3
   - Extrai texto usando `pypdf`
   - Divide em chunks de 500 caracteres (overlap 50)
   - Gera embeddings via OpenAI (`text-embedding-ada-002`)
   - Indexa no Pinecone no namespace `contracts`

**3.1.2. Tool de Busca: `search_contracts`**

```89:93:ingest/ingest_contracts.py
def search_contracts(query: str, k: int = 5) -> str:
    """Busca trechos de contratos via Pinecone."""
    results = pinecone_client.search(query=query, k=k, namespace="contracts")
    docs = [r for r in results['documents'][0]]
    return "\n".join(docs) if docs else "Nenhum trecho relevante de contrato encontrado."
```

**Definição da Tool (OpenAI):**

```5:16:llm_assistant/tools.py
    {
        "type": "function",
        "function": {
            "name": "search_contracts",
            "description": "Busca trechos de contratos jurídicos relevantes.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "k": {"type": "integer", "default": 5}},
                "required": ["query"]
            }
        }
    }
```

**3.1.3. Endpoint REST**

```83:99:app/main.py
@app.route('/api/tools/search_contracts', methods=['POST'])
def search_contracts():
    data = request.json
    query = data.get("query")
    if not query:
        log_error('app.main', "Missing 'query' parameter")
        return jsonify({"error": "Missing 'query' parameter"}), 400

    try:
        client, namespace = get_chroma_client_contract()
        results = client.search(query=query, k=3, namespace=namespace)
        docs_found = len(results.get('documents', [[]])[0])
        log_tool_call('search_contracts', query, docs_found)
        return jsonify(results), 200
    except Exception as e:
        log_error('app.main', f"Erro na busca de contratos: {e}")
        return jsonify({"error": "Internal server error"}), 500
```

#### Fluxo Operacional

```
Usuário pergunta sobre contrato
         │
         ▼
OpenAI Assistant analisa pergunta
         │
         ▼
Decide usar tool "search_contracts"
         │
         ▼
Tool é chamada com query extraída
         │
         ▼
Pinecone busca no namespace "contracts"
         │
         ▼
Retorna top 3 chunks mais similares
         │
         ▼
Assistant gera resposta baseada nos chunks
         │
         ▼
Resposta exibida no chat (demos)
```

#### Instruções do Assistente

O assistente é configurado para usar `search_contracts` **apenas quando a pergunta for especificamente sobre contratos**:

```7:8:llm_assistant/prompt_templates.py
- Use a ferramenta 'search_contracts' apenas se a pergunta for especificamente sobre termos e detalhes de contratos.
- Use a ferramenta 'search_faqs' para responder a perguntas gerais sobre a empresa, seus serviços ou outras dúvidas que não sejam sobre contratos.
```

---

### 3.2. Agente de IA para Dúvidas e Atendimento do FAQ

#### Visão Geral

Agente focado em responder **perguntas gerais sobre a empresa, serviços, procedimentos e outras dúvidas frequentes** que não sejam relacionadas a contratos. Utiliza um namespace separado no Pinecone para FAQs.

#### Componentes Principais

**3.2.1. Pipeline de Ingestão de FAQs**

```22:64:ingest/ingest_faqs.py
def index_pdf_bytes(file_bytes, source_name):
    """Indexa PDF na coleção de FAQ."""
    text = extract_text_from_pdf_bytes(file_bytes)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,   # menor
        chunk_overlap=50  # menor overlap
    )
    chunks = splitter.split_text(text)

    # Gera embeddings em batch (muito mais eficiente)
    embeddings = pinecone_client.embedding_model.embed_documents(chunks)

    metadatas = [{"source": source_name, "chunk": i} for i in range(len(chunks))]
    ids = [f"{source_name}_{i}" for i in range(len(chunks))]

    pinecone_client.add_documents(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
        namespace="faqs"
    )
```

**Arquivos:**
- `ingest/ingest_faqs.py`: Lógica específica para FAQs
- Processa PDFs da pasta `faqs/` no S3

**Diferenças do Pipeline de Contratos:**
- Processa arquivos da pasta `faqs/` (prefixo configurável)
- Namespace separado: `faqs`
- Mesma estratégia de chunking (500 caracteres, overlap 50)

**3.2.2. Tool de Busca: `search_faqs`**

```86:90:ingest/ingest_faqs.py
def search_faqs(query: str, k: int = 5) -> str:
    """Busca trechos de FAQs via Pinecone."""
    results = pinecone_client.search(query=query, k=k, namespace="faqs")
    docs = [r for r in results['documents'][0]]
    return "\n".join(docs) if docs else "Nenhum trecho relevante de FAQ encontrado."
```

**Definição da Tool:**

```18:29:llm_assistant/tools.py
    {
        "type": "function",
        "function": {
            "name": "search_faqs",
            "description": "Busca trechos de FAQs relevantes.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "k": {"type": "integer", "default": 5}},
                "required": ["query"]
            }
        }
    }
```

**3.2.3. Endpoint REST**

```101:117:app/main.py
@app.route('/api/tools/search_faqs', methods=['POST'])
def search_faqs():
    data = request.json
    query = data.get("query")
    if not query:
        log_error('app.main', "Missing 'query' parameter")
        return jsonify({"error": "Missing 'query' parameter"}), 400

    try:
        client, namespace = get_chroma_client_faqs()
        results = client.search(query=query, k=3, namespace=namespace)
        docs_found = len(results.get('documents', [[]])[0])
        log_tool_call('search_faqs', query, docs_found)
        return jsonify(results), 200
    except Exception as e:
        log_error('app.main', f"Erro na busca de FAQs: {e}")
        return jsonify({"error": "Internal server error"}), 500
```

#### Fluxo Operacional

Similar ao de contratos, mas:
- Usa namespace `faqs` no Pinecone
- Processa documentos da pasta `faqs/` no S3
- É usado para perguntas gerais (não sobre contratos)

#### Decisão Automática de Tool

O OpenAI Assistant decide automaticamente qual tool usar baseado nas instruções:

```7:8:llm_assistant/prompt_templates.py
- Use a ferramenta 'search_contracts' apenas se a pergunta for especificamente sobre termos e detalhes de contratos.
- Use a ferramenta 'search_faqs' para responder a perguntas gerais sobre a empresa, seus serviços ou outras dúvidas que não sejam sobre contratos.
```

---

### 3.3. Agente de IA para Análise de Dados

#### Visão Geral

Agente especializado em **consultar, analisar e gerar insights** a partir de planilhas Excel armazenadas no S3. Permite ao usuário fazer perguntas em linguagem natural sobre dados, KPIs, estatísticas e métricas.

#### Componentes Principais

**3.3.1. Sistema de Consulta de Planilhas**

```28:75:ingest/query_spreadsheet.py
def load_spreadsheet_from_s3(file_name: str = "base_dados_mock.xlsx") -> Optional[pd.DataFrame]:
    """
    Carrega uma planilha Excel do S3.
    
    Args:
        file_name: Nome do arquivo Excel no bucket S3
        
    Returns:
        DataFrame com os dados da planilha ou None se houver erro
    """
    global _spreadsheet_cache, _cache_file_name
    
    # Verifica se já está em cache
    if _spreadsheet_cache is not None and _cache_file_name == file_name:
        logger.info(f"📊 [SPREADSHEET] Usando planilha em cache: {file_name}")
        return _spreadsheet_cache
    
    try:
        # Busca o arquivo no S3
        logger.info(f"📥 [SPREADSHEET] Carregando planilha do S3: {file_name}")
        
        response = s3_client.get_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=file_name
        )
        
        # Lê o conteúdo do arquivo
        file_bytes = response['Body'].read()
        
        # Carrega o Excel usando pandas
        excel_file = io.BytesIO(file_bytes)
        df = pd.read_excel(excel_file, engine='openpyxl')
        
        # Atualiza cache
        _spreadsheet_cache = df
        _cache_file_name = file_name
        
        logger.info(f"✅ [SPREADSHEET] Planilha carregada com sucesso: {len(df)} linhas, {len(df.columns)} colunas")
        logger.info(f"📋 [SPREADSHEET] Colunas: {', '.join(df.columns.tolist())}")
        
        return df
```

**Funcionalidades:**
- Cache em memória para evitar recarregar a planilha a cada consulta
- Suporte a múltiplas abas
- Tratamento de erros robusto

**3.3.2. Tipos de Consultas Suportadas**

O sistema suporta múltiplos tipos de análise via linguagem natural:

**a) Informações da Estrutura:**
```151:162:ingest/query_spreadsheet.py
        if "informações" in query_lower or "info" in query_lower or "estrutura" in query_lower:
            return {
                "success": True,
                "type": "info",
                "data": {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": df.columns.tolist(),
                    "data_types": df.dtypes.astype(str).to_dict()
                },
                "message": f"Planilha possui {len(df)} linhas e {len(df.columns)} colunas"
            }
```

**b) Estatísticas Descritivas:**
```164:181:ingest/query_spreadsheet.py
        elif "estatística" in query_lower or "resumo" in query_lower or "describe" in query_lower:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                stats = df[numeric_cols].describe()
                return {
                    "success": True,
                    "type": "statistics",
                    "data": stats.to_dict(),
                    "message": "Estatísticas descritivas das colunas numéricas"
                }
```

**c) Valores Únicos:**
```183:212:ingest/query_spreadsheet.py
        elif "valores únicos" in query_lower or "unique" in query_lower or "distintos" in query_lower:
            # Tenta identificar a coluna mencionada na query
            cols = [col for col in df.columns if col.lower() in query_lower]
            if cols:
                col = cols[0]
                unique_values = df[col].unique().tolist()
                return {
                    "success": True,
                    "type": "unique_values",
                    "column": col,
                    "data": unique_values,
                    "count": len(unique_values),
                    "message": f"Valores únicos da coluna '{col}': {len(unique_values)} valores"
                }
```

**d) Cálculos (Média, Soma, Máximo, Mínimo):**
```237:300:ingest/query_spreadsheet.py
        elif any(word in query_lower for word in ["média", "médio", "average", "mean"]):
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                means = df[numeric_cols].mean().to_dict()
                return {
                    "success": True,
                    "type": "mean",
                    "data": means,
                    "message": "Médias das colunas numéricas"
                }
        # ... similar para soma, máximo, mínimo ...
```

**e) Análise de KPIs:**
```315:337:ingest/query_spreadsheet.py
        elif "kpi" in query_lower or "indicador" in query_lower:
            numeric_cols = df.select_dtypes(include=['number']).columns
            result = {
                "kpis": {}
            }
            
            for col in numeric_cols:
                result["kpis"][col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "sum": float(df[col].sum()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "std": float(df[col].std())
                }
            
            return {
                "success": True,
                "type": "kpis",
                "data": result,
                "message": "Análise de KPIs das colunas numéricas"
            }
```

**3.3.3. Tool de Consulta: `query_spreadsheet`**

```30:63:llm_assistant/tools.py
    {
        "type": "function",
        "function": {
            "name": "query_spreadsheet",
            "description": """Realiza consultas e análises de dados em planilhas Excel do S3.
            Use esta ferramenta para:
            - Obter informações sobre a estrutura da planilha (colunas, linhas, tipos de dados)
            - Calcular estatísticas descritivas (média, mediana, soma, máximo, mínimo)
            - Analisar KPIs e indicadores
            - Contar valores únicos ou totais
            - Filtrar e visualizar dados
            - Realizar análises de dados e métricas
            
            A planilha padrão é 'base_dados_mock.xlsx' que está no mesmo bucket S3 dos outros arquivos.
            Esta ferramenta é útil para responder perguntas sobre dados, métricas, KPIs e análises.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": """Descrição da consulta ou análise desejada. 
                        Exemplos: 
                        - 'mostrar informações da planilha'
                        - 'calcular média da coluna vendas'
                        - 'contar valores únicos de produtos'
                        - 'analisar KPIs de performance'
                        - 'estatísticas descritivas'
                        - 'filtrar dados onde status é ativo'"""
                    }
                },
                "required": ["query"]
            }
        }
    }
```

**3.3.4. Endpoint REST**

```119:135:app/main.py
@app.route('/api/tools/query_spreadsheet', methods=['POST'])
def query_spreadsheet():
    """Endpoint para consultas em planilhas Excel do S3."""
    data = request.json
    query = data.get("query")
    if not query:
        log_error('app.main', "Missing 'query' parameter")
        return jsonify({"error": "Missing 'query' parameter"}), 400

    try:
        from ingest.query_spreadsheet import query_spreadsheet_data
        result = query_spreadsheet_data(query)
        log_tool_call('query_spreadsheet', query, len(result) if result else 0)
        return jsonify({"result": result}), 200
    except Exception as e:
        log_error('app.main', f"Erro na consulta de planilha: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
```

#### Fluxo Operacional

```
Usuário pergunta sobre dados/KPIs
         │
         ▼
OpenAI Assistant identifica necessidade de análise
         │
         ▼
Decide usar tool "query_spreadsheet"
         │
         ▼
Tool extrai intenção da query (média, soma, etc)
         │
         ▼
Sistema carrega planilha do S3 (com cache)
         │
         ▼
Executa análise apropriada (pandas)
         │
         ▼
Formata resultados em texto legível
         │
         ▼
Assistant gera resposta explicativa
         │
         ▼
Resposta enviada ao usuário
```

#### Exemplos de Queries Suportadas

- "Mostrar informações da planilha"
- "Calcular média da coluna vendas"
- "Estatísticas descritivas"
- "Analisar KPIs de performance"
- "Contar valores únicos de produtos"
- "Qual o total de vendas?"
- "Mostrar os 10 maiores valores"

---

### 3.4. Sistema de Análise de Sentimento

#### Visão Geral

Sistema avançado que **analisa o sentimento das mensagens dos usuários** em tempo real, permitindo que o assistente adapte seu tom e estratégia de resposta. Os resultados são persistidos no DynamoDB e visualizados no dashboard.

#### Componentes Principais

**3.4.1. Analisador Avançado de Sentimento**

```17:95:sentiment_analyses/advanced_sentiment.py
class AdvancedSentimentAnalyzer:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Palavras-chave para contexto específico
        self.positive_keywords = [
            'obrigado', 'obrigada', 'perfeito', 'excelente', 'ótimo', 'bom', 'legal',
            'gostei', 'interessante', 'sim', 'claro', 'entendi', 'beleza', 'show',
            'maravilhoso', 'fantástico', 'incrível', 'top', 'demais', 'massa'
        ]
        
        self.negative_keywords = [
            'não', 'nunca', 'jamais', 'ruim', 'péssimo', 'terrível', 'horrível',
            'problema', 'erro', 'falha', 'defeito', 'reclamação', 'insatisfeito',
            'frustrado', 'irritado', 'chateado', 'bravo', 'raiva', 'ódio'
        ]
        
        self.urgency_keywords = [
            'urgente', 'rápido', 'agora', 'imediato', 'emergência', 'pressa',
            'depressa', 'logo', 'já', 'hoje', 'amanhã', 'asap'
        ]

    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analisa o sentimento de um texto usando múltiplos métodos.
        """
        # ... implementação ...
```

**Métodos de Análise:**

1. **VADER Sentiment Analyzer**: Análise léxica e regras específicas para português/inglês
2. **TextBlob**: Análise baseada em polaridade e subjetividade
3. **Análise de Palavras-Chave**: Dicionário customizado com palavras positivas/negativas/urgência
4. **Score Combinado**: Combinação ponderada dos métodos acima

**Cálculo de Score Combinado:**

```135:161:sentiment_analyses/advanced_sentiment.py
    def _calculate_combined_score(self, vader_scores: Dict, textblob_polarity: float, 
                                keyword_analysis: Dict, urgency_score: float) -> float:
        """Calcula score combinado de todos os métodos."""
        # Peso para cada método
        vader_weight = 0.4
        textblob_weight = 0.3
        keyword_weight = 0.2
        urgency_weight = 0.1
        
        # Score do VADER (compound score)
        vader_score = vader_scores['compound']
        
        # Score do TextBlob
        textblob_score = textblob_polarity
        
        # Score das palavras-chave
        keyword_score = keyword_analysis['score']
        
        # Combina os scores
        combined = (
            vader_score * vader_weight +
            textblob_score * textblob_weight +
            keyword_score * keyword_weight +
            urgency_score * urgency_weight
        )
        
        return combined
```

**3.4.2. Integração no Fluxo de Mensagens**

```156:179:app/main.py
            # Análise de sentimento da mensagem
            logger.info(f"🎭 [SENTIMENT] Analisando sentimento da mensagem...")
            sentiment_analysis = sentiment_analyzer.analyze_sentiment(message_content)
            logger.info(f"🎭 [SENTIMENT] {phone_number} - Sentimento: {sentiment_analysis['sentiment']} (Confiança: {sentiment_analysis['confidence']:.2f})")
            
            # Salva mensagem e análise no banco
            logger.info(f"💾 [DATABASE] Salvando mensagem no banco...")
            message_id = conversation_manager.save_message(
                conversation_id=thread_id,
                phone_number=phone_number,
                message=message_content,
                sender='user'
            )
            
            if message_id:
                logger.info(f"✅ [DATABASE] Mensagem salva com ID: {message_id}")
                conversation_manager.save_sentiment_analysis(
                    message_id=message_id,
                    conversation_id=thread_id,
                    sentiment_data=sentiment_analysis
                )
                logger.info(f"✅ [DATABASE] Análise de sentimento salva")
```

**3.4.3. Adaptação de Resposta Baseada em Sentimento**

O assistente adapta seu tom baseado no sentimento detectado:

```18:23:llm_assistant/prompt_templates.py
# Análise de Sentimento
- Considere o sentimento do usuário ao responder
- Se o sentimento for NEGATIVO: seja mais empático, ofereça ajuda e soluções
- Se o sentimento for POSITIVO: mantenha o tom positivo e proativo
- Se o sentimento for NEUTRO: seja profissional e direto
- Adapte seu tom de acordo com a urgência detectada na mensagem
```

**3.4.4. Envio de Metadata com Sentimento**

```275:277:app/main.py
                    # Resposta retornada ao cliente (demos) ou exibida no chat
```

**3.4.5. Análise de Sentimento de Conversa Completa**

```185:241:sentiment_analyses/advanced_sentiment.py
    def analyze_conversation_sentiment(self, messages: List[Dict]) -> Dict:
        """Analisa o sentimento geral de uma conversa."""
        if not messages:
            return {'overall_sentiment': 'neutro', 'confidence': 0.0, 'trend': 'estável'}
        
        sentiments = []
        confidences = []
        
        for message in messages:
            if message.get('sender') == 'user':  # Apenas mensagens do usuário
                analysis = self.analyze_sentiment(message.get('message', ''))
                sentiments.append(analysis['sentiment'])
                confidences.append(analysis['confidence'])
        
        # ... determina sentimento geral e tendência ...
        
        return {
            'overall_sentiment': overall_sentiment,
            'confidence': avg_confidence,
            'trend': trend,
            'sentiment_distribution': {
                'positivo': positive_count,
                'negativo': negative_count,
                'neutro': neutral_count
            },
            'total_messages': total
        }
```

**Funcionalidades:**
- Calcula sentimento geral da conversa
- Identifica tendência (melhorando, piorando, estável)
- Distribuição de sentimentos
- Confiança média

#### Estrutura de Dados Retornada

```python
{
    'sentiment': 'positivo' | 'negativo' | 'neutro',
    'confidence': 0.0-1.0,
    'scores': {
        'vader': {...},
        'textblob_polarity': float,
        'textblob_subjectivity': float,
        'keyword_analysis': {...},
        'urgency_score': float,
        'combined_score': float
    },
    'timestamp': 'ISO8601',
    'text_length': int,
    'word_count': int
}
```

#### Persistência no DynamoDB

```191:216:data_store/conversation_schema.py
    def save_sentiment_analysis(self, message_id: str, conversation_id: str, 
                               sentiment_data: Dict) -> str:
        """Salva análise de sentimento de uma mensagem."""
        analysis_id = f"sentiment_{message_id}"
        
        try:
            # Converte floats para Decimal
            converted_data = self._convert_floats_to_decimal(sentiment_data)
            
            self.sentiment_table.put_item(
                Item={
                    'analysis_id': analysis_id,
                    'message_id': message_id,
                    'conversation_id': conversation_id,
                    'sentiment': converted_data.get('sentiment'),
                    'confidence': converted_data.get('confidence', Decimal('0.0')),
                    'scores': json.dumps(converted_data.get('scores', {}), cls=DecimalEncoder),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return analysis_id
```

---

## 🔧 Componentes Técnicos

### 4.1. Gerenciamento de Assistente OpenAI

**Arquivo:** `llm_assistant/assistant_manager.py`

**Funções Principais:**

```9:34:llm_assistant/assistant_manager.py
def create_or_get_assistant(assistant_name: str = "Assistente Jurídico de Contratos") -> str:
    """
    Cria um novo assistente ou recupera um existente com base no nome.
    Retorna o ID do assistente.
    """
    try:
        # Tenta listar assistentes e encontrar um com o nome
        my_assistants = openai_client.beta.assistants.list(order="desc", limit="100")
        for existing_assistant in my_assistants.data:
            if existing_assistant.name == assistant_name:
                #print(f"Assistente '{assistant_name}' já existe! ID: {existing_assistant.id}")
                return existing_assistant.id

        # Se não encontrou, cria um novo
        assistant = openai_client.beta.assistants.create(
            name=assistant_name,
            instructions=DEFAULT_ASSISTANT_INSTRUCTIONS,
            model=LLM_MODEL,
            tools=TOOLS_DEFINITION
        )
        #print(f"Assistente '{assistant_name}' criado com sucesso! ID: {assistant.id}")
        return assistant.id

    except Exception as e:
        #print(f"Erro ao criar/obter o Assistente: {e}")
        return None
```

**Inicialização na Aplicação:**

```57:72:app/main.py
def initialize_application():
    """Inicializa o assistente LLM."""
    global ASSISTANT_ID
    logger.info("🚀 Inicializando aplicação...")
    try:
        assistant_id_local = create_or_get_assistant("Assistente Jurídico de Contratos")
        if not assistant_id_local:
            raise ValueError("Falha crítica: não foi possível criar/obter Assistant ID.")
        ASSISTANT_ID = assistant_id_local
        logger.info(f"✅ Assistant ID obtido: {ASSISTANT_ID}")
        logger.info("✅ Aplicação inicializada com sucesso!")
    except (APIError, AuthenticationError, RateLimitError, APIConnectionError, ValueError, Exception) as e:
        logger.error(f"❌ ERRO na inicialização: {type(e).__name__}: {e}")
        sys.exit(1)

initialize_application()
```

### 4.2. Sistema de Busca Vetorial (Pinecone)

**Arquivo:** `llm_assistant/pinecone_client.py`

**Classe Principal:**

```13:33:llm_assistant/pinecone_client.py
class PineconeClient:
    def __init__(self):
        """Inicializa o cliente Pinecone."""
        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY não definida no ambiente ou no arquivo .env")
        
        # Inicializa Pinecone com a nova API
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Conecta ao índice
        self.index = self.pc.Index(PINECONE_INDEX_NAME)
        
        # Embeddings OpenAI
        embedding_model = EMBEDDING_MODEL or "text-embedding-ada-002"
        self.embedding_model = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=OPENAI_API_KEY
        )
        
        logger.info(f"✅ Pinecone conectado ao índice: {PINECONE_INDEX_NAME}")
```

**Operações:**
- `add_documents()`: Indexa documentos com embeddings
- `search()`: Busca por similaridade vetorial
- `delete_by_ids()`: Remove documentos específicos
- `get_stats()`: Estatísticas do índice

**Namespaces:**
- `contracts`: Para documentos contratuais
- `faqs`: Para documentos de FAQ

### 4.3. Gerenciamento de Contexto (DynamoDB)

**Arquivos:**
- `data_store/dynamodb_handler.py`: Gerenciamento de threads
- `data_store/conversation_schema.py`: Schema completo de conversas

**Persistência de Threads:**

```13:33:data_store/dynamodb_handler.py
def get_user_thread_id(phone_number: str) -> str | None:
    """
    Recupera o thread_id do usuário do DynamoDB.
    Retorna o thread_id se encontrado, None caso contrário ou em caso de erro.
    """
    try:
        response = table.get_item(Key={'phone_number': phone_number})
        item = response.get('Item')
        if item:
            logger.info(f"💾 [DYNAMODB] Thread ID encontrado para {phone_number}: {item['thread_id']}")
            return item['thread_id']
        logger.info(f"💾 [DYNAMODB] Nenhuma Thread ID encontrada para {phone_number}.")
        return None
    except ClientError as e:
        # Erros específicos do cliente Boto3, como permissão negada, etc.
        logger.error(f"❌ [DYNAMODB] Erro ao buscar thread ID no DynamoDB para {phone_number}: {e.response['Error']['Message']}")
        return None
```

**Schema de Conversas:**

Tabelas DynamoDB:
1. **Conversations**: Metadados de conversas
2. **Messages**: Mensagens individuais (user/assistant)
3. **SentimentAnalysis**: Análises de sentimento por mensagem

**Índices:**
- `phone-number-index`: Buscar conversas por telefone
- `conversation-index`: Buscar mensagens por conversa
- `message-index`: Buscar análise por mensagem

### 4.4. Processamento Assíncrono

**Arquitetura:**
- **Queue**: `queue.Queue` com capacidade de 100 mensagens
- **Worker Thread**: Processa mensagens em background
- **Thread Pool**: `ThreadPoolExecutor` com 4 workers
- **Async Processing**: Função `process_message_async` usando `asyncio`

```53:55:app/main.py
# === Fila e pool de threads ===
message_queue = queue.Queue(maxsize=100)
executor = ThreadPoolExecutor(max_workers=4)
```

**Worker Background:**

```288:303:app/main.py
def background_worker():
    """Worker que consome mensagens da fila e processa."""
    logger.info("🔄 [WORKER] Worker iniciado")
    while True:
        try:
            logger.info("⏳ [WORKER] Aguardando mensagem na fila...")
            phone_number, message_content = message_queue.get()
            logger.info(f"📥 [WORKER] Processando mensagem de {phone_number}")
            asyncio.run(process_message_async(phone_number, message_content))
            logger.info(f"✅ [WORKER] Mensagem processada com sucesso")
        except Exception as e:
            logger.error(f"❌ [WORKER] Erro ao processar mensagem: {e}")
            import traceback
            traceback.print_exc()
        finally:
            message_queue.task_done()
```

**Lock por Usuário:**

```142:144:app/main.py
    if phone_number not in user_locks:
        user_locks[phone_number] = asyncio.Lock()

    async with user_locks[phone_number]:
```

Garante que mensagens do mesmo usuário sejam processadas sequencialmente.

### 4.5. Sistema de Cache de Documentos

**Arquivo:** `ingest/cache_manager.py`

**Funcionalidades:**
- Evita reprocessar documentos já indexados
- Usa hash MD5 baseado em ETag + LastModified do S3
- Persistência em JSON local

```56:79:ingest/cache_manager.py
    def is_processed(self, s3_key: str) -> bool:
        """Verifica se documento já foi processado."""
        current_hash = self._get_file_hash(settings.S3_BUCKET_NAME, s3_key)
        if not current_hash:
            return False
        
        cached_hash = self.cache_data["processed_docs"].get(s3_key)
        return cached_hash == current_hash
    
    def mark_processed(self, s3_key: str):
        """Marca documento como processado."""
        current_hash = self._get_file_hash(settings.S3_BUCKET_NAME, s3_key)
        if current_hash:
            self.cache_data["processed_docs"][s3_key] = current_hash
            self.cache_data["last_update"] = datetime.now().isoformat()
            self._save_cache()
    
    def get_unprocessed_docs(self, doc_keys: list) -> list:
        """Retorna lista de documentos não processados."""
        unprocessed = []
        for key in doc_keys:
            if not self.is_processed(key):
                unprocessed.append(key)
        return unprocessed
```

---

## 🔄 Fluxos Operacionais

### 5.1. Fluxo de Demos (conversa no chat)

```
1. Usuário acessa /demos e seleciona assistente (opcional: upload de PDF)
         │
         ▼
2. Frontend chama API de demos (conversations, messages)
         │
         ▼
3. Backend adiciona mensagem à thread OpenAI e cria Run do Assistant
         │
         ▼
4. Assistant processa e pode solicitar tools
         │
         ├─► search_contracts → Pinecone (namespace: contracts)
         ├─► search_faqs → Pinecone (namespace: faqs)
         └─► (outras tools: trading, etc.)
         │
         ▼
5. Assistant gera resposta; frontend exibe no chat
```

### 5.2. Base de Conhecimento

- **Upload de PDF (demos):** Arquivo enviado pelo cliente é processado e indexado em um vector store da OpenAI (File Search) para aquela conversa.
- **Pinecone:** Namespaces `contracts` e `faqs` podem ser alimentados por outros fluxos; as tools `search_contracts` e `search_faqs` consultam o Pinecone.

### 5.3. Fluxo de Tool Call

```
1. Assistant identifica necessidade de informação externa
         │
         ▼
2. Status do Run muda para "requires_action"
         │
         ▼
3. main.py detecta tool calls no run.required_action
         │
         ▼
4. Para cada tool_call:
   ├─► Extrai function_name e arguments
   ├─► Busca função em AVAILABLE_FUNCTIONS
   ├─► Executa função com argumentos
   └─► Coleta resultado
         │
         ▼
5. Submete tool_outputs ao Assistant
         │
         ▼
6. Assistant processa outputs e gera resposta final
```

**Exemplo de Execução:**

```196:248:app/main.py
                if run.status == 'requires_action':
                    # Processa tool calls
                    tool_outputs = []
                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        logger.info(f"🔧 [TOOL] Executando tool: {function_name} com args: {function_args}")
                        
                        # Executa a função correspondente
                        if function_name in AVAILABLE_FUNCTIONS:
                            try:
                                function_to_call = AVAILABLE_FUNCTIONS[function_name]
                                
                                # Chama a função com os argumentos
                                if function_name == "query_spreadsheet":
                                    result = function_to_call(function_args.get("query", ""))
                                elif function_name in ["search_contracts", "search_faqs"]:
                                    result = function_to_call(
                                        function_args.get("query", ""),
                                        function_args.get("k", 5)
                                    )
                                else:
                                    result = function_to_call(**function_args)
                                
                                tool_outputs.append({
                                    "tool_call_id": tool_call.id,
                                    "output": str(result) if not isinstance(result, str) else result
                                })
                                
                                log_tool_call(function_name, str(function_args), len(str(result)))
                                logger.info(f"✅ [TOOL] Tool {function_name} executada com sucesso")
```

### 5.4. Fluxo de Análise de Sentimento

```
1. Mensagem recebida do usuário
         │
         ▼
2. AdvancedSentimentAnalyzer.analyze_sentiment()
         │
         ├─► VADER analysis
         ├─► TextBlob analysis
         ├─► Keyword analysis
         └─► Urgency detection
         │
         ▼
3. Combina scores com pesos
         │
         ▼
4. Determina sentimento final (positivo/negativo/neutro)
         │
         ▼
5. Salva análise no DynamoDB (tabela SentimentAnalysis)
         │
         ▼
6. Assistant usa sentimento para adaptar resposta
         │
         ▼
7. Metadata de sentimento incluída na resposta enviada
```

---

## 🚀 Infraestrutura e Deploy

### 6.1. Render (Aplicação Principal)

**Procfile:**

```
web: gunicorn --bind 0.0.0.0:$PORT app.main:app
```

**Características:**
- Aplicação Flask com Gunicorn
- Porta dinâmica via variável `$PORT`
- Auto-deploy via Git push

**Endpoints Expostos:**
- `GET /`: Health check
- `GET /demos`, `/demos/`: Frontend de demos
- `GET /api/demos/assistants`, `POST /api/demos/upload-pdf`, `POST /api/demos/conversations`, etc.
- `POST /api/tools/search_contracts`: Tool de busca de contratos (Pinecone)
- `POST /api/tools/search_faqs`: Tool de busca de FAQs (Pinecone)

### 6.2. AWS S3

**Estrutura de Pastas:**
```
s3://gen-ai-contratos/
├── contratos/
│   ├── contrato1.pdf
│   └── contrato2.pdf
├── faqs/
│   ├── faq1.pdf
│   └── faq2.pdf
└── base_dados_mock.xlsx
```

**Acesso:**
- Credenciais via variáveis de ambiente
- Região configurável (padrão: `us-east-2`)

### 6.3. AWS DynamoDB

**Tabelas:**

1. **AssistantUserThreads** (via `dynamodb_handler.py`)
   - Key: `phone_number`
   - Atributos: `thread_id`, `last_updated`
   - Uso: Mapear telefone → thread OpenAI

2. **Conversations** (via `conversation_schema.py`)
   - Key: `conversation_id`
   - GSI: `phone-number-index`
   - Atributos: `phone_number`, `last_message`, `created_at`, `message_count`

3. **Messages**
   - Key: `message_id`
   - GSI: `conversation-index`
   - Atributos: `conversation_id`, `phone_number`, `message`, `sender`, `timestamp`

4. **SentimentAnalysis**
   - Key: `analysis_id`
   - GSI: `message-index`, `conversation-index`
   - Atributos: `message_id`, `conversation_id`, `sentiment`, `confidence`, `scores`

**Billing Mode:**
- `PAY_PER_REQUEST` (on-demand)

### 6.4. Pinecone

**Configuração:**
- Índice único: `genai-documents`
- Namespaces separados: `contracts`, `faqs`
- Embedding model: `text-embedding-ada-002` (OpenAI)

**Operações:**
- Inserção em batch (100 vetores por vez)
- Busca por similaridade cosseno
- Metadados armazenam texto original e fonte

### 6.5. Dashboard (Opcional)

**Arquivo:** `dashboard/app.py`

**Funcionalidades:**
- Visualização de conversas em tempo real
- Análise de sentimento por conversa
- WebSocket para atualizações live
- Estatísticas gerais

**Tecnologias:**
- Flask-SocketIO para WebSocket
- Frontend: HTML/JS (templates/dashboard.html)

### 6.6. Demos — site de demonstração

Site para **demonstrar os assistentes de IA** via chat na web com **suporte a upload de PDFs** para criar bases de conhecimento personalizadas.

- **Backend:** `backend/` — API em `/api/demos` (listar assistentes, criar conversa, enviar mensagem, upload de PDF). Blueprint Flask registrado em `app/main.py`.
- **Frontend:** `frontend/` — SPA React + Vite. Build: `cd frontend && npm install && npm run build`. Saída em `frontend/dist`.
- **Acesso:** Com a aplicação Flask rodando e `frontend/dist` presente, o site é servido em **`/demos`** (ex.: `http://localhost:5004/demos/`). A raiz `/` exibe um link para as demos.

**Endpoints da API de demos:**
- `GET /api/demos/assistants` — lista assistentes disponíveis
- `POST /api/demos/upload-pdf` — faz upload de PDF e cria vector store (multipart/form-data: `file`, `agent_id`)
- `POST /api/demos/conversations` — cria conversa (body opcional: `{ "agent_id": "juridico", "vector_store_id": "vs_xxx" }`)
- `POST /api/demos/conversations/<id>/messages` — envia mensagem (body: `{ "content": "..." }`)
- `DELETE /api/demos/conversations/<id>` — deleta conversa e limpa recursos (assistente customizado e vector store)

**Funcionalidades:**
- **Seleção de Assistente:** Escolha entre os assistentes disponíveis no registry (jurídico, investimento, etc.)
- **Upload de PDF:** Faça upload de um PDF para criar uma base de conhecimento específica para a conversa
- **Vector Store Dinâmico:** Cada PDF é processado e indexado em um vector store exclusivo usando a API de File Search da OpenAI
- **Assistente Customizado:** Quando um PDF é enviado, um assistente específico é criado com acesso ao vector store
- **Limpeza Automática:** Recursos são limpos ao trocar de assistente ou encerrar a conversa

Ver `docs/ARCHITECTURE.md` e as skills **backend-developer** e **frontend-developer** para detalhes.

---

## ⚙️ Configuração

### 7.1. Variáveis de Ambiente

**Arquivo:** `.env` (não commitado) ou variáveis no Render

```bash
# OpenAI
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-ada-002

# Pinecone (base de conhecimento)
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=genai-documents

```

### 7.2. Dependências

**requirements.txt:**

Principais bibliotecas:
- `flask`: Framework web
- `openai`: Cliente OpenAI API
- `pinecone-client`: Cliente Pinecone
- `langchain`: Processamento de documentos
- `langchain-openai`: Integração OpenAI
- `pandas`: Análise de dados
- `openpyxl`: Leitura de Excel
- `pypdf`: Extração de texto PDF
- `vaderSentiment`: Análise de sentimento
- `textblob`: Análise de sentimento
- `gunicorn`: Servidor WSGI

### 7.3. Setup Inicial

1. **Clonar repositório**
2. **Criar ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```

3. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variáveis de ambiente:**
   - Copiar `.env.example` para `.env`
   - Preencher com credenciais (OpenAI, Pinecone). O projeto não usa AWS nem Zatten.

5. **Executar aplicação:**
   - A base de conhecimento vem dos arquivos que os clientes fazem upload na aplicação (demos) e do Pinecone.
   - Threads e conversas ficam em memória.

6. **Deploy no Render:**
   - Conectar repositório Git
   - Configurar variáveis de ambiente
   - Deploy automático

---

## 📊 Resumo Técnico

### Stack Completo

| Componente | Tecnologia |
|------------|------------|
| **LLM** | OpenAI GPT-4o (Assistant API) |
| **Vector DB** | Pinecone |
| **Cloud Storage** | AWS S3 |
| **NoSQL DB** | AWS DynamoDB |
| **Web Framework** | Flask (Python) |
| **Processamento** | asyncio, ThreadPoolExecutor |
| **Deploy** | Render |
| **Análise Sentimento** | VADER + TextBlob |
| **Data Analysis** | pandas + openpyxl |

### Arquitetura de Dados

- **Ingestão**: S3 → PDF Processing → Chunking → Embeddings → Pinecone
- **Busca**: Query → Embedding → Pinecone Search → RAG
- **Contexto**: Phone → DynamoDB → Thread ID → OpenAI Thread
- **Análise**: Message → Sentiment Analysis → DynamoDB → Dashboard

### Escalabilidade

- **Queue-based processing**: Suporta picos de tráfego (quando aplicável)
- **Cache**: Evita reprocessamento quando aplicável
- **On-demand DynamoDB**: Escala automaticamente
- **Pinecone**: Otimizado para busca vetorial em escala

---

## 🎯 Conclusão

Este sistema representa uma **solução completa de IA conversacional** para suporte automatizado, combinando:

✅ **Múltiplos agentes especializados** (contratos, FAQs, análise de dados)  
✅ **Busca vetorial avançada** com Pinecone  
✅ **Análise de sentimento** em tempo real  
✅ **Persistência de contexto** via DynamoDB  
✅ **Processamento assíncrono** para alta performance  
✅ **Dashboard de monitoramento**  
✅ **Arquitetura escalável** na nuvem  

A arquitetura modular permite fácil extensão e manutenção.
