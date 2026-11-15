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
    id: readme.md
    excerpt: "Knowledge bundles exist anywhere skills run:"
relatedTo:
  - https://w3id.org/ktl/knowledge/glossary/workshop
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
generated:
  by: process:ktl-librarian
  at: "2026-11-15T19:13:22Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-11-14T22:54:18Z"
---

# Overview

`docs/obsidian.md` names two vaults. The bundle is the **exhibition**: the checked part of what the [workshop](workshop.md) knows, and the part that teammates, CI and agents read. It opens as a small vault of its own, and the two never index the same file. The vault a person already has is the workshop, and nothing in it is moved or migrated.

The README uses the word for the sites too. Its Exhibitions section says knowledge bundles exist anywhere skills run, and lists:[^readme.md]

- this repository's own bundle, at `https://w3id.org/ktl/knowledge/`, the knowledge behind the skills;
- the KTL Curator Obsidian plugin's, at `https://w3id.org/ktl/curator/knowledge/`, which helps a person judge what a bundle claims;
- the KTL Registrar Obsidian plugin's, at `https://w3id.org/ktl/registrar/knowledge/`, which keeps a bundle well-formed as a person edits it;
- the lmodel catalog, at `https://github.com/lmodel`, which has dozens of knowledge bundles.

Under its own heading, *Federation of Bundles (Context Layer)*, the section lists KTL Federation, the domain that federates member bundles into one workspace, as a context layer, at `https://w3id.org/ktl/federation/knowledge/`.

[^readme.md]: README.md, the *Exhibitions* section
