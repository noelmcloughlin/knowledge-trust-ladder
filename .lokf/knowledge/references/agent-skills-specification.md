---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
title: Agent Skills specification
description: The specification defining a skill directory - a required SKILL.md with name/description frontmatter, plus optional scripts/, references/, and assets/.
genre: reference
resource: https://agentskills.io/home
generated:
  by: process:ktl-librarian
  at: "2026-09-09T10:00:00Z"
verified:
- by: process:ktl-librarian
  at: "2026-09-24T01:25:00Z"
- by: human:noelmcloughlin
  at: "2026-09-09T18:30:00Z"
stale_after: 2027-09-09
---

# Overview

Defines the unit this repository distributes. Each skill is a directory with a
case-exact `SKILL.md` whose frontmatter carries `name` (matching the directory)
and `description`; supporting files may sit alongside it and travel with the
directory when installed.

Two consequences shape the layout here: the `description` is always resident in
the calling agent's context, so it is kept near 100 words, while the body loads
only on trigger - which is why each `SKILL.md` is a lean router and detail
lives in `references/`. `gh skill publish --dry-run` validates conformance in
CI on every pull request.
