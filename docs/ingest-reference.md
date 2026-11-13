# The ingest: sources, manifest, mirror and lock

This page is for whoever writes `.lokf/ingest.yaml`, or reads what a run recorded. [How to mirror knowledge from outside the repository](ingest.md) gives the steps.

## What can be mirrored

- **Confluence pages**, chosen by label, space, page, page tree or CQL query, on Cloud or Data Center.
- **Pages and documents at an address**: HTML, Markdown, plain text and PDF. Most PDFs work, meaning any whose text can be selected and copied in a viewer. A scan of paper holds pictures of pages and no text, and is refused.
- **Files in another git repository**, a folder at a branch, tag or commit. A GitHub or GitLab wiki is such a repository. A run downloads the file list, then only the files that changed. Every such entry needs git 2.31 or later. Git follows no redirect with a credential, or where the manifest refuses private addresses. Where the manifest refuses private addresses, an entry that names a host, not an IP address, needs git 2.37 or later, unless a proxy resolves its name. So name a moved repository by its new address, and a host outside ASCII by its `xn--` form. Name the address git fetches, too: one that git's own configuration rewrites, by `url.<base>.insteadOf`, is refused.
- **The output of a command** this repository holds: a client for a service the ingest has no fetcher for, a schema dump, an export.

There is no fetcher for Jira, since issues are unsuitable as knowledge sources. Attachments and images are not fetched, and a link to one keeps its origin address. A source that is not text, such as a database, is mirrored only through a command that prints it.

## The manifest

The manifest, `.lokf/ingest.yaml`, lists what to mirror: for each entry a place, a selector, who answers for the source and why this repository mirrors it. It holds no token. An `auth` block names environment variables.

```yaml
ingest_version: "1"
max_total_bytes: 50000000        # the whole mirror; an item that would pass it is refused
allow_private_addresses: false   # true permits intranet addresses, http:// sites and local git paths

services:                        # a site and its credential, written once
  confluence:
    kind: confluence
    site: https://acme.atlassian.net   # as a person knows it; api: datacenter for Data Center
    auth:
      scheme: basic                    # basic, bearer or header; values come from the environment
      user_env: KNOWLEDGE_INGEST_ATLASSIAN_USER
      env: KNOWLEDGE_INGEST_ATLASSIAN_TOKEN
  github:
    kind: git
    auth:
      scheme: basic                    # a fine-grained token with Contents read
      env: KNOWLEDGE_INGEST_GITHUB_TOKEN

defaults:                        # what an entry inherits
  sensitivity: internal          # public, internal or confidential; see below
  lock_details: false            # true records a confidential entry's items in the committed lock
  max_items: 200                 # a selector over this is refused whole, never mirrored in part
  max_item_bytes: 1000000        # each body fetched, and the Markdown written from it
  authors: true                  # false leaves account ids out of the headers

entries:
  - id: platform-runbooks        # lowercase letters, digits and hyphens: it names the folder
    service: confluence
    select:                      # one of: label with an optional space, space, page, tree, cql
      label: ktl
      space: PLAT
    owner: team:platform         # the author the concept's source names
    why: the runbooks the on-call rota follows   # the entry's row in the source map

  - id: ops-wiki                 # a GitHub or GitLab wiki is a git repository
    service: github
    url: https://github.com/acme/platform.wiki.git   # https; http and local paths need allow_private_addresses
    ref: master                  # a branch, a tag or a commit; the commit is the version
    path: runbooks
    include: ["*.md"]            # the default; a binary file that matches is skipped and named
    exclude: ["draft-*"]
    owner: team:ops
    why: the on-call wiki, which lives beside the repository

  - id: vendor-protocol
    kind: http                   # HTML, Markdown, text or PDF; ETag and Last-Modified when given
    urls:
      - https://vendor.example/spec/v3.pdf
    convert: pdf-text            # html-markdown, pdf-text or text, when the content type does not say
    sensitivity: public
    license: https://vendor.example/terms
    owner: vendor-example/v3
    reference: true              # --patch drafts a Reference concept per mirrored file
    why: the wire protocol the gateway implements

  - id: schema-dump
    kind: command                # a tracked command's output is the text; its own digest is recorded too
    command: .lokf/ingest/schema-dump.sh
    args: ["--format", "markdown"]
    timeout: 120
    owner: team:data
    disabled: true               # pauses the entry and keeps its mirror
    why: the live database schema
```

A command is code the repository runs in a job that holds secrets, so commit one a person has read. It receives the variables its own `auth` block names, and its last error line is written to the lock. An entry taken out of the manifest loses its folder on the next run, and the summary names each file a concept still cites.

## The mirror

The mirror, `.lokf/mirror/<entry id>/`, holds one Markdown file per page or document. Each opens with a header: origin, title, version, digest of the bytes fetched, retrieval time and converter. A file is named by the item's stable identity, a page id or a path, never its title, so a retitled page is the same file. The workflow publishes a name of letters, digits and `._/@+-` only, so a file named otherwise is spelled with those characters, with a digest of its name added: `Release Notes.md` becomes `Release-Notes-2040e8c7.md`, and its header keeps the name. Links are made absolute against the address the page was served from: after a redirect the header names that address, without its query, as `redirected_to`. A redirect from https to http is refused, whatever `allow_private_addresses` says: a manifest names the http address itself where plain http is meant. A PDF carries a comment before each page so a concept can cite the page.

The mirror is tracked, and stays so: the work list, the gate and coverage all read it as repository content, and the scheduled librarian holds no secret with which to fetch. Never clear it before a run. Refresh it instead, since a run fetches only what moved and restores any file missing from the disk. `git checkout -- .lokf/mirror` brings back committed files without a fetch.

## The lock

The lock, `.lokf/ingest.lock.yaml`, records the same per item, with one of these statuses:

- `ok` for a current copy;
- `gone` after a 404 or 410;
- `unlisted` when the selector no longer returns it, or returns a file that is binary now;
- `failed` when a request did not complete;
- `refused`, with the reason;
- `skipped` for a binary file that a `git` entry's include matches.

The mirror and the lock change only when content changes, or when the entry's `authors`, `license` or `convert` changes, or the version of a converter, which each header names as `converted_by`. The entry's record keeps a digest of those, and when it differs the next run fetches and writes every item again. A file it cannot fetch, such as one whose page left the selection, gets only its header written again.

Each item's record keeps `mirror_sha256`, the digest of its file as written. A file edited by hand, like one the disk has lost, is fetched and written again, and `--status` counts both. A record from before the digest was kept is treated the same way, so the first runs after that upgrade write the mirror again, as many items a run as the time limit allows.

## Sensitivity

A committed mirror is published as far as the repository is, so the script refuses what the repository's visibility does not allow. `public` may be committed anywhere. `internal`, the default, may be committed to a private repository only. `confidential` is never committed: the copy goes to the ignored `.lokf/.cache/mirror/`, a concept names the origin as its `resource`, the work list cannot compare it, and a scheduled librarian reads text no person reviewed.

A confidential entry's records go to `.lokf/.cache/ingest.lock.yaml`, beside its copies. The committed lock says only how the entry's last run went, so no page's title, address or author is committed. The summary counts the entry's items and names none. With `lock_details: true`, the committed lock records the entry's items, as it does for any other entry. The script refuses a `confidential` entry when git does not ignore the cache or tracks a file in it. When an entry's sensitivity or `lock_details` changes, its next run moves its records and removes its files from the old folder, then fetches them into the new one.

The workflow passes the repository's visibility from the forge. By hand, the script asks `gh` when it is signed in, and otherwise counts the repository as public until `--visibility private` says otherwise.

## What the librarian does with a mirror

The work list names each concept whose mirror file moved, by git history, as it names any moved source. A concept derived from a mirrored page names the mirror file as its `resource` and the origin as a `sources` entry, with the entry's `owner` as `author` and the page's `last_modified`. A `Reference` concept is the other way round: the origin as `resource` and the mirror under `sources`. The source map gains one row per entry, naming the entry's folder, so `knowledge-report.sh coverage` counts the mirror as mapped. The librarian's [ingest reference](../skills/ktl-librarian/references/ingest.md) has the rules.

The curator and the docent need nothing new. A mirror file is a tracked path: the curator quotes it under evidence first, and the docent opens it to check a value and names the origin, version and retrieval date in its footer.

## Security

The ingest keeps its secrets and its write token in separate jobs, and fetches only the addresses the manifest names, within size caps. The [threat model](threat-model.md#the-ingest-workflow) says what else guards it.

Behind a proxy, the proxy resolves each name. The script still refuses a name that resolves locally to a private address. It cannot check a name that resolves only at the proxy, so the proxy must refuse private addresses itself. Where the manifest refuses private addresses, git uses the proxy that `https_proxy` or `all_proxy` names for a `git` entry, and ignores any proxy in git's own configuration.
