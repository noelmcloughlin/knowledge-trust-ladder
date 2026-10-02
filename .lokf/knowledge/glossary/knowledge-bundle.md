---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
title: "Knowledge bundle"
description: "The `.lokf/knowledge` folder: one Markdown file per concept, with a semantic header on the root index.md, which people read as documentation and tools query as a graph."
definition: "A folder of Markdown concept files, one concept per file, whose root index.md carries the header that lifts the whole folder into a queryable LOKF graph."
genre: reference
resource: README.md
sources:
- resource: README.md
- resource: skills/ktl-sidecar/SKILL.md
- resource: skills/ktl-sidecar/templates/README.md
- resource: docs/obsidian.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/lokf
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/explanation/hosts-and-doorways
  - https://knowledge-trust-ladder.example/knowledge/playbooks/open-bundle-in-obsidian
---

# Overview

A knowledge bundle is the catalogue the README describes: a plain folder of Markdown concept files that keeps the work of finding, connecting and judging a repository's knowledge, instead of discarding it with each task. Every concept says where it came from and how far it has been checked, in plain words.

In this family the bundle is always `.lokf/knowledge/`, one real folder on every host. The `.lokf/` folder beside it holds the tooling: a `pyproject.toml` that declares the `lokf` toolkit, a `justfile`, the scripts the gate runs, and the Copilot builder. A `knowledge_bundle` link at the repository root points at the real folder, so that folder pickers, which hide dot-folders, have an ordinary name to open.

# What is in it

- `index.md` at the root carries the semantic header: `lokf_version`, `okf_version`, `base_iri`, `context`, `title`, `description`, `license` and `publisher`. `base_iri` plus a concept's path mints that concept's IRI. Without the header the bundle is plain OKF.
- `log.md` records knowledge changes, newest day first, under one bare `## YYYY-MM-DD` heading per day.
- Every other Markdown file is one concept. Its frontmatter names its `type`, its `id`, where it came from (`resource`, `sources`), who produced it (`generated`), who checked it (`verified`) and its lifecycle (`status`, `stale_after`). Its body is prose a person reads.
- Each domain folder (`playbooks/`, `policies/`, `glossary/`, `references/`, `explanation/`) carries an `index.md` of its own, a table of contents.

# The exhibition, not the workshop

`docs/obsidian.md` names the split. The vault or repository a person already keeps is the workshop, and nothing in it is moved or migrated. The bundle is the exhibition: the checked part of what the workshop knows, and the front door that teammates, continuous integration and agents come through. In Obsidian it opens as a small vault of its own, through the `knowledge_bundle` link, and the two never index the same file.
