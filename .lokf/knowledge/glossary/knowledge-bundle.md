---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
title: Knowledge bundle
description: The `.lokf/knowledge` directory - containing one-concept-per-file Markdown, carrying a semantic header, that is simultaneously human-readable documentation and a queryable graph.
definition: The `.lokf/knowledge` directory - containing one-concept-per-file Markdown, carrying a semantic header, that is simultaneously human-readable documentation and a queryable graph. Accessible via a `knowledge_bundle` link at the repository root if that link exists.
genre: reference
resource: skills/ktl-sidecar/templates/README.md
sources:
  - resource: README.md
  - resource: docs/architecture.md
  - resource: docs/obsidian.md
  - resource: skills/ktl-librarian/SKILL.md
generated:
  by: human:noelmcloughlin
  at: "2026-10-18T18:20:55Z"
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
---

# Overview

Strictly, the *bundle* is the `knowledge/` folder - one concept per Markdown
file under an `index.md` that names it - and the *sidecar* is `.lokf/`, the
bundle plus the tooling that validates it, kept out of the host project's
build. In a repository the two travel together, so the terms are used
loosely for each other here. To an Obsidian user the bundle is a folder of
notes that should be opened as a vault of its own, via the host's
`knowledge_bundle` link. It may sit beside the Obsidian vault they already
keep, but not inside. If the bundle is a subfolder of the vault itself, it
puts exhibits in the vault's index, at a cost the plugins' architecture pages
name. In
library terms - the poem the repository's README opens with - the bundle is the
*catalogue* the librarian keeps: the layer that stays put between the stacks
and the next reader. In museum terms it is the *exhibition* - the hall
visitors are shown into, where the docent takes people - and each concept in
it an *exhibit*, the checked, curated part. Both stand against the *workshop*
of raw sources or notes it was distilled from: a repository's code, or an
Obsidian vault, which is never migrated into the bundle. `knowledge/index.md` carries the
semantic header (`base_iri`, `context`, versions, publisher) plus the table
of contents; `knowledge/log.md` records knowledge changes only. The bundle is
the durable layer between scattered sources and the next task - the thing that
stops each session re-finding, re-connecting, and re-judging the same material.
