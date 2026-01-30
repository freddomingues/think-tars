---
name: frontend-ui-chat
description: UI do chat de demos do think-tars — sidebar, seletor de assistente, upload PDF, mensagens, input, toast. Use ao alterar layout ou componentes visuais do chat. Triggers: "UI chat", "sidebar", "mensagens", "upload PDF", "componente chat".
---

# Skill: UI do chat de demos

Componentes e layout da interface de chat das demos: sidebar (seletor, upload PDF, botões), área de mensagens, input e toast de erro.

---

## 1. Layout geral (App.jsx)

- **Estrutura:** `layout` (flex column) → `header` (título, subtítulo) → `main` (flex) → `sidebar` (esquerda) + `chat` (direita). Toast de erro flutuante.
- **Estilos:** objeto `styles` em `App.jsx`; variáveis CSS em `index.css` (--bg, --surface, --accent, --border, --text, --text-muted).

---

## 2. Sidebar

- **Seletor de assistente:** `<select>` com `assistants.map(a => <option key={a.id} value={a.id}>{a.name}</option>)`; `value={selected}`; `disabled={!!conversationId}`. Ao mudar: `setSelected`, limpar `conversationId` e mensagens.
- **Upload PDF (opcional):** `<input type="file" accept=".pdf">`; só visível quando `!conversationId`. Estado `pdfFile`; validação de extensão; ao iniciar conversa com PDF, chama `POST /upload-pdf` com FormData.
- **Botões:** "Iniciar conversa" / "Processar PDF e Iniciar" (chama `startConversation`); "Nova conversa" / "Trocar assistente" (limpa conversa e mensagens).

---

## 3. Área de chat

- **Sem conversa:** placeholder com texto e dica (upload PDF).
- **Com conversa:** lista de mensagens (`messages.map`) + input (textarea + botão Enviar).
- **Mensagens:** cada item com `role` (user/assistant), `content`, `isError?`. Estilos: `bubble`, `userBubble`, `assistantBubble`, `errorBubble`; label "Você" ou nome do assistente.
- **Scroll:** `bottomRef` e `useEffect` para scroll suave ao atualizar mensagens.
- **Input:** Enter envia (sem Shift); botão "Enviar" desabilitado quando `!input.trim()` ou `loading`.

---

## 4. Toast de erro

- Exibido quando `error` não é null; botão para fechar (`setError(null)`).
- Estilo: destaque (ex.: fundo vermelho ou borda); `role="alert"`.

---

## 5. Onde alterar

- **Novo controle na sidebar:** adicionar estado e elemento em `App.jsx` na seção `sidebar`.
- **Novo tipo de mensagem ou estilo:** ajustar `styles` e o mapeamento de `messages`.
- **Extrair componente:** criar ex.: `MessageBubble`, `Sidebar`, `ChatInput` em `src/` e importar em `App.jsx`.

---

## 6. Referências

- **Estrutura do App:** skill **frontend-demos-structure**.
- **Chamadas à API:** skill **frontend-api-demos**.

---

## 7. Respostas

Responder em **português** ao usuário.
