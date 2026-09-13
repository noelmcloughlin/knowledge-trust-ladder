---
type: Playbook
id: https://lokf-agent-skills.example/knowledge/playbooks/open-bundle-in-obsidian
title: Open the knowledge bundle in Obsidian
description: How a knowledge bundle meets an Obsidian vault - two vaults, the workshop someone already keeps and the bundle opened as its own vault through the root-level knowledge_bundle doorway - with what Obsidian does with a link on each host, verified against Obsidian 1.13.7's file reconciler, and why the bundle is never laid down as a real folder inside a vault.
genre: how-to
resource: skills/lokf-sidecar/SKILL.md
generated:
  by: process:lokf-librarian
  at: "2026-09-13T12:00:00Z"
status: draft
isPartOf:
  - https://lokf-agent-skills.example/knowledge/playbooks/lokf-sidecar-skill
about:
  - https://lokf-agent-skills.example/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://lokf-agent-skills.example/knowledge/explanation/hosts-and-doorways
verified:
  - by: process:lokf-librarian
    at: "2026-09-13T15:00:00Z"
---

# Overview

`lokf-sidecar` Step 2 creates a `knowledge_bundle` symlink at the host root, pointing at
`.lokf/knowledge`. It exists because `.lokf/` is a dot-directory and Finder, most folder pickers -
Obsidian's **File → Open folder as vault** included - and a repository listing hide or bury those, so
`.lokf/knowledge` is easy to open by typing the path but awkward to browse to. The link is the
**doorway**: the one name a person needs to know, whatever they open the bundle with. For an Obsidian
user it is also the boundary between two vaults.

# Two vaults

The vault someone already keeps is the **workshop**: notes change freely there, and nothing about it
is migrated or reorganised. The bundle is the **exhibition**, and it is opened as a vault of its own:

1. **File → Open folder as vault** → `knowledge_bundle`. The bundle becomes a small vault - every note
   a concept, the root `index.md` carrying the bundle's header - and Obsidian writes its workspace
   state through the link into the real `.lokf/knowledge/.obsidian/`, harmless to `lokf validate` (it
   reads only `*.md`) and excluded from git by `.lokf/.gitignore`.
2. Install LOKF Registrar and LOKF Curator *in that vault* - Obsidian installs plugins per vault.
   Nothing to configure: both default to "the vault root is the bundle root" when the root `index.md`
   carries a header.

The doorway is invisible to any vault it sits inside (the reconciler below), so the workshop vault and
the exhibition vault never index the same file. Open the link itself; a vault opened at the host root
never lists the bundle.

Per host:

- **Windows** - a junction does the same job with no administrator rights or Developer Mode:
  `mklink /J knowledge_bundle .lokf\knowledge`. Obsidian follows junctions as it follows symlinks.
- **No link at all** (a filesystem without them, or a sync service that carries folders but not
  links - OneDrive syncs neither symbolic links nor junctions) - open `.lokf/knowledge` directly by
  typing the path into the picker, or recreate the link on each machine (`just lokf-link` from
  `.lokf/`). Everything else is identical.
- **Git** carries the symlink as a symlink; a Windows checkout without `core.symlinks` materialises it
  as a small text file, which is the cue to make the junction.

# What Obsidian does with the link on each host

Obsidian 1.13.7's file reconciler (`reconcileSymbolicLinkCreation`, read from the installed
application bundle on 2026-09-12) resolves a link's real path and **skips the link when that path
equals, contains, or lies inside a folder it is already watching** - the vault root always being one.
Its help page says the same in words: it ignores "a symlink to a parent folder of the vault, or from
one folder in the vault to another folder in the same vault", as a safeguard against a note being
indexed twice. Dot-directories are never indexed at all. Two consequences:

- **From a vault opened at the host's root** (a code repository, or a notes vault kept in git that
  the sidecar was laid into), neither `.lokf/` nor `knowledge_bundle` appears - the sidecar is
  invisible to that vault by the same rule that hides `.obsidian/` and `.git/`. So point people at the
  doorway, not the root. For a notes vault this is the feature that makes the sidecar safe to keep
  *inside* the vault folder: the workshop and the exhibition never index the same file, which is the
  one hazard Obsidian's caution about nested vaults names.
- **A link whose target lies outside the vault is followed.** An Obsidian user with one vault and many
  repositories can link each repository's `.lokf/knowledge` into a folder of that vault
  (`projects/acme-knowledge -> ~/git/acme/.lokf/knowledge`) and list those folders under the plugins'
  *Bundle root folders* setting - with the sources now inside the vault for the review card to open.
  This is the one arrangement that does put exhibits in the workshop's index, so it costs what a real
  folder costs (below); Obsidian Sync does not carry such links either, so keep them out of a synced
  vault.

# Why the bundle is never a real folder inside a vault

Obsidian indexes a real folder inside a vault like any other, so the exhibition leaks into the
workshop's link suggestions, quick switcher, graph and search, and *Settings → Files and links →
Excluded files* only makes an excluded folder "less noticeable" in the quick switcher and link
suggestions (hidden in search, graph view and unlinked mentions). `lokf-sidecar` laid the bundle down
that way for a vault host for one day (2026-09-12) and retired it the next; the two-vault workflow
above is the one the skills and the plugins assume. A shared folder that is *not* a vault may still be
rearranged that way by hand, for a synced visible name - the sidecar's `references/portability.md`
says how and what it costs. The attempt, its cost and what the reversal kept:
[Hosts and doorways](../explanation/hosts-and-doorways.md).
