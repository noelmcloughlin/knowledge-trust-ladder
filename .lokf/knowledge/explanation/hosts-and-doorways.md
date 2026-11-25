---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/hosts-and-doorways
title: Why the bundle is in a hidden folder
description: Why the bundle lives in the hidden folder `.lokf/knowledge`, the same on every host, and how `knowledge_bundle` beside it, the doorway, lets people, folder pickers and Obsidian find it; the four common arrangements, from a code repository to several repositories in one Obsidian vault; and why the bundle is never a visible folder inside a vault.
genre: explanation
resource: skills/ktl-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-11-15T20:43:54Z"
about:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-sidecar-skill
  - https://w3id.org/ktl/knowledge/playbooks/open-bundle-in-obsidian
relatedTo:
  - https://w3id.org/ktl/knowledge/glossary/host
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
  - https://w3id.org/ktl/knowledge/explanation/portability
  - https://w3id.org/ktl/knowledge/explanation/why-a-registrar-role
sources:
  - resource: skills/ktl-sidecar/SKILL.md
  - resource: docs/obsidian.md
  - resource: skills/ktl-sidecar/references/portability.md
verified:
  - by: process:ktl-librarian
    at: "2026-11-23T16:04:59Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T01:20:21Z"
status: draft
---

# A hidden folder beside the content

A LOKF bundle is a **sidecar**: it sits beside the raw sources it distils, in the same folder tree and normally the same git repository. The repository or folder that holds it is the [host](../glossary/host.md). The sidecar is `.lokf/`, and the bundle is `.lokf/knowledge/`. The tooling (`pyproject.toml`, `justfile`, `scripts/`, `feedback.md`) sits next to the bundle. This is the same shape as `.git/`, `.github/`, `.devcontainer/` and, for an Obsidian user, `.obsidian/`: a dot-folder the tools own, kept beside the content people own.

# The doorway

A dot-folder is hidden from Finder, from most folder pickers and, in effect, from a repository listing. So `ktl-sidecar` Step 2 adds a **doorway**: `knowledge_bundle`, a link at the host's root onto the bundle. The bundle therefore has **two names**:

| Name | Who uses it | What it is |
| --- | --- | --- |
| `.lokf/knowledge` | every skill, the `lokf` toolkit, CI's `knowledge-registrar.yaml`, `llms.txt` | the real folder, on every host |
| `knowledge_bundle` | people, folder pickers, file managers, Obsidian's *Open folder as vault* | a symlink (a junction on Windows), added by the sidecar's optional Step 2 |

The real folder is always the hidden one. The doorway is committed alongside a tracked `.lokf/`, or added to the root `.gitignore` alongside a gitignored one. A host that lints, spell-checks or link-checks `**/*.md` across the repository excludes `knowledge_bundle/` from that check, or the same files are processed twice, once at each path. Obsidian writes the bundle vault's workspace state through the link into `.lokf/knowledge/.obsidian/`, which the sidecar's gitignore excludes and `lokf validate` ignores. The release workflow resolves `.lokf/knowledge` to the real folder before packing it.

# Four arrangements

- **A code repository.** Readers are developers, agents and CI. The hidden folder keeps the bundle out of their way. The doorway is how a person browses to it, and how Obsidian opens it as a vault of its own.
- **An Obsidian vault.** The sidecar is installed beside the notes. The vault never indexes `.lokf/`, and it skips the doorway too, because the link resolves inside the vault being indexed (see [Open the knowledge bundle in Obsidian](../playbooks/open-bundle-in-obsidian.md)). The notes vault is the [workshop](../glossary/workshop.md). The person curates the bundle in a second vault opened through the doorway, the [exhibition](../glossary/exhibition.md), so the two never index the same file, and the bundle stays out of the notes vault's graph, search and Sync.
- **A shared drive or SharePoint library.** Readers are whoever the service shows the folder to. `.lokf/` syncs, since Microsoft's restricted-name list has nothing against a leading dot, so the real folder is the same on every machine. OneDrive syncs neither symbolic links nor junctions, so the doorway is made on each machine (`just lokf-link`), or the bundle is opened by its path. A library nobody reaches through git may be rearranged by hand for a synced visible name, as the sidecar's `references/portability.md` says. A shared folder that is also an Obsidian vault must not be.
- **Several repositories, one Obsidian vault.** A person links each repository's `.lokf/knowledge` into a folder of their own Obsidian vault, and lists those folders under the KTL plugins' *Bundle root folders* setting. Every bundle they curate is then in one vault, beside the notes they keep about them. This is the one arrangement that puts the bundles in the vault's own index, and Obsidian Sync does not carry such links.

# Why the bundle is never a visible folder inside a vault

Obsidian indexes a real folder inside a vault like any other, so a bundle there would put its concepts into the notes vault's link suggestions, quick switcher, graph and search. *Settings → Files and links → Excluded files* hides an excluded folder from search, graph view and unlinked mentions, but only makes it less noticeable in the quick switcher and link suggestions. Two vaults avoid that: the one a person already keeps, and the bundle opened as a vault of its own through the doorway, where the plugins do their work. So the sidecar has one layout on every host, the hidden folder with the doorway, and its `lokf-link` recipe creates or recreates the doorway.

A shared folder rearranged by hand, with a real `knowledge_bundle/` and `.lokf/knowledge` as the link onto it, still works. The Step 5 templates name the bundle by both paths, the plugins detect a top-level `knowledge_bundle/` and read their *Bundle root folders* setting, and the junction guidance for Windows applies.

[Portability](portability.md) says what works on each machine, shell and forge.
