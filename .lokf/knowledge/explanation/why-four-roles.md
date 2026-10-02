---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/why-four-roles
title: "Why four skill roles rather than one skill"
description: "Why the work is split into four skills named for library and museum professions, sidecar, librarian, curator and docent, which run first in order and then as a loop, and why the fifth skill, ktl-prose, is a helper and not a role."
genre: explanation
resource: README.md
sources:
- resource: README.md
- resource: docs/three-lines.md
- resource: skills/ktl-librarian/SKILL.md
- resource: skills/ktl-prose/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
references:
  - https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
about:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-docent-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-prose-skill
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/explanation/why-a-registrar-role
  - https://knowledge-trust-ladder.example/knowledge/explanation/three-lines-of-defence
---

# Overview

The README puts the family in one line: an agent derives the bundle, deterministic tools check it, a named person vouches for it, and the bundle records which of the three happened to every claim. Each of those is a different kind of work, and the four skills divide it so that no skill does another's job.

# The four roles

The README names each role for a library or museum profession and says what it runs.

- The **sidecar** lays the network. It lays down the `.lokf/` sidecar, tooling, docs and a dummy skeleton, from bundled templates, with `knowledge_bundle` as its visible doorway. It runs once.
- The **librarian** binds it into order. It scrapes the repository, derives concepts with their sources, classifies them, wires typed relationships, audits, and hands off for review. Like a real librarian it catalogues without vouching: facts about the repository, never verdicts about truth. It runs often, including on a schedule.
- The **curator** holds the scales. It is a person's assistant: it shows what needs a look, puts the source next to the claim, and records the verdict in the bundle's own frontmatter. Judgments a person made, never facts it derived. It runs a little, regularly.
- The **docent** guides the visitors, the role the poem leaves implicit, because the collection exists for them. It answers from the bundle, labels how far each concept has been trusted, checks exact values at the source, and records what the bundle lacked. It is read-only on the bundle and runs whenever anyone asks.

The README adds the museum sense of each word. The curator authenticates, weighs provenance and decides what goes on exhibit; the data-management sense of "curation" is the librarian's job. The docent explains the exhibition without moving anything on the shelves.

# Why the split holds

The boundary is the trust ladder itself. `docs/three-lines.md` puts the librarian and the curator together in the first line as maker and checker: the agent cannot vouch, and the person does not derive. A librarian that could confirm its own work would make "confirmed by a person" mean nothing. A curator that derived facts would record an agent's text as a person's. The docent reads and writes back only what was missed, so readers' questions reach the librarian as untrusted input rather than as edits.

# First a sequence, then a loop

On a fresh repository the skills run in order: sidecar, then the librarian fills the bundle with drafts, then the curator, where a person turns drafts into confirmed knowledge a few at a time. After that it is a loop. The librarian refreshes on a schedule, readers send back what the bundle missed, and the curator works through whatever that surfaces. A fifth role, the registrar, is no skill at all: the toolkit and continuous integration keep the records in order.

# The fifth skill, which is not a role

`ktl-prose` is the librarian's copy editor. It rewords what an agent wrote, in plain English, before a person confirms it. It changes the wording and never a fact, leaves every byte of frontmatter alone, and never touches a concept a person wrote or confirmed. It is optional, and the four roles lose nothing without it.
