---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/accession
title: Accession
description: A museum's word for an item added to its collection, which the README's registrar keeps documented with its provenance filed; in the bundle, each concept added is one.
definition: A museum's word for an item added to its collection. The README says the registrar keeps each accession documented and its provenance filed.
genre: reference
resource: README.md
sources:
- resource: README.md
- resource: skills/ktl-librarian/references/golden-rules.md
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/glossary/registrar
generated:
  by: process:ktl-librarian
  at: "2026-10-04T18:03:25Z"
status: draft
---

# Overview

An *accession* is a museum's word for an item added to its collection. The README uses it where it says what the registrar does: the registrar "keeps the records themselves in order: each accession (an item added to the collection) documented, its provenance filed, nothing entered in a form the catalogue can't read".

In the bundle, the item added is a concept. Its record is its frontmatter: the `sources` it derives from, and the `generated` stamp that says who or what produced its content, and when. The `lokf` toolkit checks every change, and CI's `knowledge-registrar.yaml` checks every pull request that touches the bundle.
