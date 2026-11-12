# Your first bundle

This page is for anyone who has not yet run Knowledge Trust Ladder (KTL). It takes one repository from no bundle to a first confirmed concept and a first answer.

You need a git repository, an agent that runs Agent Skills, such as Claude Code or GitHub Copilot, and [`uv`](https://docs.astral.sh/uv/). [A captured run](examples/first-bundle.md) shows what each step printed on a small repository.

## 1. Install the skills

```bash
gh skill install noelmcloughlin/knowledge-trust-ladder --all --scope user
```

`gh skill` installs for GitHub Copilot unless you pass `--agent`. [install.md](install.md#quick-start) names the agents and gives two other ways to install.

## 2. Lay the sidecar

Open your agent in the repository and say:

> Add a LOKF knowledge bundle to this repository.

The [sidecar](cast/sidecar.md) creates `.lokf/`, a folder beside the code, and a `knowledge_bundle` link to the bundle inside it. The bundle holds only two dummy concepts so far.

## 3. Fill the bundle

> Fill the knowledge bundle from this repository.

The [librarian](cast/librarian.md) reads the repository and writes one Markdown file per concept under `.lokf/knowledge/`, each naming the source it came from. Every new concept is a draft, because nobody has vouched for it yet.

## 4. Confirm one concept

Sign in to your forge first, with `gh auth login` on GitHub. A confirmation carries your login, and the skill takes it from there.

> What in the bundle needs my confirmation?

The [curator](cast/curator.md) skill prints a one-screen report and offers a review session. Say yes. For one concept it shows the source, then the claim, and asks whether the source still says this. Answer **Confirm** for a concept you know to be right.

Ask for the report again, and its first line reads `Confirmed by a person: 1 of N`. That number is meant to rise slowly, a handful of concepts in a sitting.

## 5. Ask a question

Ask about something the bundle covers, such as what a part of the project does.

The [docent](cast/docent.md) answers from the bundle and names each concept it used, with a trust label. The concept you confirmed reads *confirmed by a person*. The others read *nobody has checked this yet, still a draft*.

## What to do next

- **Keep it checked.** Commit `.lokf/` on a branch and open a pull request. [Turn on the workflows](install.md#turn-on-the-workflows), and the [registrar](cast/registrar.md)'s gate checks every later change. The gate accepts your own confirmation only on a signed commit, so [sign your commits](signing-commits.md) first.
- **Keep it current.** The same page turns on the scheduled librarian, which opens a pull request when sources move.
- **Read the bundle in an editor.** [The bundle in Obsidian](obsidian.md) opens `knowledge_bundle` as a vault.
- **Show it.** [`ktl-website`](cast/website.md) publishes the bundle as a website.
- **Understand it.** [The architecture](architecture.md) says why the work is split this way.
