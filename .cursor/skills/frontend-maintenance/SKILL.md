---
name: frontend-maintenance
description: Manutenção do frontend React — componentes, estado, API calls, CSS, responsividade. Use ao adicionar features, corrigir bugs UI, melhorar UX ou debug. Triggers: "bug frontend", "UI não funciona", "React", "componente", "CSS", "responsivo", "mobile".
---

# Skill: Manutenção do Frontend React

Como manter, debugar e estender o frontend React da aplicação.

---

## 1. Estrutura do Frontend

### Arquivos Principais

- **`frontend/src/App.jsx`** - Componente principal, todas as seções do site, Playground, chat
- **`frontend/src/index.css`** - Estilos globais, variáveis CSS, media queries
- **`frontend/src/main.jsx`** - Entrypoint React
- **`frontend/vite.config.js`** - Configuração Vite (base URL, proxy)

---

## 2. Adicionar Nova Seção

### 1. Adicionar Seção no App.jsx

```jsx
// Dentro do componente App
const [sectionState, setSectionState] = useState(null);

// No return, adicionar nova seção
<section id="nova-secao" className="section">
  <div className="container">
    <h2>Nova Seção</h2>
    {/* Conteúdo aqui */}
  </div>
</section>
```

### 2. Adicionar Link no Menu

```jsx
// No nav-links
<li><a href="#nova-secao" onClick={handleNavClick}>Nova Seção</a></li>
```

### 3. Adicionar Estilos (se necessário)

```css
/* Em index.css */
#nova-secao {
  padding: 80px 0;
  background: var(--bg-primary);
}
```

---

## 3. Modificar Playground

### Adicionar Novo Agente no Carrossel

1. O frontend busca agentes via API: `GET /api/demos/assistants`
2. Os agentes são exibidos automaticamente no carrossel
3. Para adicionar novo agente, ver skill **ai-agents-maintenance**

### Modificar UI do Chat

- **Arquivo:** `frontend/src/App.jsx`
- **Função:** `sendMessage()` - Envia mensagem para o backend
- **Estado:** `messages`, `selectedAgent`, `conversationId`

### Upload de Arquivo

```jsx
// Input de arquivo
<input
  type="file"
  ref={fileInputRef}
  onChange={handleFileSelect}
  accept="*/*"
  style={{ display: 'none' }}
/>

// Upload antes de enviar mensagem
if (pdfFile) {
  const formData = new FormData();
  formData.append('file', pdfFile);
  
  const uploadRes = await fetch(`/api/demos/conversations/${conversationId}/upload-file`, {
    method: 'POST',
    body: formData
  });
  
  const { file_id } = await uploadRes.json();
  // Usar file_id ao enviar mensagem
}
```

---

## 4. Estilização

### Variáveis CSS

```css
:root {
  --primary-color: #6366f1;
  --bg-primary: #0f0f1a;
  --text-primary: #ffffff;
  --max-width: 1200px;
}
```

### Media Queries

```css
/* Mobile */
@media (max-width: 768px) {
  .section {
    padding: 40px 0;
  }
}

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) {
  .section {
    padding: 60px 0;
  }
}
```

### Responsividade

- **Mobile-first:** Estilos base para mobile, depois desktop
- **Breakpoints:** 360px, 480px, 768px, 1024px
- **Menu mobile:** Hamburger menu para telas pequenas

---

## 5. Integração com API

### Chamadas à API

```jsx
// Listar assistentes
const response = await fetch('/api/demos/assistants');
const assistants = await response.json();

// Criar conversa
const response = await fetch('/api/demos/conversations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ agent_id: 'juridico' })
});

// Enviar mensagem
const response = await fetch(`/api/demos/conversations/${conversationId}/messages`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Olá', file_ids: [fileId] })
});
```

### Error Handling

```jsx
try {
  const response = await fetch('/api/demos/assistants');
  if (!response.ok) {
    throw new Error('Erro ao buscar assistentes');
  }
  const data = await response.json();
} catch (error) {
  console.error('Erro:', error);
  // Mostrar mensagem de erro ao usuário
}
```

---

## 6. Estado e Hooks

### useState

```jsx
const [messages, setMessages] = useState([]);
const [selectedAgent, setSelectedAgent] = useState(null);
const [conversationId, setConversationId] = useState(null);
```

### useEffect

```jsx
// Buscar assistentes ao montar componente
useEffect(() => {
  fetchAssistants();
}, []);

// Resetar timer do carrossel quando slide muda
useEffect(() => {
  // Lógica aqui
}, [currentSlide]);
```

### useRef

```jsx
const fileInputRef = useRef(null);
const chatMessagesRef = useRef(null);

// Abrir file input
fileInputRef.current?.click();

// Scroll para última mensagem
chatMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
```

---

## 7. Debugging

### Console Logs

```jsx
console.log('Estado atual:', { messages, selectedAgent });
console.log('Resposta da API:', data);
```

### React DevTools

- Instalar extensão do navegador
- Inspecionar componentes, props, estado
- Verificar re-renders

### Verificar Network

- Abrir DevTools → Network
- Verificar requisições à API
- Verificar status codes, payloads, respostas

---

## 8. Build e Deploy

### Build Local

```bash
cd frontend
npm install
npm run build
```

### Verificar Build

- Verificar se `frontend/dist` foi criado
- Verificar se `index.html` e `assets/` existem
- Testar servindo localmente

### Deploy

- Build acontece automaticamente no Render
- Verificar logs de build no Render
- Verificar se frontend está sendo servido corretamente

---

## 9. Boas Práticas

1. **Componentizar quando reutilizar código**
2. **Usar variáveis CSS para cores e espaçamentos**
3. **Mobile-first para responsividade**
4. **Tratar erros de API com try/catch**
5. **Validar entrada do usuário**
6. **Otimizar imagens e assets**
7. **Usar lazy loading para componentes pesados (se necessário)**

---

## 10. Referências

- **Estrutura:** `.cursor/skills/frontend-demos-structure/`
- **API Calls:** `.cursor/skills/frontend-api-demos/`
- **UI Chat:** `.cursor/skills/frontend-ui-chat/`
- **Build:** `.cursor/skills/frontend-build-serve/`
