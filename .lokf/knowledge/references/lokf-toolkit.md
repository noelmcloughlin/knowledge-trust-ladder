---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/lokf-toolkit
title: LOKF toolkit (lokf on PyPI)
description: The Python package that validates, converts, and serves a LOKF bundle - the dependency the scaffolded .lokf/pyproject.toml declares.
genre: reference
resource: https://pypi.org/project/lokf/
generated:
  by: process:ktl-librarian
  at: "2026-09-17T22:30:00Z"
status: draft
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/lokf-specification
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/references/linkml
verified:
- by: process:ktl-librarian
  at: "2026-09-24T01:25:00Z"
---

# Overview

The implementation, not the specification. `lokf validate` checks frontmatter
and bundle shape against the generated JSON Schema, and `--schema <file>.yaml`
checks against a domain schema that imports LOKF's instead, which is the flag
the extension recipe rests on; the generated SHACL shapes
catch cardinality, datatype, and range violations on the projected graph;
`lokf convert` projects to RDF and `lokf serve` exposes a SPARQL endpoint.
`lokf query` runs a SPARQL query against the bundle. Typed-relation targets
with no matching concept are `lokf validate --check-refs`, which this
repository's own `just lokf-check-refs` recipe now calls: it takes the
relation slots from the schema, so a domain schema's own slots are covered
without the recipe restating a predicate list.

Scaffolded bundles pin `lokf[build]`, and that `[build]` extra pulls in the full
`linkml` package - so every sidecar already has the LinkML generators available
for a domain-schema extension, with no extra installation. Where Python is
unavailable, the skills fall back to the raw schema at the tag matching the
`lokf` floor, `raw.githubusercontent.com/nicholsn/lokf/v0.8.0/lokf.yaml`, for
a structural cross-check only, which is not a validation run. The pin moves
with the floor: upstream `main` has already diverged from 0.8.0, so a check
against it would pass or fail things the installed toolkit does not.
