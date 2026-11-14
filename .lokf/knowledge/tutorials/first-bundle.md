---
type: Tutorial
id: https://w3id.org/ktl/knowledge/tutorials/first-bundle
title: Your first bundle
description: "A first run of Knowledge Trust Ladder (KTL) on one repository, for someone who has never used it: install the skills, lay the sidecar, fill the bundle, confirm one concept and ask a question, then what to do next."
genre: tutorial
resource: docs/first-bundle.md
sources:
  - resource: docs/first-bundle.md
    id: first-bundle.md
    excerpt: "Ask for the report again, and its first line reads `Confirmed by a person: 1 of N`."
references:
  - https://w3id.org/ktl/knowledge/glossary/sidecar
  - https://w3id.org/ktl/knowledge/glossary/librarian
  - https://w3id.org/ktl/knowledge/glossary/curator
  - https://w3id.org/ktl/knowledge/glossary/docent
  - https://w3id.org/ktl/knowledge/glossary/registrar
  - https://w3id.org/ktl/knowledge/glossary/trust-label
  - https://w3id.org/ktl/knowledge/references/gh-skill-cli
  - https://w3id.org/ktl/knowledge/playbooks/open-bundle-in-obsidian
  - https://w3id.org/ktl/knowledge/playbooks/ktl-website-skill
generated:
  by: process:ktl-librarian
  at: "2026-11-14T10:17:06Z"
status: draft
---

# Your first bundle

This tutorial takes one repository from no bundle to a first confirmed concept and a first answer. It is for someone who has not yet run Knowledge Trust Ladder (KTL). `docs/first-bundle.md` gives each step, and `docs/examples/first-bundle.md` shows what each step printed on a small repository.

You need three things: a git repository, an agent that runs Agent Skills (for example Claude Code or GitHub Copilot), and `uv`.

## 1. Install the skills

Run `gh skill install noelmcloughlin/knowledge-trust-ladder --all --scope user`. `gh skill` installs for GitHub Copilot unless you pass `--agent`. `docs/install.md` names the agents and gives two other ways to install.

## 2. Lay the sidecar

Open your agent in the repository and ask it to add a LOKF knowledge bundle. The sidecar creates `.lokf/`, a folder beside the code, and a `knowledge_bundle` link to the bundle inside it. The bundle holds only two dummy concepts at this point.

## 3. Fill the bundle

Ask the agent to fill the knowledge bundle from the repository. The librarian reads the repository and writes one Markdown file per concept under `.lokf/knowledge/`, and each file names the source it came from. Every new concept is a draft, because nobody has confirmed it yet.

## 4. Confirm one concept

Sign in to your forge first, with `gh auth login` on GitHub. A confirmation carries your login, and the curator skill takes it from there.

Ask what in the bundle needs your confirmation. The curator prints a one-screen report and offers a review session. Accept it. For one concept the curator shows the source, then the claim, and asks whether the source still says this. Answer **Confirm** for a concept you know to be right.

Ask for the report again. Its first line now reads `Confirmed by a person: 1 of N`.[^first-bundle.md] That number is meant to rise slowly, a handful of concepts in a sitting.

## 5. Ask a question

Ask about something the bundle covers, such as what a part of the project does. The docent answers from the bundle and names each concept it used, with a trust label. The concept you confirmed reads *confirmed by a person*. The others read *nobody has checked this yet, still a draft*.

## What to do next

- **Keep it checked.** Commit `.lokf/` on a branch and open a pull request. Turn on the workflows, and the registrar's gate checks every later change. The gate accepts your own confirmation only on a signed commit, so sign your commits first.
- **Keep it current.** The same install page turns on the scheduled librarian, which opens a pull request when sources move.
- **Read the bundle in an editor.** Open `knowledge_bundle` as an Obsidian vault.
- **Show it.** `ktl-website` publishes the bundle as a website.
- **Understand it.** `docs/architecture.md` says why the work is split this way.

[^first-bundle.md]: docs/first-bundle.md, step 4
