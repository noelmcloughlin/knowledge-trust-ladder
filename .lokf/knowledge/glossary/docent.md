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
- resource: README.en-simple.md
- resource: skills/ktl-docent/SKILL.md
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-docent-skill
- https://knowledge-trust-ladder.example/knowledge/explanation/why-four-roles
- https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
generated:
  by: process:ktl-librarian
  at: "2026-10-12T03:11:32Z"
status: draft
verified:
- by: process:ktl-librarian
  at: "2026-10-12T00:29:45Z"
---

# Overview

A *docent* is a museum's name for a guide, as the README for readers aged 13 to 18 says. The README says that a docent "explains the exhibition without moving anything on the shelves". ktl-docent opens the same way: "A docent guides visitors through an exhibition. This skill guides an agent through the `.lokf/` knowledge bundle."

In the README's table of roles the docent *guides the visitors*, the role the poem leaves implicit, because the collection exists for them. It answers from the bundle, labels how far each concept has been trusted, and checks exact values at the source. When the bundle has no answer, it explores the repository and records the miss in `.lokf/feedback.md` through its own copy of `knowledge-feedback.sh`. The miss becomes the librarian's next task. It writes nothing in the bundle.
