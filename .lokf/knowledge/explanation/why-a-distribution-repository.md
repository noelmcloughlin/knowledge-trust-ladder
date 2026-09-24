---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/why-a-distribution-repository
title: Why the skills live in their own repository
description: Why the four skills are published from one installable repository - three install routes, one tag for all four, one changelog - and answer from this repository's own bundle.
genre: explanation
resource: README.md
sources:
- resource: README.md
- resource: docs/install.md
- resource: .claude-plugin/marketplace.json
generated:
  by: process:ktl-librarian
  at: "2026-09-24T00:41:00Z"
status: draft
references:
  - https://knowledge-trust-ladder.example/knowledge/references/gh-skill-cli
  - https://knowledge-trust-ladder.example/knowledge/references/open-skills-cli
  - https://knowledge-trust-ladder.example/knowledge/policies/versioning
---

# Overview

The four skills are installed from this repository rather than copied into each project that uses them. Each skill stands alone, and there are three routes to the same set: the GitHub CLI (`gh skill install noelmcloughlin/knowledge-trust-ladder <skill>`), the Open Skills CLI (`npx skills add noelmcloughlin/knowledge-trust-ladder --skill <skill>`), and, since 2026-09-19, a Claude Code plugin that bundles all four (`/plugin marketplace add noelmcloughlin/knowledge-trust-ladder`, then `/plugin install knowledge-trust-ladder@knowledge-trust-ladder`), declared by `.claude-plugin/plugin.json` and `marketplace.json`.

All four skills release together under one `vMAJOR.MINOR.PATCH` tag with one `CHANGELOG.md`, so a set pinned to one tag agrees with itself: append the tag to the skill name (`ktl-docent@v0.16.0`) or pass `--pin`. `docs/install.md` carries the commands, the pinning rule, and what each skill needs on the machine.

The repository also carries its own bundle, kept by its own skills, so a reader can install the docent anywhere and ask about this project: it answers from this repository's `.lokf/`, saying how far each answer has been checked.

The repository was renamed on 2026-09-19; GitHub redirects the old links, clones and `npx skills add` paths, so an existing install keeps working. `docs/install.md` records the old name, and check 16 keeps it out of every file that does not record history - this concept included.

## Open questions

- 2026-09-24, process:ktl-librarian: `docs/install.md` says of the repository rename that "the skill names are unchanged", but the skills were renamed from `lokf-*` to `ktl-*` in #64 (2026-09-23), and check 16a now blocks the old names. The source needs a one-line fix; until then this concept leaves the claim out.
