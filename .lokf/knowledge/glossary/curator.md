---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/curator
title: Curator
description: "The role that holds the scales, always a person: in the museum sense, the one who authenticates, weighs provenance and decides what goes on exhibit. The ktl-curator skill and the KTL Curator plugin are that person's assistants, and reach no verdict of their own."
definition: "The role, always played by a person, that records a verdict on a concept against its source: confirm, correct, retire or send back. Curator is the museum sense, the one who authenticates, weighs provenance and decides what goes on exhibit, not the data-management sense, which is the librarian's job."
genre: reference
resource: docs/architecture.md
sources:
- resource: docs/architecture.md
- resource: docs/for-the-curious.md
- resource: docs/obsidian.md
- resource: skills/ktl-curator/SKILL.md
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
- https://knowledge-trust-ladder.example/knowledge/glossary/librarian
- https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
- https://knowledge-trust-ladder.example/knowledge/glossary/health-line
generated:
  by: process:ktl-librarian
  at: "2026-10-13T15:08:54Z"
status: draft
verified:
- by: process:ktl-librarian
  at: "2026-10-14T00:35:00Z"
---

# Overview

The architecture page names a role after the museum profession: the **curator** *holds the scales*. Curator is the museum sense, the one who authenticates, weighs provenance and decides what goes on exhibit. It is not the data-management sense, which is the [librarian](librarian.md)'s job.

The curator is always a person. The `ktl-curator` skill is that person's assistant: it shows what needs a look, puts the source next to the claim, and records the verdict (confirm, correct, retire, send back) in the bundle's own frontmatter. It records judgments a person made, never facts it derived, and it runs a little, regularly ([ktl-curator skill](../playbooks/ktl-curator-skill.md)). In Obsidian, the KTL Curator plugin is the same assistant. The skill and the plugin that carry the name reach no verdict of their own.

A verdict is a `verified` event in that person's name, or a change of `status` or review date, with one line in `log.md`. A concept a person checked against its source reads *confirmed by a person*, the top [trust label](trust-label.md), and the [health line](health-line.md) counts how many do.
