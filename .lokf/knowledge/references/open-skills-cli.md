---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/open-skills-cli
title: "Open Skills CLI (npx skills)"
description: "The vendor-neutral installer for agent skills, `npx skills add`, which takes a GitHub repository, a git URL or a local path and repeatable --skill selections."
genre: reference
resource: https://github.com/vercel-labs/skills
sources:
- resource: https://github.com/vercel-labs/skills
- resource: docs/install.md
- resource: README.md
- resource: scripts/smoke-test-install.sh
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/references/gh-skill-cli
  - https://knowledge-trust-ladder.example/knowledge/playbooks/repository-validation
definedBy:
  - https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
---

# Overview

`npx skills add` is the installer the README leads with: `npx skills add noelmcloughlin/knowledge-trust-ladder --skill ktl-docent --yes` installs the docent into any agent a person already uses. `docs/install.md` gives the form that installs all five skills at once, each named with its own `--skill` flag, and `--pin v0.16.0` pins them to one tag.

# How this repository uses it

`CONTRIBUTING.md` names `npx skills add ./knowledge-trust-ladder --skill ktl-sidecar` as the way to install from a local clone. The smoke test in `scripts/smoke-test-install.sh` installs every skill the same way into a throwaway repository and checks that each is discovered, that its files arrived, and that `ktl-prose`'s installed script runs. Continuous integration runs that test on every pull request, with Node set up for `npx`.

The threat model notes that `npx skills` prints a warning after every install that a skill's scope line is prose, not a checked permission.
