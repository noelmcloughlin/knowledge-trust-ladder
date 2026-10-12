---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/why-four-roles
title: Why four skill roles rather than one skill
description: Why the work is split into four skills, sidecar, librarian, curator and docent, named for the library and museum professions and run first in order and then as a loop, beside a fifth role that is not a skill (the registrar) and a fifth skill that is not a role (ktl-prose).
genre: explanation
resource: README.md
sources:
- resource: README.md
- resource: skills/ktl-librarian/SKILL.md
- resource: skills/ktl-docent/SKILL.md
- resource: docs/three-lines-critics.md
generated:
  by: process:ktl-librarian
  at: "2026-10-12T16:08:20Z"
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
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-prose-skill
verified:
- by: process:ktl-librarian
  at: "2026-10-12T23:54:05Z"
---

# Overview

The README names five roles, and four of them are skills. Its section is "Four skills, three lines of the poem", after the three lines of Amy Lowell's *The Congressional Library* it opens with. The fifth role, the **registrar**, is not a skill. It is the `lokf` toolkit, CI's gate, `knowledge-apply.sh` at the librarian's desk, `knowledge-report.sh` at the reader's desk and the curator's, and two optional Obsidian plugins ([why a registrar role](why-a-registrar-role.md)). The README also names a fifth skill, which is not a role: `ktl-prose`, the librarian's optional copy editor, which rewords what an agent wrote before a person confirms it. The roles lose nothing without it ([ktl-prose skill](../playbooks/ktl-prose-skill.md)).

Each skill takes one line of the poem, or the role the poem leaves implicit:

- **Sidecar** *lays the network*: installs the `.lokf/` sidecar once, with `knowledge_bundle` as its visible doorway, and repairs a broken sidecar file.
- **Librarian** *binds it into order*: derives concepts from the repository with their sources, classifies and relates them, and hands off for review. Like a real librarian it catalogues without vouching: facts about the repository, never verdicts about truth.
- **Curator** *holds the scales*: a person's assistant that shows what needs a look, puts the source next to the claim, and records the person's verdict. Curator is the museum sense (the one who authenticates and weighs provenance), not the data-management sense, which is the librarian's job.
- **Docent** *guides the visitors*: answers from the bundle with each concept's trust label, and records what the bundle missed for the librarian's next run. Like a real docent it explains the exhibition without moving anything on the shelves: read-only on the bundle.

On a fresh repository they run in order: sidecar, then librarian filling the bundle with drafts, then curator, where a person turns drafts into confirmed knowledge. After that it is a loop: the librarian refreshes on a schedule, readers report what the bundle missed, and the curator reviews what is new or changed.

Each handoff is written down, not left to convention:

- the pen marks what the librarian creates `status: draft`;
- a curator's `verified` event by a `human:` actor confirms it;
- the librarian consumes the docent's `.lokf/feedback.md` entries on its next run.
