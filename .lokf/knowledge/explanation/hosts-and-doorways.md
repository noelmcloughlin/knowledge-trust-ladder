---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/hosts-and-doorways
title: Hosts and doorways - where the bundle's real folder lives
description: Why the bundle is `.lokf/knowledge`, one real folder on every host, with `knowledge_bundle` beside it as a link for people and folder pickers; what the visible layout tried and why it was retired; and what a shared folder that is not a vault may still do by hand.
genre: explanation
resource: skills/ktl-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-06T09:49:14Z"
status: draft
about:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
- https://knowledge-trust-ladder.example/knowledge/playbooks/open-bundle-in-obsidian
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/playbooks/docent-in-m365-copilot
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
- https://knowledge-trust-ladder.example/knowledge/explanation/why-a-registrar-role
sources:
- resource: skills/ktl-sidecar/SKILL.md
- resource: skills/ktl-sidecar/references/portability.md
- resource: docs/obsidian.md
- resource: CHANGELOG.md
verified:
- by: process:ktl-librarian
  at: "2026-10-06T11:10:52Z"
---

# The pattern

A LOKF bundle is a **sidecar**: it sits beside the raw sources it distils, in the same folder tree and normally the same git repository. The sidecar is `.lokf/`, and the bundle is `.lokf/knowledge/`. The tooling (`pyproject.toml`, `justfile`, `scripts/`, `feedback.md`) sits next to the bundle. This is the same shape as `.git/`, `.github/`, `.devcontainer/` and, for an Obsidian user, `.obsidian/`: a dot-folder the tools own, kept beside the content people own.

Because the dot-folder is hidden from Finder, from most folder pickers and, in effect, from a repository listing, `ktl-sidecar` Step 2 adds a **doorway**: `knowledge_bundle`, a link at the host root onto the bundle. The bundle therefore has **two names**:

| Name | Who addresses it | What it is |
| --- | --- | --- |
| `.lokf/knowledge` | every skill, the `lokf` toolkit, CI's `knowledge-registrar.yaml`, `llms.txt` | the real folder, on every host |
| `knowledge_bundle` | people, folder pickers, file managers, Obsidian's *Open folder as vault* | a symlink (junction on Windows), added by the sidecar's optional Step 2 |

Every tool and every person finds the bundle at the name they know. The sidecar no longer chooses which of the two is the real folder: it is always the hidden one.

# Hosts

- **Code repository.** Readers are developers, agents, and CI. The hidden real folder keeps the bundle out of the way. The doorway is how a person browses to it, and how Obsidian opens it as a vault of its own.
- **Notes vault.** The sidecar is installed beside the notes. The vault never indexes `.lokf/`, and skips the doorway too, because its target resolves inside the vault being indexed (see [Open the knowledge bundle in Obsidian](../playbooks/open-bundle-in-obsidian.md)). So the **workshop** and the **exhibition** never index the same file: the person curates in a second vault opened through the doorway. What the vault does *not* get is the bundle in its own graph, search or Sync, and that is what keeps the workshop clean.
- **Shared drive or SharePoint library.** Readers are whoever the service shows the folder to. `.lokf/` syncs (Microsoft's restricted-name list has nothing against a leading dot), so the real folder is the same on every machine. OneDrive syncs neither symbolic links nor junctions, so the doorway is per machine (`just lokf-link`) or the bundle is opened by path. A library nobody reaches through git may be rearranged by hand for a synced visible name, and the sidecar's `references/portability.md` says how. A shared folder that is also a vault must not be.

# What each host can do

Since 2026-09-17 the sidecar's `references/portability.md` is a matrix, host by host, of what works, what is lost and the substitute. It covers:

- Linux;
- macOS on its stock bash 3.2, with `shasum -a 256` where `sha256sum` is named;
- Windows from Git for Windows' bash, or from PowerShell through a one-line launch of that bash;
- GitLab, Forgejo and Gitea, where the three GitHub Actions workflows are the only loss and the recipe names the three calls to rewrite;
- git with no forge;
- no git at all, where the platform's version history is the record of who changed what;
- an Obsidian vault;
- since 2026-09-24, a Microsoft 365 Copilot declarative agent, which can hold only the read-only roles, as a snapshot of the bundle packed inside the skill (see [The docent in Microsoft 365 Copilot](../playbooks/docent-in-m365-copilot.md)).

A SharePoint or OneDrive workspace with no git whose curators sign in to Microsoft 365 would need an identity of its own. The curator's domain-schema guidance records it as a shape held in reserve.

A preflight the sidecar installs, `.lokf/scripts/knowledge-preflight.sh`, reports which case a machine is. Every skill runs it first, so a missing tool is said before a step is offered. `.lokf/.gitattributes` keeps a tracked bundle on LF. The conventions script reads a CRLF or byte-order-marked file the same as LF, and reports a sync client's conflict copy as a duplicate `id`.

# The rule: one layout, and how it was settled

On 2026-09-12 the sidecar's Step 0 began asking which kind of host it was in. For a notes vault or a shared folder, it installed the bundle the other way round: the **visible layout**. In it, `knowledge_bundle/` was a real folder at the host root (or inside the vault, when the vault was a subfolder of the host), and `.lokf/knowledge` was a link onto it. The intent was that an Obsidian user would see the bundle in their own vault's explorer, graph, search and Sync, and that both plugins would detect it with nothing to configure. The visible layout cost the tooling:

- a `visible` variable and a `lokf-link` recipe that recreated the tools' link where a sync service dropped it;
- two extra layout test cases;
- both workflows and the wrapper naming the bundle under both paths, because a git pathspec never traverses a symlink.

A day later, the intent turned out to be the problem. Obsidian indexes a real folder inside a vault like any other, so the exhibition's concepts appeared in the workshop: link suggestions, the quick switcher, graph and search all mixed exhibits with everyday notes. *Settings → Files and links → Excluded files* only makes an excluded folder less noticeable in the quick switcher and link suggestions.

The natural Obsidian workflow is two vaults: the one someone already has for the workshop, and the bundle opened as its own for the exhibition, which is where the plugins do their work. A doorway link supports that on every host without ever appearing in the workshop. So on 2026-09-13 the visible layout was retired:

- one layout, with the doorway by default;
- Step 0's host decision and the `visible` variable gone;
- `lokf-link` repurposed to create or recreate the doorway.

The reversal keeps these, because they cost nothing and still cover a shared folder rearranged by hand:

- the dual pathspecs in the Step 5 templates;
- the plugins' auto-detection of a top-level `knowledge_bundle/`, and their *Bundle root folders* setting;
- the junction guidance for Windows.
