---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
title: "Agent Skills specification"
description: "The specification that defines a skill directory: a required SKILL.md with name and description frontmatter, plus optional scripts/, references/ and assets/ folders."
genre: reference
resource: https://agentskills.io/home
sources:
- resource: https://agentskills.io/home
- resource: README.md
- resource: scripts/validate-repository.sh
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/repository-validation
  - https://knowledge-trust-ladder.example/knowledge/references/gh-skill-cli
  - https://knowledge-trust-ladder.example/knowledge/references/open-skills-cli
---

# Overview

The README calls the five skills Agent Skills and links to agentskills.io. Under that specification a skill is a directory holding a `SKILL.md` whose frontmatter carries at least `name` and `description`, with optional `scripts/`, `references/` and `assets/` folders beside it.

# How this repository uses it

Each skill under `skills/` follows that layout. Its `SKILL.md` is a lean router, and anything not needed on every invocation sits in `references/`, loaded only when the router points to it. `ktl-prose` is the one skill with a `scripts/` folder, which holds the check script it runs in place.

The repository contract checks the frontmatter of every `SKILL.md`: its `name` matches the directory, its `description` stays within the length the specification allows and ends with a `Keywords:` list, and `license` and `compatibility` are present. `gh skill publish --dry-run` checks the same layout against the specification in continuous integration, and the smoke test installs every skill into a throwaway repository.
