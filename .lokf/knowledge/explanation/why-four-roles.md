---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/why-four-roles
title: Why four skill roles rather than one skill
description: Why the work is split into four skills - sidecar, librarian, curator, docent - named for the library and museum professions, run first in order and then as a loop, with a fifth, non-skill role (the registrar) described in why-a-registrar-role.md.
genre: explanation
resource: README.md
sources:
- resource: README.md
- resource: skills/ktl-librarian/SKILL.md
- resource: skills/ktl-docent/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-09-24T00:41:00Z"
status: draft
about:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-docent-skill
references:
  - https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/explanation/why-a-registrar-role
---

# Overview

The README names five roles, and four of them are skills: its section is "Four skills, three lines of the poem", after the three lines of Amy Lowell's *The Congressional Library* it opens with. The fifth, the **registrar**, is the toolkit and CI rather than a skill ([why a registrar role](why-a-registrar-role.md)).

Each skill takes one line of the poem, or the role the poem leaves implicit:

- **Sidecar** *lays the network*: lays down the `.lokf/` sidecar once, with `knowledge_bundle` as its visible doorway, and repairs a broken sidecar file.
- **Librarian** *binds it into order*: derives concepts from the repository with their sources, classifies and relates them, and hands off for review. Like a real librarian it catalogues without vouching - facts about the repository, never verdicts about truth.
- **Curator** *holds the scales*: a person's assistant that shows what needs a look, puts the source next to the claim, and records the person's verdict. Curator is the museum sense - the one who authenticates and weighs provenance - not the data-management sense, which is the librarian's job.
- **Docent** *guides the visitors*: answers from the bundle with each concept's trust label, and records what the bundle missed for the librarian's next run. Read-only on the bundle.

In short: the librarian reports, the curator fact-checks and edits, the docent reads and writes back what was missed.

On a fresh repository they run in order - sidecar, then librarian filling the bundle with drafts, then curator, where a person turns drafts into confirmed knowledge a few at a time. After that it is a loop: the librarian refreshes on a schedule, readers send back what the bundle missed, and the curator works through whatever that surfaces (`.assets/ktl-lifecycle-loop.svg`).

Each handoff is a frontmatter fact, not a convention: the librarian marks what it creates `status: draft`, a curator's `verified` event by a `human:` actor is what confirms it, and the docent's `.lokf/feedback.md` entries are what the librarian consumes next run.
