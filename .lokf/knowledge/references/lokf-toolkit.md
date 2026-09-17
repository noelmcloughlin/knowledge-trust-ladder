---
type: Reference
id: https://lokf-agent-skills.example/knowledge/references/lokf-toolkit
title: LOKF toolkit (lokf on PyPI)
description: The Python package that validates, converts, and serves a LOKF bundle - the dependency the scaffolded .lokf/pyproject.toml declares.
genre: reference
resource: https://pypi.org/project/lokf/
generated:
  by: process:lokf-librarian
  at: "2026-09-14T12:00:00Z"
status: draft
definedBy:
- https://lokf-agent-skills.example/knowledge/references/lokf-specification
relatedTo:
- https://lokf-agent-skills.example/knowledge/references/linkml
verified:
- by: process:lokf-librarian
  at: "2026-09-17T14:02:11Z"
---

# Overview

The implementation, not the specification. `lokf validate` checks frontmatter
and bundle shape against the generated JSON Schema, and `--schema <file>.yaml`
checks against a domain schema that imports LOKF's instead, which is the flag
the extension recipe rests on; the generated SHACL shapes
catch cardinality, datatype, and range violations on the projected graph;
`lokf convert` projects to RDF and `lokf serve` exposes a SPARQL endpoint.
`lokf query` runs a SPARQL query against the bundle and is what this
repository's own `just lokf-check-refs` recipe uses to find typed-relation
targets with no matching concept - a gap `lokf validate` doesn't cover.

Scaffolded bundles pin `lokf[build]`, and that `[build]` extra pulls in the full
`linkml` package - so every sidecar already has the LinkML generators available
for a domain-schema extension, with no extra installation. Where Python is
unavailable, the skills fall back to the raw schema at
`raw.githubusercontent.com/nicholsn/lokf/main/lokf.yaml` for a structural
cross-check only, which is not a validation run.
