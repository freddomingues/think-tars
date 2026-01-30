# Como Usar o Sistema de Demos

Este guia explica como usar a interface de demos para testar os assistentes de IA com upload de PDFs.

---

## 🚀 Acesso

1. **Inicie a aplicação Flask:**
   ```bash
   python app/main.py
   ```

2. **Acesse o frontend:**
   - Navegue para `http://localhost:5004/demos/`
   - Ou clique no link "Demos dos assistentes" na página inicial

---

## 📝 Fluxo de Uso

### 1. Selecionar Assistente

Na barra lateral esquerda, você verá um dropdown com os assistentes disponíveis:
- **Assistente Jurídico de Contratos** (padrão)
- **CryptoAnalyst - Análise de Investimento**
- Outros assistentes configurados no registry

Selecione o assistente que deseja testar.

### 2. Upload de PDF (Opcional)

**Para criar uma base de conhecimento personalizada:**

1. Clique no campo "Base de Conhecimento (opcional)"
2. Selecione um arquivo PDF do seu computador
3. O nome do arquivo aparecerá abaixo do campo
4. Para remover o arquivo, clique no "×" ao lado do nome

**Importante:**
- Apenas arquivos PDF são suportados
- O PDF será processado e indexado automaticamente
- O assistente se tornará especialista no conteúdo do PDF
- Cada conversa com PDF tem seu próprio vector store isolado

### 3. Iniciar Conversa

Clique no botão:
- **"Iniciar conversa"** - se não houver PDF selecionado
- **"Processar PDF e Iniciar"** - se houver PDF selecionado

**Com PDF:**
- O sistema processará o arquivo (pode levar alguns segundos)
- Você verá a mensagem "Processando PDF..."
- Quando concluído: "PDF processado com sucesso!"
- Um assistente customizado será criado com acesso ao conteúdo do PDF

**Sem PDF:**
- Uma conversa padrão será criada
- O assistente usará apenas suas ferramentas padrão (busca em contratos, FAQs, planilhas)

### 4. Conversar

1. Digite sua mensagem no campo de texto na parte inferior
2. Pressione Enter ou clique em "Enviar"
3. O assistente processará sua mensagem e responderá
4. O histórico da conversa aparecerá na tela

**Dicas:**
- Se você fez upload de um PDF, pergunte sobre o conteúdo do documento
- O assistente pode usar ferramentas adicionais conforme necessário
- As respostas são contextualizadas com base no histórico da conversa

### 5. Nova Conversa

Para iniciar uma nova conversa:
1. Clique em "Nova conversa"
2. O histórico será limpo
3. Você pode fazer upload de um novo PDF ou continuar sem PDF

### 6. Trocar Assistente

Para trocar de assistente:
1. Clique em "Trocar assistente"
2. Selecione um novo assistente no dropdown
3. Faça upload de um novo PDF (opcional)
4. Clique em "Iniciar conversa"

---

## 💡 Exemplos de Uso

### Exemplo 1: Assistente Jurídico com PDF de Contrato

1. Selecione "Assistente Jurídico de Contratos"
2. Faça upload de um PDF de contrato
3. Inicie a conversa
4. Pergunte: "Quais são as cláusulas de rescisão?"
5. O assistente buscará no PDF enviado e responderá

### Exemplo 2: CryptoAnalyst com Relatório de Mercado

1. Selecione "CryptoAnalyst - Análise de Investimento"
2. Faça upload de um PDF com análise de mercado
3. Inicie a conversa
4. Pergunte: "Qual a recomendação de investimento baseada neste relatório?"
5. O assistente analisará o conteúdo e fornecerá insights

### Exemplo 3: Assistente sem PDF

1. Selecione qualquer assistente
2. Não faça upload de PDF
3. Inicie a conversa
4. Faça perguntas gerais que o assistente possa responder com suas ferramentas padrão

---

## 🔧 Funcionalidades Técnicas

### Vector Stores

- Cada PDF enviado cria um **vector store exclusivo** na OpenAI
- O conteúdo é indexado usando a API de File Search
- O vector store é vinculado a um assistente customizado
- Quando você troca de assistente ou encerra a conversa, os recursos são limpos automaticamente

### Assistentes Customizados

- Com PDF: um assistente específico é criado para aquela conversa
- Sem PDF: usa o assistente padrão do registry
- Assistentes customizados têm a ferramenta `file_search` habilitada
- Mantêm todas as outras ferramentas do assistente base

### Limpeza de Recursos

- Ao trocar de assistente, os recursos da conversa anterior são deletados
- Assistentes customizados e vector stores são removidos
- Isso evita acúmulo de recursos não utilizados

---

## ⚠️ Limitações e Observações

1. **Tamanho do PDF:** Arquivos muito grandes podem demorar para processar
2. **Formato:** Apenas PDFs são suportados no momento
3. **Idioma:** O sistema funciona melhor com PDFs em português
4. **Persistência:** Conversas são armazenadas em memória (não persistem entre reinicializações)
5. **Custo:** Cada vector store e assistente customizado gera custos na OpenAI

---

## 🐛 Solução de Problemas

### Erro ao fazer upload

- Verifique se o arquivo é um PDF válido
- Certifique-se de que o arquivo não está corrompido
- Tente com um arquivo menor

### Assistente não responde sobre o PDF

- Aguarde alguns segundos após o upload (processamento pode demorar)
- Verifique se a mensagem "PDF processado com sucesso!" apareceu
- Tente fazer perguntas mais específicas sobre o conteúdo

### Erro ao iniciar conversa

- Verifique a conexão com a internet
- Confirme que as variáveis de ambiente estão configuradas
- Veja os logs do servidor para mais detalhes

---

## 📚 Próximos Passos

Após testar o sistema de demos, você pode:

1. Adicionar novos assistentes ao registry (`config/agents.py`)
2. Criar ferramentas customizadas para os assistentes
3. Integrar com outros sistemas via webhook
4. Expandir o frontend com mais funcionalidades

Para mais detalhes técnicos, consulte:
- `docs/ARCHITECTURE.md` - Arquitetura do sistema
- `.cursor/skills/` - Skills do projeto
- `README.md` - Visão geral completa
