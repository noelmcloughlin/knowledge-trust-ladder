---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/linkml
title: LinkML
description: The schema language LOKF is written in, created by the LinkML Community. LOKF's specification is a single LinkML schema, from which the JSON Schema, JSON-LD context, SHACL shapes and OWL ontology are generated, and a domain schema that extends it is written in LinkML too.
definition: The schema language LOKF is written in, created by the LinkML Community. LOKF's specification is a single LinkML schema, `lokf.yaml`.
genre: reference
resource: docs/architecture.md
sources:
  - resource: docs/architecture.md
  - resource: docs/for-the-curious.md
  - resource: skills/ktl-librarian/SKILL.md
  - resource: skills/ktl-curator/references/domain-schemas.md
definedBy:
  - https://w3id.org/ktl/knowledge/references/linkml
relatedTo:
  - https://w3id.org/ktl/knowledge/glossary/lokf
  - https://w3id.org/ktl/knowledge/glossary/domain-schema
generated:
  by: process:ktl-librarian
  at: "2026-10-13T15:08:54Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-28T00:35:16Z"
---

# Overview

LinkML is the schema language [LOKF](lokf.md) is written in, and its creators are the LinkML Community. LOKF's specification is a single LinkML schema, `lokf.yaml`. The JSON Schema, JSON-LD context, SHACL shapes and OWL ontology are generated from it and never edited by hand, and this bundle consumes that schema.

A [domain schema](domain-schema.md) that extends LOKF's is written in LinkML too, so that one schema serves the people who think in JSON, Python or docs pages and the people who think in graphs. The scaffolded sidecar depends on `lokf[build]`, whose `[build]` extra installs the `linkml` package, the full generator suite, so a domain schema costs no new installation.
