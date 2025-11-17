# Resposta para Vaga de LLM Engineer

---

**Subject: Re: LLM Engineer Position - RAG Pipeline & Document Intelligence Experience**

Olá Orgül,

Obrigado pelo interesse e pela oportunidade de compartilhar mais sobre minha experiência. Fico entusiasmado com a possibilidade de contribuir com a equipe em projetos de IA de ponta.

Abaixo respondo às suas duas perguntas com detalhes técnicos sobre um projeto real que desenvolvi:

---

## 1. Pipeline RAG End-to-End

Desenvolvi um **sistema completo de assistente jurídico inteligente** que implementa um pipeline RAG de produção para responder dúvidas sobre contratos e FAQs via WhatsApp. Aqui está a arquitetura:

### **Vector Database: Pinecone**

Escolhi **Pinecone** pela sua escalabilidade, performance em busca por similaridade e suporte a namespaces múltiplos. O sistema utiliza um único índice (`genai-documents`) com dois namespaces separados:
- `contracts`: Para documentos contratuais jurídicos
- `faqs`: Para perguntas frequentes e documentação geral

### **Pipeline RAG Completo:**

**Ingestão:**
1. **Extração**: PDFs armazenados no AWS S3 são processados usando `pypdf` para extração de texto
2. **Chunking**: Texto dividido em chunks de 500 caracteres com overlap de 50 caracteres usando `RecursiveCharacterTextSplitter` (LangChain)
3. **Embeddings**: Geração de embeddings via OpenAI `text-embedding-ada-002` em batch para eficiência
4. **Indexação**: Vetores indexados no Pinecone com metadados (fonte, chunk_id) para rastreabilidade

**Retrieval Strategy:**
- **Busca por Similaridade Vetorial**: Query convertida em embedding e busca por similaridade cosseno no Pinecone
- **Top-K Retrieval**: Retorna top 3-5 chunks mais relevantes (configurável)
- **Namespace Routing**: O assistente OpenAI decide automaticamente qual namespace consultar baseado na intenção da pergunta (contratos vs. FAQs)
- **Context Injection**: Chunks recuperados são injetados no contexto do Assistant via tool calls, permitindo RAG verdadeiro

**Generation:**
- **OpenAI Assistant API** com GPT-4o como modelo base
- **Tool-based RAG**: O assistente decide quando usar as tools `search_contracts` ou `search_faqs`
- **Context Persistence**: Threads mantidas no DynamoDB para continuidade de conversa
- **Multi-turn Conversations**: Sistema mantém contexto histórico entre mensagens

### **Otimizações Implementadas:**
- **Cache de Documentos**: Sistema evita reprocessar documentos já indexados usando hash MD5 baseado em ETag do S3
- **Processamento Assíncrono**: Queue-based processing com workers para alta throughput
- **Batch Embeddings**: Geração de embeddings em lote para reduzir latência e custos
- **Metadata Filtering**: Metadados armazenados permitem filtragem futura por fonte, data, etc.

**Resultados**: O sistema processa centenas de documentos, mantém latência < 3s para respostas e escala para múltiplos usuários simultâneos.

---

## 2. Experiência com Análise de Contratos e Document Intelligence

Sim, tenho experiência significativa em **análise de contratos jurídicos** e **extração de dados estruturados**. O mesmo projeto mencionado acima é focado especificamente nisso:

### **Análise de Contratos Jurídicos:**

O sistema foi projetado para:
- **Busca Semântica em Contratos**: Usuários fazem perguntas em linguagem natural sobre termos, cláusulas e detalhes contratuais
- **RAG Especializado**: Namespace dedicado no Pinecone contém apenas documentos contratuais, permitindo respostas precisas sobre aspectos legais
- **Context-Aware Responses**: O assistente entende contexto jurídico e fornece respostas objetivas baseadas nos documentos reais

**Exemplo de Uso Real:**
- Usuário pergunta: *"Qual é o prazo de pagamento no contrato?"*
- Sistema busca chunks relevantes no namespace `contracts`
- Assistant gera resposta citando trechos específicos do contrato
- Resposta enviada via WhatsApp com fonte rastreada

### **Extração de Dados Estruturados:**

Além de contratos, implementei um **agente especializado em análise de dados** que:

1. **Processa Planilhas Excel** do S3 (ex: `base_dados_mock.xlsx`)
2. **Análise via Linguagem Natural**: Usuários fazem perguntas como:
   - "Calcular média da coluna vendas"
   - "Analisar KPIs de performance"
   - "Estatísticas descritivas"
   - "Contar valores únicos de produtos"

3. **Extração e Agregação**: Sistema usa `pandas` para:
   - Calcular estatísticas descritivas (média, mediana, desvio padrão)
   - Agregações complexas (soma, máximo, mínimo por categoria)
   - Análise de KPIs e métricas
   - Filtragem e visualização de dados

4. **LLM Workflow**: O OpenAI Assistant interpreta a intenção da query e executa a análise apropriada, retornando insights formatados em texto natural

**Tecnologias Utilizadas:**
- `pandas` + `openpyxl` para processamento de Excel
- Cache em memória para performance
- Integração com OpenAI para interpretação de queries em linguagem natural
- Formatação inteligente de resultados para apresentação ao usuário

### **Arquitetura de Document Intelligence:**

O sistema também inclui:
- **Análise de Sentimento**: Sistema avançado que analisa sentimento das mensagens usando VADER + TextBlob + análise de palavras-chave customizada
- **Persistência de Contexto**: Todas as conversas e análises são armazenadas no DynamoDB para auditoria e melhoria contínua
- **Dashboard de Monitoramento**: Interface web para visualizar conversas, análises de sentimento e métricas

---

## Diferenciais Técnicos

Além do pipeline RAG, o projeto demonstra:
- **Protocol Engineering**: Integração com Zatten API e Meta WhatsApp Business API para comunicação A2A
- **Distributed Systems**: Arquitetura em nuvem (AWS + Render) com processamento assíncrono
- **Production-Ready**: Sistema em produção com logging, error handling, e monitoramento
- **Fine-tuning Ready**: Arquitetura preparada para incorporar modelos fine-tuned quando necessário

---

Estou disponível para uma conversa no Google Meet para discutir como essa experiência se alinha com as necessidades da posição. Posso também compartilhar mais detalhes técnicos, código (se apropriado), ou demonstrar o sistema em ação.

Aguardo seu retorno!

Atenciosamente,  
[Seu Nome]

---

**P.S.**: O projeto está documentado em detalhes técnicos completos, incluindo arquitetura, fluxos operacionais e decisões de design. Posso compartilhar a documentação completa se for de interesse.

