---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/why-four-roles
title: Why four skill roles rather than one skill
description: Why the work is split into four skills, sidecar, librarian, curator and docent, named for the library and museum professions and run first in order and then as a loop, beside a fifth role that is not a skill (the registrar) and two optional skills beside the roles (ktl-prose, and ktl-website, which publishes the bundle).
genre: explanation
resource: docs/architecture.md
sources:
  - resource: docs/architecture.md
  - resource: skills/ktl-librarian/SKILL.md
  - resource: skills/ktl-docent/SKILL.md
  - resource: docs/three-lines-critics.md
  - resource: docs/obsidian.md
generated:
  by: process:ktl-librarian
  at: "2026-10-15T01:30:10Z"
about:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-sidecar-skill
  - https://w3id.org/ktl/knowledge/playbooks/ktl-librarian-skill
  - https://w3id.org/ktl/knowledge/playbooks/ktl-curator-skill
  - https://w3id.org/ktl/knowledge/playbooks/ktl-docent-skill
references:
  - https://w3id.org/ktl/knowledge/glossary/trust-label
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/why-a-registrar-role
  - https://w3id.org/ktl/knowledge/playbooks/ktl-prose-skill
  - https://w3id.org/ktl/knowledge/explanation/three-lines-of-defence
verified:
  - by: process:ktl-librarian
    at: "2026-10-19T18:47:10Z"
  - by: human:noelmcloughlin
    at: "2026-10-19T20:46:38Z"
stale_after: 2027-10-19
---

# Overview

The architecture page names five roles, and four of them are skills. Its section is "Four skills, three lines of the poem", after the three lines of Amy Lowell's *The Congressional Library* it opens with. The fifth role, the **registrar**, is not a skill. It is the `lokf` toolkit, CI's gate, `knowledge-apply.sh` at the librarian's desk and `knowledge-report.sh` at the reader's desk and the curator's ([why a registrar role](why-a-registrar-role.md)). In Obsidian, where there is no CI, the optional KTL Registrar plugin does the registrar's work, checking each record as it is typed.

The page also names a fifth skill, which is not a role: `ktl-prose`, the librarian's copy editor, which rewords what an agent wrote, in plain English, before a person confirms it. It changes the wording and never a fact, it leaves every byte of frontmatter alone, and it never touches a concept a person wrote or confirmed. It is optional, and the roles lose nothing without it ([ktl-prose skill](../playbooks/ktl-prose-skill.md)).

The page names a sixth skill too, `ktl-website`, which publishes the bundle. It builds a website with a page per concept and its trust label, the health page, the knowledge graph and search by trust and type, and serves the four files `lokf export` writes beside the pages. The repository's README, docs, changelog and LinkML schema pages join them when it has them, and its data as SQLite databases to open in Datasette Lite once a person turns that on. A workflow publishes the site to GitHub Pages. It is optional, like `ktl-prose` ([ktl-website skill](../playbooks/ktl-website-skill.md)).

Each skill takes one line of the poem, or the role the poem leaves implicit, and the page's table says how often each runs:

- **Sidecar** *lays the network*, once: installs the `.lokf/` sidecar, with `knowledge_bundle` as its visible doorway, and repairs a broken sidecar file.
- **Librarian** *binds it into order*, often, including on a schedule: derives concepts from the repository with their sources, classifies and relates them, and hands off for review. Like a real librarian it catalogues without vouching: facts about the repository, never verdicts about truth.
- **Curator** *holds the scales*, a little, regularly: a person's assistant that shows what needs a look, puts the source next to the claim, and records the person's verdict. Curator is the museum sense (the one who authenticates, weighs provenance and decides what goes on exhibit), not the data-management sense, which is the librarian's job. The curator is always a person, and the skill and the plugin that carry the name reach no verdict of their own.
- **Docent** *guides the visitors*, whenever anyone asks: answers from the bundle with each concept's trust label, and records what the bundle missed for the librarian's next run. Like a real docent it explains the exhibition without moving anything on the shelves: read-only on the bundle.

On a fresh repository they run in order: sidecar, then librarian filling the bundle with drafts, then curator, where a person turns drafts into confirmed knowledge. After that it is a loop: the librarian refreshes on a schedule, readers report what the bundle missed, and the curator reviews what is new or changed.

In the three lines of defence that regulated industries use, the librarian and the curator are the first line, the registrar the second, and the bundle holds the evidence a third line would need ([three lines of defence](three-lines-of-defence.md)).

Each handoff is written down, not left to convention:

- the pen marks what the librarian creates `status: draft`;
- a curator's `verified` event by a `human:` actor confirms it;
- the librarian consumes the docent's `.lokf/feedback.md` entries on its next run.
