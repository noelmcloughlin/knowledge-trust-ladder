---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/docent
title: Docent
description: A museum's name for a guide, and the role that answers a reader's questions from the bundle, says how far each answer has been checked, and writes nothing in the bundle.
definition: A museum's name for a guide, who explains the exhibition to visitors without moving anything on the shelves. In Knowledge Trust Ladder it names the role that answers questions from the bundle and labels how far each concept has been trusted, which the ktl-docent skill plays.
genre: reference
resource: docs/architecture.md
sources:
  - resource: docs/architecture.md
  - resource: docs/architecture.en-simple.md
  - resource: skills/ktl-docent/SKILL.md
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-docent-skill
  - https://w3id.org/ktl/knowledge/explanation/why-four-roles
  - https://w3id.org/ktl/knowledge/glossary/trust-label
generated:
  by: process:ktl-librarian
  at: "2026-10-13T15:08:54Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-19T23:21:13Z"
---

# Overview

A *docent* is a museum's name for a guide, as the retelling for readers aged 13 to 18 says. The architecture page says that a docent "explains the exhibition without moving anything on the shelves". ktl-docent opens the same way: "A docent guides visitors through an exhibition. This skill guides an agent through the `.lokf/` knowledge bundle."

In the architecture page's table of roles the docent *guides the visitors*, the role the poem leaves implicit, because the collection exists for them. It answers from the bundle, labels how far each concept has been trusted, and checks exact values at the source. When the bundle has no answer, it explores the repository and records the miss in `.lokf/feedback.md` through its own copy of `knowledge-feedback.sh`. The miss becomes the librarian's next task. It writes nothing in the bundle.
