---
type: Reference
id: https://w3id.org/ktl/knowledge/references/agent-skills-specification
title: Agent Skills specification
description: The specification defining a skill directory - a required SKILL.md with name/description frontmatter, plus optional scripts/, references/, and assets/.
genre: reference
resource: https://agentskills.io/specification
generated:
  by: human:noelmcloughlin
  at: "2026-10-13T00:48:53Z"
verified:
- by: human:noelmcloughlin
  at: "2026-09-09T16:35:55Z"
- by: human:noelmcloughlin
  at: "2026-09-26T20:33:12Z"
- by: process:ktl-librarian
  at: "2026-10-12T03:11:32Z"
- by: human:noelmcloughlin
  at: "2026-10-13T00:48:53Z"
stale_after: 2027-09-26
---

# Overview

Defines the unit this repository distributes. Each skill is a directory with a
`SKILL.md` whose frontmatter carries `name` (matching the directory)
and `description`; supporting files may sit alongside it and travel with the
directory when installed.

Two consequences shape the layout here: the `description` is always resident in
the calling agent's context, while the body loads
only on trigger - which is why each `SKILL.md` is a lean router and detail
lives in `references/`. The spec's ~100 tokens covers `name` and `description` together, and is a startup estimate, not a rule. This repo only enforces 1024 characters (`validate-repository.sh`). `gh skill publish --dry-run` validates conformance in
CI on every pull request.
