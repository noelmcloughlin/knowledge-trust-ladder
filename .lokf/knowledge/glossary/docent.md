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
  - resource: docs/cast/docent.md
    id: cast-docent.md
    excerpt: Like a real docent it explains the exhibition and moves nothing on the shelves.
  - resource: skills/ktl-docent/SKILL.md
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-docent-skill
  - https://w3id.org/ktl/knowledge/explanation/why-four-roles
  - https://w3id.org/ktl/knowledge/glossary/trust-label
generated:
  by: process:ktl-librarian
  at: "2026-11-13T14:41:35Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-29T00:48:33Z"
---

# Overview

A *docent* is a museum's name for a guide, as the retelling for readers aged 13 to 18 says. The docent's own page says that, like a real docent, it "explains the exhibition and moves nothing on the shelves".[^cast-docent.md] ktl-docent opens the same way: "A docent guides visitors through an exhibition. This skill guides an agent through the `.lokf/` knowledge bundle."

In the architecture page's table of roles the docent *guides the visitors*, the role the poem leaves implicit, because the collection exists for its visitors. It runs whenever anyone asks, and it is read-only on the bundle. It answers from the bundle first, and names each concept the answer rests on with its trust label. It opens the source before it states a version, a number or a path. When the bundle has no answer, it explores the repository and records the miss in `.lokf/feedback.md` through its own copy of `knowledge-feedback.sh`. The librarian handles that record on its next run. The docent writes nothing in the bundle.

[^cast-docent.md]: docs/cast/docent.md, the opening paragraph
