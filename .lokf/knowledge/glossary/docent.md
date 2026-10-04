---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/docent
title: Docent
description: A museum's name for a guide, and the role that answers a reader's questions from the bundle, says how far each answer has been checked, and writes nothing in the bundle.
definition: A museum's name for a guide, who explains the exhibition to visitors without moving anything on the shelves. In Knowledge Trust Ladder it names the role that answers questions from the bundle and labels how far each concept has been trusted, which the ktl-docent skill plays.
genre: reference
resource: README.md
sources:
- resource: README.md
- resource: skills/ktl-docent/SKILL.md
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-docent-skill
- https://knowledge-trust-ladder.example/knowledge/explanation/why-four-roles
- https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
generated:
  by: process:ktl-librarian
  at: "2026-10-04T17:49:16Z"
status: draft
---

# Overview

A *docent* is a museum's name for a guide. The README says so where it first names the docent, and later adds that a docent "explains the exhibition without moving anything on the shelves". ktl-docent opens the same way: "A docent guides visitors through an exhibition. This skill guides an agent through the `.lokf/` knowledge bundle."

In the README's table of roles the docent *guides the visitors*, the role the poem leaves implicit, because the collection exists for them. It answers from the bundle, labels how far each concept has been trusted, and checks exact values at the source. When the bundle has no answer, it explores the repository and records the miss in `.lokf/feedback.md` through `knowledge-feedback.sh`, and the miss becomes the librarian's next task. It writes nothing in the bundle.
