---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/registrar
title: Registrar
description: "The person in a museum who keeps the collection's records, and Knowledge Trust Ladder's fifth role, which programs play: the `lokf` toolkit, the gate `knowledge-registrar.yaml` (or `knowledge-provenance.sh` on another forge or none), the pen and the report script."
definition: In a museum, the person who keeps the collection's records. In Knowledge Trust Ladder, the role that keeps the bundle's records in order and ties each confirmation to the person who gave it, which no person has to play.
genre: reference
resource: docs/architecture.md
sources:
  - resource: docs/architecture.md
  - resource: docs/for-the-curious.md
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/why-a-registrar-role
  - https://w3id.org/ktl/knowledge/glossary/the-pen
  - https://w3id.org/ktl/knowledge/glossary/desk
generated:
  by: process:ktl-librarian
  at: "2026-10-18T10:22:18Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-19T23:21:13Z"
---

# Overview

A *registrar* is the person in a museum who keeps the collection's records. The architecture page names Knowledge Trust Ladder's fifth role after it: the registrar "keeps the records in order: each accession (an item added to the collection) documented, its provenance filed, nothing entered in a form the catalogue can't read".

No person has to play the role. The `lokf` toolkit checks every change, and CI's `knowledge-registrar.yaml` checks every pull request that touches the bundle. There it also ties each confirmation that is added or removed to that person's approval or signed commit. On another forge, or with none, `knowledge-provenance.sh` checks each confirmation's signature against the keys under `.lokf/curators/` instead. At the librarian's desk the registrar is `knowledge-apply.sh`, the pen, and at the reader's desk and the curator's it is `knowledge-report.sh`. In Obsidian, the KTL Registrar plugin checks each record as it is typed.
