---
type: Reference
id: https://w3id.org/ktl/knowledge/references/lokf-toolkit
title: LOKF toolkit (lokf on PyPI)
description: The lokf Python package, which validates, converts and serves a LOKF bundle and is the dependency the scaffolded .lokf/pyproject.toml declares.
genre: reference
resource: https://pypi.org/project/lokf/
generated:
  by: process:ktl-librarian
  at: "2026-10-26T20:05:58Z"
status: draft
definedBy:
  - https://w3id.org/ktl/knowledge/references/lokf-specification
relatedTo:
  - https://w3id.org/ktl/knowledge/references/linkml
verified:
  - by: process:ktl-librarian
    at: "2026-10-20T23:23:33Z"
sources:
  - resource: https://pypi.org/project/lokf/
  - resource: https://github.com/nicholsn/lokf/blob/66073c3eb8b8ca6ca00fb66ba11beca235eaedc8/src/lokf/cli.py
  - resource: skills/ktl-librarian/SKILL.md
  - resource: CHANGELOG.md
  - resource: docs/context-layer.md
  - resource: docs/federation.md
  - resource: docs/context-layer-technology.md
  - resource: skills/ktl-curator/references/domain-schemas.md
  - resource: skills/ktl-sidecar/templates/pyproject.toml
---

# Overview

The toolkit is the implementation, not the specification. `lokf validate` checks frontmatter and bundle shape against the generated JSON Schema. It takes the schema from `--schema`, else from a `lokf.yaml` in the current folder or an ancestor, else from the copy inside the installed package. With `--schema <file>.yaml` it checks against a domain schema that imports LOKF's instead, and the extension recipe depends on that flag. The toolkit generates SHACL shapes but neither includes them in its package nor runs them, so the checks that run are `lokf validate` (JSON Schema) and `--check-refs`.

`lokf convert` projects to RDF as Turtle, N-Triples, JSON-LD, RDF/XML, N3 or TriG, and `lokf export` writes the four files a bundle publishes, `graph.nt` among them. `lokf serve` exposes a SPARQL endpoint, `lokf query` runs a SPARQL query against the bundle, and `lokf mcp` serves it over the Model Context Protocol (MCP). `lokf tables` writes CSV, Parquet or SQLite: one table per concept type plus a `relations` table. For BigQuery or Athena it writes the Parquet and prints the external-table statements that register it.

`lokf registry init`, `add`, `list` and `resolve` keep a registry of bundles offline. A domain's federation build registers each member release with `lokf registry add` and exports it with `lokf export` (`docs/federation.md`). The command line also carries `new`, `propose`, `vocab` and `skills`, and the package has a `[tables]` extra, which adds pandas and pyarrow, beside `[build]`. PyPI lists 0.8.0 as the latest release.

`lokf validate --check-refs` finds typed-relation targets in the bundle's own namespace with no matching concept, and leaves targets outside its `base_iri` alone. This repository's own `just lokf-check-refs` recipe now calls it. It takes the relation slots from the schema, so a domain schema's own slots are covered without the recipe restating a predicate list.

Scaffolded bundles depend on `lokf[build]>=0.8.0`, a floor and not a pin. Since 0.56.1 they also depend on `rust-just==1.47.0`, so that `uv.lock` checks the recipe runner by hash and `uv run just` runs it. The `[build]` extra installs the full `linkml` package: the whole generator suite, not just the runtime. So a scaffolded sidecar already has the LinkML generators for a domain-schema extension, with no extra installation.

Where Python is unavailable, the skills fall back to a structural cross-check against the raw schema, which is not a validation run. They read it from the commit tagged `v0.8.0`, which matches the `lokf` floor: `raw.githubusercontent.com/nicholsn/lokf/66073c3eb8b8ca6ca00fb66ba11beca235eaedc8/lokf.yaml`. Since 2026-10-05 the URL names that commit, never a tag or `main`, because a tag can be moved. The pin moves with the floor, so the fallback cross-checks against the schema the installed toolkit enforces. That file is byte-identical to the schema inside the `lokf` 0.8.0 wheel, which `uv sync --locked` checks against `.lokf/uv.lock` wherever Python is present.

ktl-librarian checks the toolkit's version in a live session. It compares the latest `lokf` on PyPI with the `>=` floor in `.lokf/pyproject.toml`. For a minor or patch release it raises the floor, runs `uv sync` and validates again. For a major release, or a breaking change in the changelog, it asks the person first. It never bumps `linkml` on its own.

## Open questions

- 2026-10-19, human:noelmcloughlin: refresh against sources.
