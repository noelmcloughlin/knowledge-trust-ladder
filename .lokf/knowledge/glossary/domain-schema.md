---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/domain-schema
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
- https://knowledge-trust-ladder.example/knowledge/explanation/domain-schemas
- https://knowledge-trust-ladder.example/knowledge/glossary/linkml
- https://knowledge-trust-ladder.example/knowledge/glossary/lokf
generated:
  by: process:ktl-librarian
  at: "2026-10-13T15:08:54Z"
status: draft
---

# Overview

LOKF's vocabulary is a short list of classes and typed relations. It is kept small, which is what keeps bundles portable. When concepts stop fitting those classes, it is typically in a deep or safety-critical domain: medicine, law, finance, safety engineering. The answer is a **domain schema** written in [LinkML](linkml.md) that extends [LOKF](lokf.md)'s, not a looser bundle. The [curator](curator.md) flags the drift, the team decides, and the [librarian](librarian.md) applies it.

The architecture page says that a domain that extends the schema has its own types checked rather than tolerated ([when the built-in vocabulary stops fitting](../explanation/domain-schemas.md)).
