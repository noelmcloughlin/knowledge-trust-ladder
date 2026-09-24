---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/linkml
title: LinkML
description: The schema-modelling language LOKF is written in, and the generator suite that turns a schema into JSON Schema, Pydantic models, SHACL shapes, docs, and OWL.
genre: reference
resource: https://linkml.io/linkml/
generated:
  by: process:ktl-librarian
  at: "2026-09-14T10:33:02Z"
status: draft
verified:
- by: process:ktl-librarian
  at: "2026-09-24T00:55:04Z"
---

# Overview

LOKF is defined as a LinkML schema, which is why its JSON Schema, JSON-LD
context, SHACL shapes, and OWL ontology are all generated artifacts rather
than hand-maintained files.

It matters to a bundle owner at exactly one moment: when the fifteen-class
vocabulary stops fitting a deep or safety-critical domain. The answer is a
LinkML domain schema that imports LOKF's and validates with `lokf validate
--schema <file>`; the recipe is the librarian skill's
`references/domain-schema.md`. The same schema also yields Pydantic models,
JSON Schema and rendered documentation, meeting people who think in JSON or
Python on their own ground rather than in RDF.
