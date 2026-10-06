---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/open-bundle-in-obsidian
title: Open the knowledge bundle in Obsidian
description: "How a knowledge bundle meets an Obsidian vault: two vaults, the workshop someone keeps and the bundle opened as its own through the `knowledge_bundle` doorway, what Obsidian does with the link on each host, and why the bundle is never a real folder inside a vault."
genre: how-to
resource: skills/ktl-sidecar/SKILL.md
sources:
- resource: skills/ktl-sidecar/SKILL.md
- resource: docs/obsidian.md
- resource: skills/ktl-docent/references/obsidian.md
- resource: skills/ktl-sidecar/references/portability.md
- resource: https://obsidian.md/help/settings
- resource: CHANGELOG.md
generated:
  by: process:ktl-librarian
  at: "2026-10-05T12:41:36Z"
status: draft
isPartOf:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/explanation/hosts-and-doorways
verified:
- by: process:ktl-librarian
  at: "2026-10-06T11:10:52Z"
---

# Overview

`ktl-sidecar` Step 2 creates a `knowledge_bundle` symlink at the host root, pointing at `.lokf/knowledge`. It exists because `.lokf/` is a dot-directory, and Finder, most folder pickers (Obsidian's **File → Open folder as vault** included) and a repository listing hide those or make them hard to find. So `.lokf/knowledge` is easy to open by typing the path but awkward to browse to. The link is the **doorway**: the one name a person needs to know, whatever they open the bundle with. For an Obsidian user it is also the boundary between two vaults.

# Two vaults

The vault someone already keeps is the **workshop**: notes change freely there, and nothing about it is migrated or reorganised. The bundle is the **exhibition**, and it is opened as a vault of its own:

1. Choose **File → Open folder as vault** → `knowledge_bundle`. The bundle becomes a small vault: every note a concept, the root `index.md` carrying the bundle's header. Obsidian writes its workspace state through the link into the real `.lokf/knowledge/.obsidian/`. That folder is harmless to `lokf validate` (it reads only `*.md`) and excluded from git by `.lokf/.gitignore`.
2. Install KTL Registrar and KTL Curator *in that vault*, since Obsidian installs plugins per vault. There is nothing to configure: the root `index.md` carries the bundle's header, so the whole vault is the bundle.

The doorway is invisible to any vault it sits inside (the reconciler below), so the workshop vault and the exhibition vault never index the same file. Open the link itself: a vault opened at the host root never lists the bundle.

Per host:

- **Windows.** A junction does the same job with no administrator rights or Developer Mode: `mklink /J knowledge_bundle .lokf\knowledge`. Obsidian follows junctions as it follows symlinks.
- **No link at all.** A filesystem may have no links, or a sync service may carry folders but not links: OneDrive syncs neither symbolic links nor junctions. Then open `.lokf/knowledge` directly by typing the path into the picker, or recreate the link on each machine (`just lokf-link` from `.lokf/`). Everything else is identical.
- **Git.** Git carries the symlink as a symlink. On a Windows checkout without `core.symlinks`, the symlink becomes a small text file, which is the cue to make the junction.

# What Obsidian does with the link on each host

Obsidian 1.13.7's file reconciler (`reconcileSymbolicLinkCreation`) resolves a link's real path and **skips the link when that path equals, contains, or lies inside a folder it is already watching**. The vault root is always one of those folders. Its help page says the same in words: it ignores "a symlink to a parent folder of the vault, or from one folder in the vault to another folder in the same vault", as a safeguard against a note being indexed twice. Dot-directories are never indexed at all. Two consequences follow:

- **From a vault opened at the host's root** (a code repository, or a notes vault kept in git that the sidecar was installed into), neither `.lokf/` nor `knowledge_bundle` appears. The sidecar is invisible to that vault by the same rule that hides `.obsidian/` and `.git/`. So point people at the doorway, not the root.

  For a notes vault this is the feature that makes the sidecar safe to keep *inside* the vault folder: the workshop and the exhibition never index the same file, which is the one hazard Obsidian's caution about nested vaults names. On a code-repository host the cost runs the other way. Concepts cite sources such as `src/…` and `docs/…` that sit above the small vault, so no plugin can open them from there, and KTL Curator shows such a source as a path with a copy button.
- **A link whose target lies outside the vault is followed.** An Obsidian user with one vault and many repositories can link each repository's `.lokf/knowledge` into a folder of that vault (`projects/acme-knowledge -> ~/git/acme/.lokf/knowledge`), and list those folders under the plugins' *Bundle root folders* setting. The sources are then inside the vault for the review card to open. This is the one arrangement that does put exhibits in the workshop's index, so it costs what a real folder costs (below). Obsidian Sync does not carry such links either, so keep them out of a synced vault.

# Why the bundle is never a real folder inside a vault

Obsidian indexes a real folder inside a vault like any other, so the exhibition's concepts appear in the workshop's link suggestions, quick switcher, graph and search. *Settings → Files and links → Excluded files* hides an excluded folder from search, graph view and unlinked mentions. But it only makes it "less noticeable" in the quick switcher and link suggestions, in the words of [Obsidian's settings help](https://obsidian.md/help/settings). `ktl-sidecar` installed the bundle that way for a vault host for one day (2026-09-12) and retired it the next. The two-vault workflow above is the one the skills and the plugins assume. A shared folder that is *not* a vault may still be rearranged that way by hand, for a synced visible name: the sidecar's `references/portability.md` says how and what it costs. [Hosts and doorways](../explanation/hosts-and-doorways.md) gives the attempt, its cost and what the reversal kept.
