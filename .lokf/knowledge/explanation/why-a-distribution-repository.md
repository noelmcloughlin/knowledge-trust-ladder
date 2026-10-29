---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/why-a-distribution-repository
title: Why the skills live in their own repository
description: "Why the six skills are published from one installable repository: three install routes plus Microsoft 365 Copilot for the docent, one tag for all of them, one changelog, a bundle of its own that the docent answers from, and the repository's rename."
genre: explanation
resource: docs/install.md
sources:
  - resource: docs/install.md
  - resource: docs/architecture.md
  - resource: .claude-plugin/marketplace.json
  - resource: docs/m365.md
  - resource: .claude-plugin/plugin.json
  - resource: CHANGELOG.md
generated:
  by: process:ktl-librarian
  at: "2026-10-26T20:05:58Z"
status: draft
references:
  - https://w3id.org/ktl/knowledge/references/gh-skill-cli
  - https://w3id.org/ktl/knowledge/references/open-skills-cli
  - https://w3id.org/ktl/knowledge/policies/versioning
  - https://w3id.org/ktl/knowledge/playbooks/docent-in-m365-copilot
verified:
  - by: process:ktl-librarian
    at: "2026-10-29T12:26:25Z"
---

# Overview

The skills are installed from this repository rather than copied into each project that uses them. The optional fifth and sixth skills, `ktl-prose` and `ktl-website`, install the same way. There are three routes to the same set:

- the GitHub CLI, version 2.90.0 or later (`gh skill install noelmcloughlin/knowledge-trust-ladder --all --agent claude-code --scope user`, or a skill's name in place of `--all` to install only that one). It defaults to GitHub Copilot, so `--agent` names the agent. The repository contract keeps every tracked `SKILL.md` under `skills/ktl-*/`, so `--all` installs the ktl- skills only;
- the Open Skills CLI (`npx skills add noelmcloughlin/knowledge-trust-ladder --global --skill <skill>`), which can fail behind a company proxy or an internal npm registry;
- a Claude Code plugin that bundles all six (`/plugin marketplace add noelmcloughlin/knowledge-trust-ladder`, then `/plugin install knowledge-trust-ladder@knowledge-trust-ladder`), declared by `.claude-plugin/plugin.json` and `marketplace.json`.

A user install keeps the instructions an agent follows under the user's control. The scheduled librarian run installs `ktl-librarian` at the pinned tag before it starts. A team that wants every member on one version installs into the repository instead: it leaves out `--global`, or passes `--scope project`, and commits the `skills-lock.json` that `npx skills` writes.

All six skills are released together under one `vMAJOR.MINOR.PATCH` tag with one `CHANGELOG.md`, so a set pinned to one tag agrees with itself. To pin it, append the tag to the skill name (`ktl-docent@v0.16.0`) or pass `--pin`. `docs/install.md` carries the commands, the pinning rule, and what each skill needs on the machine.

The repository also carries its own bundle, kept by its own skills, so a reader can install the docent anywhere and ask about this project. The docent answers from this repository's `.lokf/`, saying how far each answer has been checked. Microsoft 365 Copilot is a fourth route for the docent alone. Each release that changes the bundle carries the docent as a zip with a snapshot of the bundle inside, to upload to a declarative agent ([The docent in Microsoft 365 Copilot](../playbooks/docent-in-m365-copilot.md)).

The repository was renamed, and GitHub redirects the old clone and `npx skills add` paths, as `CHANGELOG.md` records. The skills themselves took the `ktl-` prefix in 0.22.0. `CHANGELOG.md` lists their old names, and says that a host upgrading from 0.21.0 removes the old copies.
