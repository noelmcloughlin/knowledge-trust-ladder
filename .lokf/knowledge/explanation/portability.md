---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/portability
title: "Portability: what works on each platform"
description: "What the skills keep, lose and use instead on each platform, as the sidecar's `references/portability.md` lists them: Linux, macOS, Windows, other forges, git with no forge, no git, an Obsidian vault, a package mirror or proxy, and Microsoft 365 Copilot; and how the preflight says which case a machine is."
genre: explanation
resource: skills/ktl-sidecar/references/portability.md
sources:
  - resource: skills/ktl-sidecar/references/portability.md
  - resource: skills/ktl-sidecar/SKILL.md
  - resource: skills/ktl-sidecar/references/prerequisites.md
  - resource: skills/ktl-curator/references/domain-vocabularies.md
about:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-sidecar-skill
relatedTo:
  - https://w3id.org/ktl/knowledge/glossary/host
  - https://w3id.org/ktl/knowledge/explanation/hosts-and-doorways
  - https://w3id.org/ktl/knowledge/playbooks/docent-in-m365-copilot
generated:
  by: process:ktl-librarian
  at: "2026-11-15T20:43:54Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-11-17T20:29:12Z"
---

# One matrix

The sidecar's `references/portability.md` is a matrix of platforms: what works on each, what is lost, and what takes its place. A platform here is the setting the skills run in at a [host](../glossary/host.md): the operating system and its shell, the forge, a synced folder, or an assistant. The matrix covers:

- Linux, git and GitHub, where everything works;
- macOS on its stock bash 3.2, with `shasum -a 256` where `sha256sum` is named;
- Windows from Git for Windows' bash, with a junction in place of the `ln -s` doorway, or from PowerShell through a one-line launch of that bash;
- GitLab, Codeberg, Forgejo and Gitea, where the GitHub Actions workflows are lost, ktl-website's deploy included, and the page names the three calls that talk to GitHub, which a port rewrites;
- git with no forge, where review happens by the host's own means and the forge-free gate checks confirmations;
- no git at all, where the platform's version history is the record of who changed what;
- an Obsidian vault as the host, where `knowledge_bundle` is opened as a vault of its own;
- a machine behind a package mirror or a proxy, or with a python3 older than 3.11, such as RHEL 9's 3.9 or Ubuntu 22.04's 3.10: the sidecar's scripts run from `.lokf/.venv` after `uv sync`, the committed lock is made against the index the gate's runner reads, and uv is told to trust the proxy's certificate;
- a Microsoft 365 Copilot declarative agent, which holds the docent, from a snapshot of the bundle packed inside the skill, and the auditor once it exists (see [The docent in Microsoft 365 Copilot](../playbooks/docent-in-m365-copilot.md)).

A SharePoint or OneDrive workspace with no git, whose curators sign in to Microsoft 365, would need an identity of its own. The curator's domain-vocabulary guidance records it as a shape held in reserve.

# Which case a machine is

The preflight the sidecar installs, `.lokf/scripts/knowledge-preflight.sh`, reports which case a machine is. Every skill runs it first, so a missing tool is named before a step is offered. `.lokf/.gitattributes` keeps a tracked bundle on LF line endings. The conventions script reads a file with CRLF line endings or a byte-order mark as it reads one with LF, and reports a sync client's conflict copy as a duplicate `id`.

[Why the bundle is in a hidden folder](hosts-and-doorways.md) says where the bundle sits on each kind of host, and why.
