---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/domain-schema
title: Domain schema
description: "A LinkML schema that models a domain, owned by a LinkML project in `src/<slug>/schema/` or `.linkml/src/<slug>/schema/`. It never imports LOKF's schema: a bundle borrows its classes through the domain vocabulary that `lokf adapt` writes from it into `.lokf/schema/`."
definition: A LinkML schema that models a domain; a LinkML project owns it, and it never imports LOKF's schema.
genre: reference
resource: docs/for-the-curious.md
sources:
  - resource: docs/for-the-curious.md
  - resource: skills/ktl-librarian/references/domain-vocabulary.md
  - resource: skills/ktl-curator/references/domain-vocabularies.md
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/domain-schemas
  - https://w3id.org/ktl/knowledge/glossary/domain-vocabulary
  - https://w3id.org/ktl/knowledge/glossary/linkml
  - https://w3id.org/ktl/knowledge/glossary/lokf
generated:
  by: process:ktl-librarian
  at: "2026-11-12T14:46:38Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-11-02T13:29:19Z"
---

# Overview

A **domain schema** is a [LinkML](linkml.md) schema that models a domain: what the domain's data looks like. A LinkML project owns it, in `src/<slug>/schema/` or `.linkml/src/<slug>/schema/`, in this repository or another, and it never imports [LOKF](lokf.md)'s schema.

A bundle never names a domain schema on its `schema :=` line. `lokf adapt` reads the schema and writes a copy into `.lokf/schema/`, and the bundle's [domain vocabulary](domain-vocabulary.md) imports that copy or is that copy. A file that imports `lokf` belongs in `.lokf/schema/`, and a domain schema never does. LOKF's specification and the toolkit's messages call the bundle's file a *LOKF domain schema*, which is the other file.

When the classes a bundle needs amount to a model of the domain, the curator's `domain-vocabularies.md` says to write that model as a domain schema, in a LinkML project with lint, tests and a docs site, and adapt it into the bundle. The linkml-sidecar skills install such a project beside the bundle, or around a schema the repository already holds. A domain that already has one, such as AI governance with IBM AI Atlas Nexus's AI Risk Ontology, is reused that way rather than described again.
