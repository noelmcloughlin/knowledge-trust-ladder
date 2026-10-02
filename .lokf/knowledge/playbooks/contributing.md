---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/contributing
title: "Contributing"
description: "How to work on the skills: no build step, the local checks to run before opening a pull request, the role boundary a change must respect, the code of conduct and the AI covenant, and what maintainers do to release."
genre: how-to
resource: CONTRIBUTING.md
sources:
- resource: CONTRIBUTING.md
- resource: docs/repository-layout.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
references:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/repository-validation
  - https://knowledge-trust-ladder.example/knowledge/playbooks/releasing
  - https://knowledge-trust-ladder.example/knowledge/policies/ai-covenant
  - https://knowledge-trust-ladder.example/knowledge/policies/code-of-conduct
  - https://knowledge-trust-ladder.example/knowledge/policies/versioning
---

# Overview

`CONTRIBUTING.md` is a checklist, not a design log. Each rule is a line or two that links to where its reasoning lives, and the repository contract holds the file to a word budget so it stays that way.

# Development setup

There is no build step: the skills are Markdown, YAML, shell and one Python script. Clone the repository and run `bash scripts/validate-repository.sh`. To try a change end to end before publishing, install from the local clone with `gh skill install ./knowledge-trust-ladder ktl-sidecar --from-local` or `npx skills add ./knowledge-trust-ladder --skill ktl-sidecar`.

# Layout

Each `SKILL.md` is a lean router, and detail lives in that skill's `references/`, loaded only when the router points to it. `skills/ktl-sidecar/templates/` holds every file the sidecar writes, copied verbatim. `skills/ktl-prose/scripts/prose-check.py` is that skill's check. `scripts/` holds the repository contract continuous integration runs on every pull request. `docs/repository-layout.md` shows the whole tree.

# Before opening a pull request

- Run `bash scripts/validate-repository.sh`. Continuous integration runs the same script plus ShellCheck, actionlint, markdownlint, lychee and codespell.
- Run `gh skill publish --dry-run` if you have the GitHub CLI.
- If a change alters what a skill does, add a line or two under `## [Unreleased]` in `CHANGELOG.md`.
- Files here are deep-linked from the sibling repositories; check 9 lists the paths. Move one only together with their links, and land this side first.
- Copy a change under `skills/ktl-sidecar/templates/` over this repository's own copy in the same pull request; check 11 holds each pair byte-identical.
- When the commits would release, give the pull request title the releasing type too, because a squash merge takes its subject from the title.
- Sign a pull request that records a `human:` confirmation.

# Editing scope

This repository packages and distributes the four skills and the `ktl-prose` helper. A change to what an agent should actually do needs its why in the pull request, and it must keep the role boundary intact. The librarian derives facts from the repository and never vouches for them. The curator records a person's verdicts and never derives facts. `ktl-prose` changes wording and never a fact, a frontmatter byte or a concept a person vouched for.

# Conduct and AI tools

Participation is covered by the Contributor Covenant. AI assistance is welcome; these skills exist for agents to run. The contributor is still the author of whatever they submit, responsible for understanding and defending it in review, and an agent may not take part in discussion on their behalf. `AI_COVENANT.md` has the full rules.

# Releasing

Commits typed with Conventional Commits decide the version, `## [Unreleased]` is the release note, `semantic-release.yml` promotes the changelog on a merge to `main` but never tags, and a maintainer runs `publish.yml` by hand with the version to ship. After a release that changes a template or `skills/ktl-librarian/`, `scripts/sync-sidecar.sh` carries it to the sibling repositories.
