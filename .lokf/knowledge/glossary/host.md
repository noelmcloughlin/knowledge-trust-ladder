---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/host
title: Host
description: "The repository or folder a knowledge bundle sits in, in its `.lokf/` sidecar: most often a code repository, sometimes an Obsidian vault or a shared folder. The skills' pages also use the word for the setting the skills run in there: the machine, the shell and the forge."
definition: The repository or folder that holds a knowledge bundle in its `.lokf/` sidecar, such as a code repository, an Obsidian vault or a shared folder.
genre: reference
resource: docs/obsidian.md
sources:
  - resource: docs/obsidian.md
    id: obsidian.md
    excerpt: the repository or vault the bundle sits in
  - resource: skills/ktl-sidecar/SKILL.md
  - resource: skills/ktl-sidecar/references/portability.md
relatedTo:
  - https://w3id.org/ktl/knowledge/glossary/sidecar
  - https://w3id.org/ktl/knowledge/glossary/doorway
  - https://w3id.org/ktl/knowledge/explanation/hosts-and-doorways
generated:
  by: process:ktl-librarian
  at: "2026-11-15T20:43:54Z"
status: draft
---

# Overview

A **host** is the repository or folder a knowledge bundle sits in: in the words of `docs/obsidian.md`, "the repository or vault the bundle sits in".[^obsidian.md] The [sidecar](sidecar.md) keeps the bundle in the host's `.lokf/` folder, and the [doorway](doorway.md) gives it a name at the host's root that a folder picker can see. Here the word means the place the bundle lives, not a server, and not a hosting service such as GitHub.

A host is most often a code repository. It can also be an Obsidian vault, a shared drive or SharePoint library, or several repositories linked into one Obsidian vault. [Why the bundle is in a hidden folder](../explanation/hosts-and-doorways.md) describes each of the four.

The skills' own pages also say *host* for the setting the skills run in there: the operating system and its shell, the forge, a synced folder, or Microsoft 365 Copilot. [Portability](../explanation/portability.md) lists what works in each.

[^obsidian.md]: docs/obsidian.md, the step that opens `knowledge_bundle` as a vault
