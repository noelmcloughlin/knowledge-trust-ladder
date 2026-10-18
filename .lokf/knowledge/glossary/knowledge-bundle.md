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
  - resource: docs/obsidian.md
  - resource: skills/ktl-librarian/SKILL.md
generated:
  by: human:noelmcloughlin
  at: "2026-10-13T00:16:44Z"
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
    at: "2026-10-18T10:22:18Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T00:16:44Z"
stale_after: 2028-09-24
status: draft
---

# Overview

Strictly, the *bundle* is the `knowledge/` folder - one concept per Markdown
file under an `index.md` that names it - and the *sidecar* is `.lokf/`, the
bundle plus the tooling that validates it, kept out of the host project's
build. In a repository the two travel together, so the terms are used
loosely for each other here. To an Obsidian user a bundle is a folder of
notes opened as a vault of its own - the intended arrangement, through the
host's `knowledge_bundle` link - or, at a cost the plugin READMEs name, a
folder inside a vault, or a whole vault that is a bundle outright. In
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

## Open questions

- 2026-10-13, process:ktl-librarian: Since 2026-10-13 `README.md` keeps the poem, but "Why libraries have catalogues", which says a bundle is the catalogue, is on `docs/architecture.md`. `sources` should list `docs/architecture.md` beside `README.md`.
- 2026-10-15, process:ktl-librarian: Since 2026-10-14 `docs/obsidian.md` sends readers to each plugin's usage page, not its README, and says the plugins' architecture pages name the cost of putting exhibits in a vault's index. This concept says the plugin READMEs name the cost of a folder inside a vault. Which page names that cost now?
