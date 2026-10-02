---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/linkml
title: "LinkML"
description: "The schema-modelling language LOKF is written in, and the generator suite that turns a schema into JSON Schema, Pydantic models, SHACL shapes, documentation and OWL."
genre: reference
resource: https://linkml.io/linkml/
sources:
- resource: https://linkml.io/linkml/
- resource: README.md
- resource: skills/ktl-curator/references/domain-schemas.md
- resource: skills/ktl-librarian/references/domain-schema.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/references/lokf-specification
  - https://knowledge-trust-ladder.example/knowledge/explanation/domain-schemas
---

# Overview

LinkML is the schema language the LOKF specification is written in. The README credits the LinkML Community for it. One LinkML schema, `lokf.yaml`, defines the whole format, and the JSON Schema, JSON-LD context, SHACL shapes and OWL ontology are generated from it rather than hand-edited.

# How this repository uses it

The sidecar's `pyproject.toml` depends on `lokf[build]`, and that `[build]` extra pulls in the `linkml` package with its full generator suite. So a host that needs a domain schema already has the tooling: from `.lokf/`, `uv run gen-json-schema`, `gen-pydantic`, `gen-doc` and `gen-shacl` each take the schema and produce one projection of it.

A domain schema imports LOKF's schema and adds classes and slots. `lokf validate --schema <file>` then checks a bundle against both. The curator's `references/domain-schemas.md` says when that is worth doing, and the librarian's `references/domain-schema.md` is the recipe.
