---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/lokf-toolkit
title: LOKF toolkit (lokf on PyPI)
description: The lokf Python package, which validates, converts and serves a LOKF bundle and is the dependency the scaffolded .lokf/pyproject.toml declares.
genre: reference
resource: https://pypi.org/project/lokf/
generated:
  by: process:ktl-librarian
  at: "2026-10-06T11:10:52Z"
status: draft
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/lokf-specification
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/references/linkml
verified:
- by: process:ktl-librarian
  at: "2026-10-12T23:54:05Z"
sources:
- resource: https://pypi.org/project/lokf/
- resource: skills/ktl-librarian/SKILL.md
- resource: CHANGELOG.md
---

# Overview

The toolkit is the implementation, not the specification. `lokf validate` checks frontmatter and bundle shape against the generated JSON Schema. With `--schema <file>.yaml` it checks against a domain schema that imports LOKF's instead, and the extension recipe depends on that flag. The generated SHACL shapes catch cardinality, datatype, and range violations on the projected graph. `lokf convert` projects to RDF and `lokf serve` exposes a SPARQL endpoint. `lokf query` runs a SPARQL query against the bundle. The command line also carries `new`, `tables`, `propose`, `vocab`, `skills`, `export`, `mcp` and `registry`, with a `[tables]` extra beside `[build]`.

`lokf validate --check-refs` finds typed-relation targets with no matching concept, and this repository's own `just lokf-check-refs` recipe now calls it. It takes the relation slots from the schema, so a domain schema's own slots are covered without the recipe restating a predicate list.

Scaffolded bundles pin `lokf[build]`, and that `[build]` extra installs the full `linkml` package. So every sidecar already has the LinkML generators for a domain-schema extension, with no extra installation.

Where Python is unavailable, the skills fall back to a structural cross-check against the raw schema, which is not a validation run. They read it from the commit tagged `v0.8.0`, which matches the `lokf` floor: `raw.githubusercontent.com/nicholsn/lokf/66073c3eb8b8ca6ca00fb66ba11beca235eaedc8/lokf.yaml`. Since 2026-10-05 the URL names that commit, never a tag or `main`, because a tag can be moved. The pin moves with the floor, so the fallback cross-checks against the schema the installed toolkit enforces.

## Open questions

- 2026-10-13, human:noelmcloughlin: the SHACL sentence says the shapes catch violations, but `CHANGELOG.md` withdrew that claim ("The toolkit generates the shapes and neither ships nor runs them"). The template sets `lokf[build]>=0.8.0`, a floor, not a pin. The commands beyond `validate`, `convert`, `serve`, `tables` and `new`, and what `[build]` installs, come from sources this concept does not list (`docs/context-layer.md`, `docs/context-layer-technology.md`, `skills/ktl-curator/references/domain-schemas.md`, `skills/ktl-sidecar/templates/pyproject.toml`). Also carry the librarian's version check (raise the floor for a minor or patch, ask a person for a major, never bump `linkml` on its own) and that the no-Python schema is byte-identical to the 0.8.0 wheel's.
