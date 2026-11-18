---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/obsidian
title: Obsidian
description: "Obsidian, a desktop and mobile app for writing and linking Markdown notes and the editor the docs name for reading and editing the bundle: it opens a folder as a vault, installs plugins per vault, and has no CI, so two optional KTL plugins work inside it."
definition: A desktop and mobile app for writing and linking Markdown notes, which opens a folder as a vault and installs plugins per vault; the editor the docs name for reading and editing the bundle.
genre: reference
resource: docs/obsidian.md
sources:
  - resource: docs/obsidian.md
    id: obsidian
    excerpt: Obsidian installs plugins per vault.
  - resource: docs/architecture.md
    id: architecture
    excerpt: there is no CI, so two optional plugins work inside the editor.
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://w3id.org/ktl/knowledge/glossary/workshop
  - https://w3id.org/ktl/knowledge/glossary/exhibition
  - https://w3id.org/ktl/knowledge/playbooks/open-bundle-in-obsidian
generated:
  by: process:ktl-librarian
  at: "2026-11-14T22:54:18Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-11-18T00:02:42Z"
---

# Overview

**Obsidian** is a desktop and mobile app for writing and linking Markdown notes, at <https://obsidian.md/>, and the editor the docs name for reading and editing the bundle. It opens a folder as a *vault*, with **File → Open folder as vault**, and it installs plugins per vault.[^obsidian] For the bundle, it writes that vault's workspace state to `.lokf/knowledge/.obsidian/`, which the sidecar's `.gitignore` excludes.

The bundle opens as a vault of its own, through the `knowledge_bundle` doorway. That vault is the [[exhibition]], and the vault a person already has is the [[workshop]]. The two never index the same file.

In Obsidian there is no CI, so two optional plugins work inside the editor.[^architecture] KTL Registrar checks each record as it is typed, and KTL Curator runs the curator's review session without an agent. Obsidian is optional in both directions: the skills rely on `lokf validate`, not on a plugin, and the plugins work on any LOKF bundle however it was made.

[^obsidian]: docs/obsidian.md, the step that installs the plugins
[^architecture]: docs/architecture.md, the paragraph on Obsidian
