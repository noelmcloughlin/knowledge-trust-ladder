---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/domain-schema
title: Domain schema
description: A schema written in LinkML that extends LOKF's, for a domain whose concepts stop fitting LOKF's short list of classes, so the domain's own types are checked rather than tolerated. The curator flags concepts that no longer fit, the team decides, and the librarian applies it.
definition: A schema written in LinkML that extends LOKF's, for a domain whose concepts stop fitting LOKF's classes.
genre: reference
resource: docs/for-the-curious.md
sources:
  - resource: docs/for-the-curious.md
  - resource: docs/architecture.md
  - resource: skills/ktl-curator/references/domain-schemas.md
  - resource: CHANGELOG.md
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/domain-schemas
  - https://w3id.org/ktl/knowledge/glossary/linkml
  - https://w3id.org/ktl/knowledge/glossary/lokf
generated:
  by: process:ktl-librarian
  at: "2026-10-26T20:05:58Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-29T00:48:33Z"
---

# Overview

LOKF's vocabulary is a short list of classes and typed relations, kept small so that bundles stay portable. Concepts typically stop fitting those classes in a deep or safety-critical domain, such as medicine, law, finance or safety engineering. The answer is then a **domain schema** written in [LinkML](linkml.md) that extends [LOKF](lokf.md)'s. The [curator](curator.md) flags concepts that no longer fit, the team decides, and the [librarian](librarian.md) applies it.

The architecture page says that a domain that extends the schema has its own types checked rather than tolerated ([when the built-in vocabulary stops fitting](../explanation/domain-schemas.md)).

Since 0.44.0 one domain schema is released with the sidecar: `domain.yaml`, for a bundle that federates other bundles, as the curator's `domain-schemas.md` says.

A domain schema that grows past a few classes is worth a project of its own, with lint, tests and a docs site. The linkml-sidecar skills install one beside the bundle, or around a schema the repository already holds, as the curator's `domain-schemas.md` says since 0.55.1.
