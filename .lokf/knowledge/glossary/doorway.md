---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/doorway
title: Doorway
description: "`knowledge_bundle`, the link at a host's root that ktl-sidecar creates onto the bundle, so the hidden `.lokf/knowledge` folder has a name a folder picker can see. Obsidian opens the bundle as a vault of its own through it."
definition: The `knowledge_bundle` link at a host's root onto the bundle, which ktl-sidecar creates so the bundle has a name a folder picker can see.
genre: reference
resource: docs/obsidian.md
sources:
- resource: docs/obsidian.md
- resource: skills/ktl-sidecar/SKILL.md
- resource: skills/ktl-docent/references/obsidian.md
relatedTo:
- https://w3id.org/ktl/knowledge/explanation/hosts-and-doorways
- https://w3id.org/ktl/knowledge/glossary/sidecar
- https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
- https://w3id.org/ktl/knowledge/playbooks/open-bundle-in-obsidian
generated:
  by: process:ktl-librarian
  at: "2026-10-15T01:30:10Z"
status: draft
verified:
- by: process:ktl-librarian
  at: "2026-10-14T00:35:00Z"
---

# Overview

`docs/obsidian.md` calls `knowledge_bundle` the **doorway**. It is the link that `ktl-sidecar` creates at the root of the host (the repository or vault the bundle sits in), beside the sidecar's `.lokf/` folder. The link gives the bundle a name a folder picker can see. ktl-docent's `references/obsidian.md` gives the rule for opening it in Obsidian: open the link itself, never the host root. A vault opened at the root lists neither the dot-folder nor the link, which keeps the [workshop](workshop.md) clean.

A host that commits `.lokf/` commits the link too. A host that gitignores `.lokf/` adds the link to the root `.gitignore` instead ([hosts and doorways](../explanation/hosts-and-doorways.md)).
