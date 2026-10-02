---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/lokf-toolkit
title: "LOKF toolkit (lokf on PyPI)"
description: "The Python package that validates, converts and serves a LOKF bundle. It is the dependency the scaffolded .lokf/pyproject.toml declares."
genre: reference
resource: https://pypi.org/project/lokf/
sources:
- resource: https://pypi.org/project/lokf/
- resource: skills/ktl-sidecar/SKILL.md
- resource: skills/ktl-librarian/SKILL.md
- resource: .lokf/justfile
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
definedBy:
  - https://knowledge-trust-ladder.example/knowledge/references/lokf-specification
---

# Overview

The `lokf` package on PyPI is the toolkit underneath the skills. The README says it supplies the schema and the tooling. The sidecar installs it through `uv`, from the `pyproject.toml` it lays down, and the `justfile` wraps its commands.

# The commands the skills run

From `.lokf/`, as the librarian skill lists them:

- `just lokf-install` runs `uv sync`.
- `just lokf-validate` runs `lokf validate`, the JSON Schema check on every concept's frontmatter and on the assembled bundle.
- `just lokf-check-refs` runs `lokf validate --check-refs`, so that every typed relation target resolves to a concept in the bundle.
- `just lokf-convert` projects the bundle to Turtle.
- `just lokf-serve` starts a SPARQL endpoint with a live graph explorer.

`lokf validate` reads a concept body as an opaque string and never opens `log.md`. The conventions the gate also checks, such as quoted timestamps and one log heading per day, are held by `knowledge-conventions.sh`, which the sidecar lays down beside it.

# Versions

The sidecar's template floors the toolkit at 0.8.0. The librarian's tooling-version step compares the latest PyPI release against that floor in interactive sessions, bumps a minor or patch version itself, and asks a person before a major one.
