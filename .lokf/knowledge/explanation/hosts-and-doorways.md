---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/hosts-and-doorways
title: "Hosts and doorways: where the bundle's real folder lives"
description: "The bundle is `.lokf/knowledge`, one real folder on every host, and `knowledge_bundle` beside it is a link, the doorway for people and folder pickers. Why there is one layout, and what each kind of host does with the link."
genre: explanation
resource: skills/ktl-sidecar/SKILL.md
sources:
- resource: skills/ktl-sidecar/SKILL.md
- resource: skills/ktl-sidecar/references/portability.md
- resource: docs/obsidian.md
- resource: README.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
about:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/open-bundle-in-obsidian
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/docent-in-m365-copilot
  - https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
  - https://knowledge-trust-ladder.example/knowledge/explanation/why-a-registrar-role
---

# Overview

The README says where the bundle lives: `.lokf/` sits beside the code, notes and documents it distils, in the same tree and almost always the same git repository, the way `.git/` does. The bundle is `.lokf/knowledge/`, one real folder on every host, with a `knowledge_bundle` link beside it for folder pickers that hide dot-folders.

# Why one layout

The sidecar skill states the rule as "one layout, every host". `.lokf/knowledge/` is the name every skill, the toolkit, continuous integration and `llms.txt` address, so a tool written once works on a code repository, a notes vault and a shared folder alike. The link is for people: Finder and most folder pickers hide dot-directories, a repository listing shows nothing else, and a double-click in a file manager should land in the bundle. So the doorway is the one name a person needs to know, whatever they open it with.

The link is made from the repository root with a relative target, `ln -s .lokf/knowledge knowledge_bundle`, which keeps it valid after a clone or a move. `just lokf-link` from `.lokf/` does the same and recreates it on a machine where a sync service dropped it. On Windows a junction does the job with no elevated rights: `mklink /J knowledge_bundle .lokf\knowledge`.

# What each host does with it

The sidecar's `references/portability.md` goes host by host.

- **A code repository under git** carries the link itself. Git commits a symlink as a symlink.
- **An Obsidian vault as host** stays clean. Obsidian never indexes a dot-folder, and its file reconciler skips a link whose resolved path lies inside a folder it already watches. So a vault opened at the host root lists neither `.lokf/` nor `knowledge_bundle`, and the person opens `knowledge_bundle` itself as a second vault.
- **A synced or shared folder** (OneDrive, SharePoint, Drive, Dropbox, iCloud) syncs `.lokf/knowledge` as ordinary files but drops links, so the doorway is made per machine, or the bundle is opened by path.
- **Windows without symlink support** uses the junction above. A filesystem that supports neither skips the link; every skill and toolkit command still addresses `.lokf/knowledge` directly.

# The one rearrangement, and the one rule

A team that wants the bundle synced under a visible name may rearrange it by hand at the host root: move `.lokf/knowledge` to `knowledge_bundle` and link `.lokf/knowledge` onto it. Every skill still addresses `.lokf/knowledge` and follows the link, the workflow templates name both paths, and the Obsidian plugins detect a top-level `knowledge_bundle/` on their own. The one rule is never to lay the bundle down as a real folder inside an Obsidian vault: the vault indexes it like any other folder, and the exhibition leaks into the workshop's link suggestions, graph and search.
