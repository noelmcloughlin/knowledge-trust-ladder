---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/domain-schema
title: Domain schema
description: A schema written in LinkML that extends LOKF's, for a domain whose concepts stop fitting LOKF's short list of classes, so the domain's own types are checked rather than tolerated. The curator flags the drift, the team decides, and the librarian applies it.
definition: A schema written in LinkML that extends LOKF's, for a domain whose concepts stop fitting LOKF's classes.
genre: reference
resource: docs/for-the-curious.md
sources:
  - resource: docs/for-the-curious.md
  - resource: docs/architecture.md
  - resource: skills/ktl-curator/references/domain-schemas.md
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/domain-schemas
  - https://w3id.org/ktl/knowledge/glossary/linkml
  - https://w3id.org/ktl/knowledge/glossary/lokf
generated:
  by: process:ktl-librarian
  at: "2026-10-16T23:58:13Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-19T20:01:11Z"
---

# Overview

LOKF's vocabulary is a short list of classes and typed relations, kept small so that bundles stay portable. Concepts stop fitting those classes typically in a deep or safety-critical domain, such as medicine, law, finance or safety engineering. The answer is then a **domain schema** written in [LinkML](linkml.md) that extends [LOKF](lokf.md)'s. The [curator](curator.md) flags the drift, the team decides, and the [librarian](librarian.md) applies it.

The architecture page says that a domain that extends the schema has its own types checked rather than tolerated ([when the built-in vocabulary stops fitting](../explanation/domain-schemas.md)).

Since 0.44.0 one domain schema is released with the sidecar: `domain.yaml`, for a bundle that federates other bundles, as the curator's `domain-schemas.md` says.
