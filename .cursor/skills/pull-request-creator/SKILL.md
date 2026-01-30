---
name: pull-request-creator
description: Criar pull requests para o repositório generative-ai com descrição clara do que foi feito. Define processo, título, branch e template de explicação da PR. Use ao abrir PR, descrever mudanças ou preparar merge. Triggers: "criar PR", "pull request", "abrir PR", "descrição da PR", "explicar o que foi feito", "preparar PR", "merge request".
---

# Skill: Criar pull requests

Guia para criar **pull requests** no repositório do projeto generative-ai, com foco numa **explicação objetiva do que foi feito** na PR.

---

## 1. Quando usar

- Você implementou ou alterou código, config, docs ou scripts e vai **abrir uma PR** para `main` (ou outra base).
- Precisa **redigir ou revisar a descrição** da PR (o que mudou, por quê, como validar).
- Quer padronizar **título**, **branch** e **conteúdo** das PRs do projeto.

---

## 2. Processo (resumo)

1. **Branch** — Criar branch a partir da base atualizada (`main` ou outra). Nome em kebab-case (ex.: `feat/nova-skill-pr`, `fix/trading-log`).
2. **Commits** — Fazer commits atômicos e mensagens claras (recomendado: conventional commits: `feat:`, `fix:`, `docs:`, `chore:`).
3. **Push** — Enviar a branch para o remoto.
4. **Abrir PR** — Criar a PR no GitHub (ou outro host) contra a base desejada.
5. **Descrição** — Preencher título e corpo da PR conforme o template desta skill (seção 4 e `references/template-descricao-pr.md`).

---

## 3. Título e branch

- **Título da PR:** Objetivo e curto. Ex.: `feat: skill pull-request-creator`, `fix: erro em search_contracts quando query vazia`, `docs: atualiza README deploy`.
- **Branch:** Preferir prefixo + descrição em kebab-case, ex.: `feat/pull-request-creator`, `fix/trading-timeout`, `docs/readme-deploy`.

---

## 4. Descrição da PR — o que incluir

Toda PR deve ter uma **explicação clara do que foi feito**. Incluir:

### 4.1 O que foi feito (obrigatório)

- **Resumo** em 1–3 frases: qual mudança principal (ex.: “Nova skill para criar PRs com template de descrição”).
- **Escopo:** quais módulos/arquivos foram alterados (ex.: `.cursor/skills/`, `app/main.py`, `config/`).
- **Tipo de mudança:** feature, fix, refactor, docs, chore, etc.

### 4.2 Por quê (recomendado)

- Motivo da mudança: problema resolvido, melhoria, requisito novo.
- Se houver issue ou discussão, citar (ex.: “Resolve #123”).

### 4.3 Como validar (recomendado)

- Passos para testar ou verificar (comandos, endpoints, cenários).
- Ex.: “Rodar `pytest tests/`”, “Enviar mensagem no webhook e checar resposta”, “Abrir `/dashboard` e validar métricas”.

### 4.4 Checklist (opcional)

- [ ] Testes passando  
- [ ] Sem quebrar fluxos existentes  
- [ ] Docs/README atualizados se necessário  
- [ ] Variáveis de ambiente ou config documentadas, se houver novo uso  

---

## 5. Template de descrição

Use o modelo em **`references/template-descricao-pr.md`** ao abrir uma PR. Copie, preencha as seções e apague o que não se aplicar.

---

## 6. Convenções

- Descrição da PR em **português**.
- Evitar PRs gigantes: preferir mudanças focadas e várias PRs menores quando fizer sentido.
- Revisar diff antes de abrir: não incluir arquivos desnecessários (logs, `.env`, `venv/`, etc.); verificar `.gitignore`.

---

## 7. Respostas

- Responder em **português** ao usuário.
