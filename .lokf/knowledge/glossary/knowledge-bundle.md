---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
title: Knowledge bundle
description: "The knowledge bundle, `.lokf/knowledge`: one Markdown file per concept, readable as documentation and queryable as a graph; how it differs from the `.lokf/` sidecar, what its reserved `index.md` and `log.md` hold, and the `knowledge_bundle` doorway that Obsidian opens as a vault of its own."
definition: "The `.lokf/knowledge` folder: one Markdown file per concept, each with YAML frontmatter, which a person reads as documentation and a tool queries as a knowledge graph. A `knowledge_bundle` link beside `.lokf/` shows the same folder under a visible name."
genre: reference
resource: skills/ktl-sidecar/templates/README.md
sources:
  - resource: skills/ktl-sidecar/templates/README.md
  - resource: README.md
  - resource: docs/architecture.md
  - resource: docs/obsidian.md
  - resource: skills/ktl-librarian/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-19T21:26:04Z"
about:
  - https://w3id.org/ktl/knowledge/glossary/lokf
verified:
  - by: human:noelmcloughlin
    at: "2026-09-09T16:35:55Z"
  - by: human:noelmcloughlin
    at: "2026-09-24T01:09:00Z"
  - by: human:noelmcloughlin
    at: "2026-09-26T20:36:11Z"
  - by: process:ktl-librarian
    at: "2026-10-19T20:01:11Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T00:16:44Z"
  - by: human:noelmcloughlin
    at: "2026-10-18T18:20:55Z"
stale_after: 2028-09-24
status: draft
---

# Overview

A **knowledge bundle** is the folder `.lokf/knowledge/`: one Markdown file per concept, each with a YAML frontmatter block. The sidecar's README calls these plain Markdown files that are also a queryable knowledge graph. `docs/architecture.md` calls the bundle the catalogue: a plain folder of Markdown concept files that keeps the work instead of discarding it. A bundle is prose a person reads, structure a schema checks, meaning a graph can query, and context the next task can start from. It is written in LOKF (Linked Open Knowledge Format), and one bundle is one repository's context layer.

The **sidecar** is `.lokf/`, a dot-folder beside the code like `.git/`, kept out of the project's build. It holds the bundle with its tooling and docs. ktl-sidecar also puts a `knowledge_bundle` link at the host's root: the same folder under a visible name, for folder pickers and file managers that hide dot-folders, and for Obsidian's "Open folder as vault".

Two files in the bundle are reserved. The root `index.md` carries the semantic header (`lokf_version`, `okf_version`, `base_iri`, `context`, `title`, `description`, `license` and `publisher`) and the table of contents. A concept's IRI is `base_iri` plus its path. `log.md` records knowledge changes only.

In Obsidian the bundle is the **exhibition**: the checked part of what the workshop knows, and the part that teammates, CI and agents read. The **workshop** is the vault a person already has, and nothing in it is moved or migrated. The bundle opens as a small vault of its own through the `knowledge_bundle` link, never through the repository root, and the two vaults never index the same file. A person who links each repository's `.lokf/knowledge` into a folder of their own vault makes the one arrangement that puts exhibits in that vault's index, at the cost the plugins' architecture pages name.

## Open questions

- 2026-10-19, human:noelmcloughlin: the knowledge-bundle glossary concept is stale, refresh against sources.
