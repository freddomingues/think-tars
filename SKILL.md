---
name: meta-skill-creator
description: Meta-skill para criar outras skills específicas no projeto. Define padrões, formato e estrutura de skills (SKILL.md, references/). Use quando for criar nova skill, documentar módulo/workflow ou padronizar instruções para o agente. Triggers: "criar skill", "nova skill", "meta-skill", "skill específica", "documentar como skill", "padrão de skills".
---

# Meta-skill: Criar skills específicas

Guia genérico para criar novas **skills** no repositório. Segue os mesmos padrões das skills em `.cursor/skills/` (project-conventions, trading, llm-assistant, assistant-creator).

---

## 1. Quando criar uma skill específica

- **Módulo ou domínio** com convenções próprias (ex.: trading, llm-assistant, ingest).
- **Workflow ou processo** repetível (ex.: criar assistentes, fazer deploy, rodar ingestão).
- **Contexto que o agente** deve aplicar só quando relevante (por descrição e triggers), em vez de sempre.

Se for regra global e sempre ativa, considere project-conventions ou regras do Cursor; se for escopo específico e sob demanda, crie uma skill.

---

## 2. Onde criar

- **Skills do projeto:** `.cursor/skills/<nome-da-skill>/`
- **Meta-skill (esta):** `SKILL.md` na **raiz** do projeto — referência global para criar outras skills.

Cada skill específica vive em sua própria pasta em `.cursor/skills/`.

---

## 3. Estrutura de uma skill específica

```
.cursor/skills/<nome-da-skill>/
├── SKILL.md              # Obrigatório: frontmatter + corpo em Markdown
├── references/           # Opcional: exemplos, trechos, referências
│   └── *.md
├── templates/            # Opcional: modelos de arquivo
└── assets/               # Opcional: imagens, outros recursos
```

- **SKILL.md:** sempre presente; frontmatter YAML + corpo.
- **references/:** uso recomendado para exemplos longos, snippets, checklists (como em `assistant-creator`).
- **templates/**, **assets/:** quando a skill envolver gerar arquivos ou materiais visuais.

---

## 4. Formato do SKILL.md

### 4.1 Frontmatter (YAML)

```yaml
---
name: nome-da-skill
description: O que a skill faz e quando usar. Incluir triggers em linguagem natural para o agente descobrir quando aplicar. Evitar descrições vagas.
---
```

- **name:** identificador em kebab-case; deve coincidir com o nome da pasta (`<nome-da-skill>`).
- **description:** texto curto e claro; inclua **triggers** explícitos (ex.: "Triggers: X, Y, Z") para facilitar o uso pelo agente.

### 4.2 Corpo (Markdown)

- Título principal: `# Skill: <Nome legível>` ou `# <Nome legível>`.
- Seções com `##`, `###` conforme a complexidade.
- Uso de listas, tabelas, blocos de código e referências a arquivos do repositório quando fizer sentido.
- **Respostas:** se a skill orientar interação com usuário, incluir algo como “Responder em **português** ao usuário”.

Exemplos de seções comuns:

- **Visão geral** — o que a skill cobre.
- **Processo** — passos para executar o workflow.
- **Estrutura / Arquivos** — onde estão os módulos ou artefatos relevantes.
- **Convenções** — padrões de código, config, logs, idioma.
- **Exemplos** — referência a assistentes, módulos ou fluxos existentes.
- **Referências** — “Ver `references/` nesta skill” ou links para outros docs.

---

## 5. Triggers

Inclua na **description** ou numa seção **Triggers** os termos/frases que indicam quando a skill deve ser aplicada, por exemplo:

- **Genéricos:** "criar skill", "nova skill", "meta-skill", "padrão de skills".
- **Por domínio:** "trading", "assistente", "ingest", "llm".
- **Por tarefa:** "adicionar tool", "atualizar instruções", "configurar deploy".

Use os mesmos padrões das skills existentes (project-conventions, trading, llm-assistant, assistant-creator).

---

## 6. Processo para criar uma nova skill específica

1. **Escopo** — Definir nome (kebab-case), domínio/módulo e quando a skill será usada.
2. **Pasta** — Criar `.cursor/skills/<nome-da-skill>/`.
3. **SKILL.md** — Escrever frontmatter (`name`, `description` com triggers) e corpo (visão geral, processo, estrutura, convenções, exemplos).
4. **references/** (se necessário) — Adicionar `references/*.md` com exemplos, snippets ou checklists.
5. **Revisar** — Garantir que `name` = pasta, description inclui triggers e que o conteúdo segue os padrões das demais skills.

---

## 7. Exemplos de skills existentes no projeto

| Skill | Escopo | Referência |
|-------|--------|------------|
| **project-conventions** | Convenções gerais do projeto | `.cursor/skills/project-conventions/SKILL.md` |
| **trading** | Módulo de trading (AutoTrader, Binance, etc.) | `.cursor/skills/trading/SKILL.md` |
| **llm-assistant** | Assistente OpenAI, tools, Pinecone | `.cursor/skills/llm-assistant/SKILL.md` |
| **assistant-creator** | Como criar novos assistentes de IA | `.cursor/skills/assistant-creator/SKILL.md` (e `references/`) |

Use essas skills como modelo de formato, tom e nível de detalhe.

---

## 8. Convenções

- **Idioma:** descrições, triggers e conteúdo em **português**, salvo termos técnicos em inglês (ex.: `SKILL.md`, `tools`).
- **Consistência:** manter o mesmo estilo de frontmatter e seções entre skills.
- **Referências:** citar arquivos e pastas do repositório quando relevante (`llm_assistant/`, `app/main.py`, etc.).

---

## 9. Respostas

- Responder em **português** ao usuário, salvo pedido explícito em outro idioma.
