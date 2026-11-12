---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/domain-vocabulary
title: Domain vocabulary
description: The bundle's own LinkML file in `.lokf/schema/`, importing LOKF's schema, that declares the classes and keys its concepts may use beyond LOKF's. The `schema :=` line in `.lokf/justfile` names it, and `lokf validate --schema` checks the bundle against it.
definition: A LinkML file in `.lokf/schema/` that imports LOKF's schema and declares the extra classes and keys a bundle's concepts may use.
genre: reference
resource: skills/ktl-librarian/references/domain-vocabulary.md
sources:
  - resource: skills/ktl-librarian/references/domain-vocabulary.md
  - resource: skills/ktl-curator/references/domain-vocabularies.md
  - resource: docs/how-it-works.md
  - resource: docs/architecture.md
  - resource: CHANGELOG.md
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/domain-schemas
  - https://w3id.org/ktl/knowledge/glossary/domain-schema
  - https://w3id.org/ktl/knowledge/glossary/linkml
  - https://w3id.org/ktl/knowledge/glossary/lokf
generated:
  by: process:ktl-librarian
  at: "2026-11-12T14:55:35Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-11-12T18:05:07Z"
---

# Overview

LOKF's vocabulary is a short list of classes and typed relations, kept small so that bundles stay portable. Concepts typically stop fitting it in a deep or safety-critical domain, such as medicine, law, finance or safety engineering. The answer is then a **domain vocabulary**: a file written in [LinkML](linkml.md) that imports [LOKF](lokf.md)'s schema and declares the classes and keys the bundle needs, so the domain's own types are checked rather than tolerated ([when the built-in vocabulary stops fitting](../explanation/domain-schemas.md)). The [curator](curator.md) flags concepts that no longer fit, the team decides, and the [librarian](librarian.md) applies it.

It sits in `.lokf/schema/`, beside a pinned copy of LOKF's `lokf.yaml`. The `schema :=` line in `.lokf/justfile` names it, and the recipes pass it to `lokf validate` as `--schema`. A file that imports `lokf` belongs in `.lokf/schema/`.

A domain vocabulary is not a [domain schema](domain-schema.md), which models a domain in a LinkML project and never imports LOKF. `lokf adapt` reads a domain schema and writes a domain vocabulary from it, and the librarian writes one by hand when only the bundle needs it. LOKF's specification and the toolkit's messages call this file a *LOKF domain schema*.

Since 0.44.0 one domain vocabulary is released with the sidecar: `domain.yaml`, for a bundle that federates other bundles, as the curator's `domain-vocabularies.md` says. When bundles are federated, each domain vocabulary is released with its bundle.
