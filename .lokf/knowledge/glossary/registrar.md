---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/registrar
title: Registrar
description: "The person in a museum who keeps the collection's records, and Knowledge Trust Ladder's fifth role, which programs play: the `lokf` toolkit, the gate `knowledge-registrar.yaml`, the pen and the report script."
definition: In a museum, the person who keeps the collection's records. In Knowledge Trust Ladder, the role that keeps the bundle's records in order and ties each confirmation to the person who gave it, which no person has to play.
genre: reference
resource: README.md
sources:
- resource: README.md
- resource: docs/for-the-curious.md
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/explanation/why-a-registrar-role
- https://knowledge-trust-ladder.example/knowledge/glossary/the-pen
- https://knowledge-trust-ladder.example/knowledge/glossary/desk
generated:
  by: process:ktl-librarian
  at: "2026-10-04T18:03:25Z"
status: draft
verified:
- by: process:ktl-librarian
  at: "2026-10-06T09:49:14Z"
---

# Overview

A *registrar* is the person in a museum who keeps the collection's records. The README names Knowledge Trust Ladder's fifth role after it: the registrar "keeps the records themselves in order: each accession (an item added to the collection) documented, its provenance filed, nothing entered in a form the catalogue can't read".

No person has to play the role. The `lokf` toolkit checks every change, and CI's `knowledge-registrar.yaml` checks every pull request that touches the bundle. There it also ties each confirmation that is added or removed to that person's approval or signed commit. At the librarian's desk the registrar is `knowledge-apply.sh`, the pen, and at the reader's desk and the curator's it is `knowledge-report.sh`. In Obsidian, the KTL Registrar plugin checks each record as it is typed.
