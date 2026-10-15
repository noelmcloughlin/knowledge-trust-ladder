---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/exhibition
title: Exhibition
description: "In the two-vault arrangement for Obsidian, the bundle opened as a small vault of its own: the checked part of what the workshop knows, which teammates, CI and agents read. The README's Exhibitions are the sites that show a repository's collection."
definition: "The bundle as a vault of its own: the checked part of what the workshop knows, and the part that teammates, CI and agents read."
genre: reference
resource: docs/obsidian.md
sources:
- resource: docs/obsidian.md
- resource: README.md
relatedTo:
- https://w3id.org/ktl/knowledge/glossary/workshop
- https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
generated:
  by: process:ktl-librarian
  at: "2026-10-15T01:30:10Z"
status: draft
---

# Overview

`docs/obsidian.md` names two vaults. The bundle is the **exhibition**: the checked part of what the [workshop](workshop.md) knows, and the part that teammates, CI and agents read. It opens as a small vault of its own, and the two never index the same file. The vault a person already has is the workshop, and nothing in it is moved or migrated.

Since 0.42.0 the README uses the word for the sites too. Its Exhibitions section lists each site that `ktl-website` builds to show a repository's collection: this repository's own bundle at `https://w3id.org/ktl/knowledge/`, and AI-LinkMO's.
