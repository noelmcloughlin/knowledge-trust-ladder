---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/open-bundle-in-obsidian
title: "Open the knowledge bundle in Obsidian"
description: "How a knowledge bundle meets an Obsidian vault: two vaults, the workshop someone already keeps and the bundle opened as its own vault through the root-level knowledge_bundle link, which plugins go in it, and what each host does with the link."
genre: how-to
resource: docs/obsidian.md
sources:
- resource: docs/obsidian.md
- resource: skills/ktl-sidecar/SKILL.md
- resource: skills/ktl-sidecar/references/portability.md
- resource: skills/ktl-docent/references/obsidian.md
- resource: https://obsidian.md/help/settings
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
isPartOf:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/explanation/hosts-and-doorways
  - https://knowledge-trust-ladder.example/knowledge/explanation/why-a-registrar-role
---

# Overview

`docs/obsidian.md` is for the people who open the bundle in Obsidian. The vault they already have is the workshop, and nothing in it is moved or migrated. The bundle is the exhibition: the checked part of what the workshop knows, and the front door teammates, continuous integration and agents come through. It opens as a small vault of its own, and the two never index the same file.

# Steps

1. **File, Open folder as vault**, and pick `knowledge_bundle` at the root of the host. That link is the doorway the sidecar laid beside `.lokf/`, so the bundle has a name a folder picker can see. Open the link itself, never the host root: a vault opened at the root lists neither the dot-folder nor the link, which is exactly what keeps the workshop clean.
2. **Install the plugins in that vault.** Obsidian installs plugins per vault. There is nothing to configure: the root `index.md` carries the bundle's header, so the whole vault is the bundle.
3. **Edit and confirm there.** Obsidian writes that vault's workspace state through the link into `.lokf/knowledge/.obsidian/`, which the sidecar's `.gitignore` already excludes.

If `knowledge_bundle` is missing, because a sync service dropped it or a Windows checkout shows it as a small text file, open `.lokf/knowledge` by typing the path into the picker, or make the link once from the host root: `ln -s .lokf/knowledge knowledge_bundle`, `just lokf-link` from `.lokf/`, or `mklink /J knowledge_bundle .lokf\knowledge` on Windows.

# Plugin for skill

Obsidian is optional in both directions. The skills rely on `lokf validate`, not on a plugin, and the plugins work on any LOKF bundle however it was made. KTL Registrar runs the same checks as the registrar gate, as you type. KTL Curator runs the curator's review session at the desk. The librarian has no plugin, because deriving is an agent's job, and the docent is reached through the skill or `lokf serve`.

# Why never a real folder inside a vault

Obsidian never indexes a dot-folder, and its file reconciler skips a link whose resolved path lies inside a folder it already watches. So a vault opened at the host root lists neither `.lokf/` nor `knowledge_bundle`. A real folder inside the vault is indexed like any other, and so is a link whose target lies outside the vault. Either way the exhibition enters the workshop's link suggestions, quick switcher, graph and search. Obsidian's Excluded files setting hides it from search, graph view and unlinked mentions, but only makes it less noticeable in the quick switcher and link suggestions, and Obsidian Sync carries no links.

# Host by host

In a code repository, concepts cite sources that sit above the small vault, so no plugin can open them from there; KTL Curator shows such a source as a path with a copy button. In a vault kept in git, the sidecar lands beside the notes, `.lokf/` is a dot-folder the vault never indexes, and the person curates in a second vault opened through the doorway. On a shared drive or SharePoint library, links do not sync, so the doorway is made per machine or the bundle is opened by path. With many hosts and one vault, each repository's `.lokf/knowledge` can be linked into a folder of the person's own vault and listed under the plugins' Bundle root folders setting, at the cost the plugin READMEs name.
