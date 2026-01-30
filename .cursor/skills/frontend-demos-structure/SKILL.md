---
name: frontend-demos-structure
description: Estrutura do frontend de demos do think-tars — pastas, App.jsx, index.css, variáveis CSS. Use ao localizar ou alterar estrutura de arquivos do frontend. Triggers: "estrutura frontend", "App.jsx", "pastas frontend", "index.css".
---

# Skill: Estrutura do frontend (site + Playground)

Estrutura de pastas e arquivos do frontend: site Think TARS (Início, Sobre, Projetos, Contato) e **Playground** (área onde o cliente testa os assistentes de IA). React + Vite, base URL `/demos/`.

---

## 1. Estrutura de pastas

```
frontend/
├── index.html          # Entry HTML
├── package.json
├── vite.config.js      # Proxy /api → Flask
├── public/
└── src/
    ├── main.jsx        # React root
    ├── App.jsx         # App principal (seletor, chat, upload PDF)
    └── index.css       # Estilos globais e variáveis CSS
```

---

## 2. Stack

- **React** 18, **Vite** 5.
- **Build:** `npm run build` → saída em `frontend/dist`.
- **Base URL:** `/demos/` (produção: Flask serve `frontend/dist` em `/demos`).

---

## 3. Arquivos principais

| Arquivo | Responsabilidade |
|---------|------------------|
| `index.html` | Página única; root para React. |
| `src/main.jsx` | `createRoot`, `App`, `StrictMode`. |
| `src/App.jsx` | Site (nav Início/Sobre/Projetos/Contato), hero, seções, cards; **Playground** (seletor de assistente, chat, upload PDF). Estado: assistants, selected, conversationId, messages, input, loading, error, pdfFile. Contato: telefone +55 41 8749-7364. |
| `src/index.css` | Variáveis CSS (--bg, --surface, --accent, --border, --text, --text-muted, --font-sans); estilos base. |

---

## 4. Convenções

- Componentes em `src/`. Manter `App.jsx` enxuto; extrair para componentes quando fizer sentido (ex.: Sidebar, ChatArea, MessageBubble).
- Estilos: preferir variáveis CSS em `index.css`; evitar libs pesadas se não precisar.
- Idioma da UI em português.

---

## 5. Onde alterar

- **Novo componente:** criar em `src/` (ex.: `src/components/MessageList.jsx`), importar em `App.jsx` ou em outro componente.
- **Nova tela ou fluxo:** ajustar `App.jsx` (ou adicionar roteador se introduzir múltiplas telas).
- **Novo estilo global:** `src/index.css`.

---

## 6. Referências

- **Chamadas à API:** skill **frontend-api-demos**.
- **UI de chat e sidebar:** skill **frontend-ui-chat**.
- **Build e servir:** skill **frontend-build-serve**.

---

## 7. Respostas

Responder em **português** ao usuário.
