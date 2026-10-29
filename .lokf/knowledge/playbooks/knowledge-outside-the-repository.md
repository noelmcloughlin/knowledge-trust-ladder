---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/knowledge-outside-the-repository
genre: how-to
title: Knowledge outside the repository
description: How the ingest mirrors Confluence pages, web pages and PDFs, files in another git repository and a command's output into `.lokf/mirror/`, with the manifest `.lokf/ingest.yaml`, the lock, sensitivity, the weekly pull request, and how the librarian cites a mirror file.
resource: docs/ingest.md
sources:
  - resource: docs/ingest.md
    id: docs-ingest.md
  - resource: skills/ktl-librarian/references/ingest.md
  - resource: skills/ktl-sidecar/templates/ingest.yaml
  - resource: CHANGELOG.md
dependsOn:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-sidecar-skill
relatedTo:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-librarian-skill
  - https://w3id.org/ktl/knowledge/playbooks/knowledge-sources
  - https://w3id.org/ktl/knowledge/policies/threat-model
generated:
  by: process:ktl-librarian
  at: "2026-10-29T00:48:33Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-20T23:23:33Z"
---

# Overview

Much of what a team knows lives outside the repository: a wiki space, a document at an intranet address, a file in another repository, the output of a command. The **ingest** brings a copy in, as `docs/ingest.md` says. A manifest names each source, a script writes it as Markdown under `.lokf/mirror/`, and a pull request shows what changed. The librarian then derives concepts from the copy as from any tracked file, citing both the copy and its origin. Nothing in the trust ladder changes: a concept derived from a wiki page is agent-derived until a person confirms it.

The ingest was released in 0.49.0, and 0.50.0 added the restore of lost mirror files and the scheduled prune (`CHANGELOG.md`).

# What can be mirrored

- **Confluence pages**, chosen by label, space, page, page tree or CQL query, on Cloud or Data Center.

- **Pages and documents at an address**: HTML, Markdown, plain text and PDF. A PDF with no text layer, such as a scan, is refused.

- **Files in another git repository**, a folder at a branch, tag or commit. A GitHub or GitLab wiki is such a repository. A run downloads the file list, then only the files that changed. Every such entry needs git 2.31 or later. Git follows no redirect with a credential. Where the manifest refuses private addresses, git follows no redirect, and an entry that names a host, not an IP address, needs git 2.37 or later, unless a proxy resolves its name.[^docs-ingest.md] So name a moved repository by its new address, and a host outside ASCII by its `xn--` form. An address that git's own configuration rewrites, by `url.<base>.insteadOf`, is refused.

- **The output of a command** the repository holds.

There is no fetcher for Jira. Attachments and images are not fetched, and a link to one keeps its origin address.

# The manifest, the mirror and the lock

- **The manifest**, `.lokf/ingest.yaml`, lists for each entry a place, a selector, who answers for the source (`owner`) and why the repository mirrors it (`why`). It holds no token: an `auth` block names environment variables. The sidecar lays its example down as `.lokf/ingest.yaml.sample`, and the ingest reads only `.lokf/ingest.yaml`.

- **The mirror**, `.lokf/mirror/<entry id>/`, holds one Markdown file per page or document. Each opens with a header: origin, title, version, digest of the bytes fetched, retrieval time and converter. A file is named by the item's stable identity, never its title. The workflow publishes only a name of letters, digits and `._/@+-`, so a file named otherwise is spelled with those characters and a digest of its name added, and its header keeps the name.

- **The lock**, `.lokf/ingest.lock.yaml`, records each item with a status: `ok`, `gone`, `unlisted`, `failed`, `refused` or `skipped`, the last for a binary file that a `git` entry's include matches.

The mirror is tracked, so the work list, the gate and coverage read it as repository content. Never clear it before a run: refresh it, since a run fetches only what moved and restores any file the disk has lost.

# Sensitivity

The script refuses what the repository's visibility does not allow. `public` may be committed anywhere, and `internal`, the default, only to a private repository. `confidential` is never committed: the copy goes to the ignored `.lokf/.cache/mirror/`, the concept names the origin as its `resource`, the work list cannot compare it, and a scheduled librarian reads text no person reviewed.

A confidential entry's records go to `.lokf/.cache/ingest.lock.yaml`, beside its copies. The committed lock says only how the entry's last run went, so no page's title, address or author is committed, and the summary counts the entry's items and names none. With `lock_details: true`, the committed lock records the entry's items as it does for any other entry. The script refuses a `confidential` entry when git does not ignore the cache or tracks a file in it. When an entry's sensitivity or `lock_details` changes, its next run moves its records and removes its files from the old folder, then fetches them into the new one.

# Turn it on

1. Install the ingest files with ktl-sidecar's Step 5, or its repair.
2. Copy `.lokf/ingest.yaml.sample` to `.lokf/ingest.yaml` and replace its examples. A sidecar installed before the sample existed gets it from the same repair.
3. Store each credential as a secret in the `knowledge-ingest` Environment, limited to the default branch, under the name the manifest gives. Every name starts `KNOWLEDGE_INGEST_`.
4. Set the repository variable `KNOWLEDGE_INGEST_ENABLED` to `true`, and allow GitHub Actions to create and approve pull requests.
5. Start one run from the Actions tab and read its summary.

The workflow runs on Sundays and keeps one pull request open on the branch `knowledge-ingest`, refreshed until a person merges it. A pull request closed without merging is a no: a scheduled run proposes the mirror again only once the manifest has changed. By hand, `bash .lokf/scripts/knowledge-ingest.sh` takes `--dry-run`, `--visibility private`, `--only <entry>`, `--prune` and `--patch`. A run starts no more work after 25 minutes, so it ends inside the workflow's 30, and the next run takes up what it did not reach.[^docs-ingest.md] `--time-limit 0` lifts the limit for a long first run by hand.

# What the librarian does

`skills/ktl-librarian/references/ingest.md` gives the rules. In a live session the librarian runs `knowledge-ingest.sh` before the work list. Unattended, it does not. A concept derived from a mirrored page names the mirror file as its `resource` and the origin as a `sources` entry, with the entry's `owner` as `author`. A `Reference` concept is the other way round. The source map gains one row per entry, naming the entry's folder. A file marked `gone` or `unlisted` stays while a concept cites it, and the librarian re-verifies each such concept. The librarian derives nothing from a file the lock does not mark `ok`.

# Security

The ingest keeps its secrets and its write token in separate jobs, and fetches only the addresses the manifest names, within size caps. Since 0.56.1 it checks the address each connection opens, so a name that answers a public address to the check and a private one to the connection reaches nothing, unless the manifest allows private addresses (`CHANGELOG.md`). `docs/threat-model.md` covers the ingest workflow.

Behind a proxy, the proxy resolves each name. The script still refuses a name that resolves locally to a private address, but it cannot check a name that resolves only at the proxy, so the proxy must refuse private addresses itself. Where the manifest refuses private addresses, git uses the proxy that `https_proxy` or `all_proxy` names for a `git` entry, and ignores any proxy in git's own configuration.

[^docs-ingest.md]: docs/ingest.md, What can be mirrored and By hand
