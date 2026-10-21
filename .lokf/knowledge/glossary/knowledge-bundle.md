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
  at: "2026-10-19T23:21:13Z"
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
    at: "2026-10-20T23:23:33Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T00:16:44Z"
  - by: human:noelmcloughlin
    at: "2026-10-18T18:20:55Z"
stale_after: 2028-09-24
status: draft
---

# Overview

A **knowledge bundle** is the folder `.lokf/knowledge/`: one Markdown file per concept, each with a little YAML frontmatter block. The sidecar's README calls these plain Markdown files that are also a queryable knowledge graph, and says they are just files a person can read on GitHub or in any editor. The path of each file is its concept ID.

`docs/architecture.md` calls the bundle the catalogue: a plain folder of Markdown concept files that keeps the work instead of discarding it. The page says a catalogue is useful only when a reader can tell which entries are sound. The trust ladder, written into each entry, says where the entry came from and how far it has been checked.

A bundle is prose a person reads, structure a schema checks, meaning a graph can query, and context the next task can start from. It is written in LOKF (Linked Open Knowledge Format), a semantic profile of OKF. People, agents and any tool that speaks OKF, JSON Schema, JSON-LD, SHACL or another supported format can read it. One bundle is one repository's context layer, and the architecture page points to `docs/context-layer.md` for how several bundles become one catalogue.

## The bundle and the sidecar

The **sidecar** is `.lokf/`, a dot-folder beside the code like `.git/`, kept out of the project's build. It holds the bundle beside its tooling: `pyproject.toml`, which declares the `lokf` toolkit, a `justfile` of shortcut commands, and `scripts/`. Some files appear only when they are needed:

- `feedback.md`, once a reader's agent records a gap. The README calls it input for the librarian, not knowledge.
- `questions.md`, once the librarian handles a reader's entry.
- `curators/`, once a curator's public key is on file.
- `ingest.yaml` and `mirror/`, on a host that mirrors sources outside the repository.

## Reserved files

Two files in the bundle are reserved. The root `index.md` carries the bundle's metadata and its table of contents. Its semantic header holds `lokf_version`, `okf_version`, `base_iri`, `context`, `title`, `description`, `license` and `publisher`, and a concept's IRI is `base_iri` plus its path. `log.md` is the change history, and it records knowledge changes only. The librarian treats `diataxis.md` the same way: KTL Registrar may write that map at the bundle root, and it is never a concept.

## The doorway

ktl-sidecar puts a `knowledge_bundle` link at the host's root. It is the same `knowledge/` folder under a visible name, for folder pickers and file managers that hide dot-folders, and for Obsidian's "Open folder as vault". Git carries the link, but a sync service does not, so `just lokf-link` recreates it on a machine where it is missing. A Windows checkout without `core.symlinks` shows it as a small text file. Where the link is missing, a person opens `.lokf/knowledge` by typing the path. Every command works without it.

## In Obsidian

`docs/obsidian.md` calls the vault a person already has the **workshop**, and nothing in it is moved or migrated. The bundle is the **exhibition**: the checked part of what the workshop knows, and the part that teammates, CI and agents read. It opens as a small vault of its own through the `knowledge_bundle` link, never through the repository root, which cannot see a dot-folder or a link that resolves inside it. The two vaults never index the same file.

The plugins installed in that vault need no configuration, because the root `index.md` carries the bundle's header, so the whole vault is the bundle. Obsidian writes that vault's workspace state to `.lokf/knowledge/.obsidian/`, which the sidecar's `.gitignore` excludes. A person who links each repository's `.lokf/knowledge` into a folder of their own vault makes the one arrangement that puts exhibits in that vault's index, at the cost the plugins' architecture pages name.

## Open questions

- 2026-10-19, human:noelmcloughlin: the knowledge-bundle glossary concept is stale, refresh against sources.
