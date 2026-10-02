---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/gh-skill-cli
title: "gh skill (GitHub CLI)"
description: "The GitHub CLI command group that installs, pins and publishes agent skills from GitHub repositories. It is the publish path this repository's releases use."
genre: reference
resource: https://cli.github.com/manual/gh_skill_install
sources:
- resource: https://cli.github.com/manual/gh_skill_install
- resource: docs/install.md
- resource: .github/workflows/publish.yml
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/releasing
  - https://knowledge-trust-ladder.example/knowledge/references/open-skills-cli
definedBy:
  - https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
---

# Overview

`gh skill` is a command group of the GitHub CLI, from version 2.90.0. `docs/install.md` gives the install form for each skill, `gh skill install noelmcloughlin/knowledge-trust-ladder ktl-docent`, and a tag can be appended to the skill name to pin it, as `ktl-docent@v0.16.0`.

# How this repository uses it

`gh skill publish` is the one tag creator in this repository's release path. The `publish.yml` workflow runs `gh skill publish --dry-run` to check the skills against the Agent Skills specification, then `gh skill publish --tag <version>` to create the tag and the GitHub release. That is why no workflow here is tag-triggered: a tag trigger would race the tag `gh skill publish` is about to create.

`CONTRIBUTING.md` names `gh skill install ./knowledge-trust-ladder ktl-sidecar --from-local` as the way to try a change end to end from a local clone.
