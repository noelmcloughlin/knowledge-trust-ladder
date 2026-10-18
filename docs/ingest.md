# Knowledge outside the repository

A bundle cites what the librarian can read, and the librarian reads the repository. Much of what a team knows lives elsewhere: a wiki space, a document on an intranet address, a file in another repository, the output of a command. The ingest brings a copy in. A manifest names each source, a script fetches it and writes it as Markdown under `.lokf/mirror/`, and a pull request shows what changed. The librarian then derives concepts from the copy as it derives them from any tracked file, and every concept cites both the copy and the page it came from.

Nothing in the trust ladder changes. A concept derived from a wiki page is agent-derived until a person confirms it, as a concept derived from a README is. What the ingest adds is reach: Knowledge Trust Ladder (KTL) can keep a bundle accurate about sources it does not own, with the same work list, the same gate and the same review.

## The three parts

**The manifest**, `.lokf/ingest.yaml`, lists what to mirror. Each entry names a place, a selector, who answers for the source, and why this repository mirrors it. It holds no token; an `auth` block names environment variables.

**The mirror**, `.lokf/mirror/<entry id>/`, holds the fetched text, one Markdown file per page or document. Each file opens with a header: the origin, the title, the version, the digest of the bytes fetched, when they were fetched, and which converter stood between the bytes and the Markdown. A file is named by the item's stable identity, a page id or a path, never by its title, so a retitled page is the same file.

**The lock**, `.lokf/ingest.lock.yaml`, records the same per item, with a status: `ok`, `gone` when the source answered 404 or 410, `unlisted` when the selector no longer returns it, `failed` when a request did not complete, or `refused` with the reason. The mirror and the lock change only when content changes, so a run that finds nothing new writes nothing.

## The manifest

```yaml
ingest_version: "1"
mirror: .lokf/mirror
max_total_bytes: 50000000

services:
  confluence:
    kind: confluence
    site: https://acme.atlassian.net
    auth:
      scheme: basic
      user_env: KNOWLEDGE_INGEST_ATLASSIAN_USER
      env: KNOWLEDGE_INGEST_ATLASSIAN_TOKEN

defaults:
  sensitivity: internal
  max_items: 200
  max_item_bytes: 1000000

entries:
  - id: platform-runbooks
    service: confluence
    select:
      label: ktl
      space: PLAT
    owner: team:platform
    why: the runbooks the on-call rota follows; this repository holds the code they run

  - id: vendor-protocol
    kind: http
    urls:
      - https://vendor.example/spec/v3.pdf
    convert: pdf-text
    sensitivity: public
    owner: vendor-example/v3
    why: the wire protocol the gateway implements
```

A service is a site and its credential, written once; an entry names the service and its own selector. An entry's `id` is lowercase letters, digits and hyphens, since it names a folder. `owner` is the actor string the concept's source carries as `author`, and `why` is the entry's row in the bundle's source map.

Four kinds of source, each with its selector:

- `confluence`: `select` names a `label` with an optional `space`, a `space`, a `page` id, a `tree` (a page and its descendants) or a `cql` query. The site is named as a person knows it; the script resolves the cloud id when a scoped token needs Atlassian's gateway. Confluence Data Center works through the same entry with `api: datacenter`.

- `http`: a list of `urls` serving HTML, Markdown, plain text or a PDF. The server's ETag and Last-Modified are used when it gives them, and the digest of the bytes otherwise. `convert` names the converter when the content type does not: `html-markdown`, `pdf-text` or `text`.

- `git`: a `url`, a `ref` and a `path` in another repository, with `include` and `exclude` patterns (`*.md` by default). The commit is the version. A GitHub or GitLab wiki is a git repository, and this kind mirrors it.

- `command`: the tracked path of a command this repository holds, with `args` and a `timeout`. Its standard output is the text, and the digest of the command's own file is recorded beside the output's, so a changed command is a moved source. A command-line client for a service the script has no fetcher for, a schema dump of a database, an export from a desktop tool.

Three caps bound a run: `max_items` per entry, `max_item_bytes` per item and `max_total_bytes` for the mirror. A selector that returns more than `max_items` is refused whole, never mirrored in part. `disabled: true` pauses an entry and keeps its mirror. `authors: false` leaves account ids out of the headers. `reference: true` asks for a Reference concept per mirrored item, which `--patch` writes for the pen.

## Sensitivity

`sensitivity` is `public`, `internal` or `confidential`. A committed mirror is published as far as the repository is, so the script refuses what the repository's visibility does not allow:

- `public` may be committed to any repository;

- `internal`, the default, may be committed to a private repository only;

- `confidential` is never committed. The copy goes to `.lokf/.cache/mirror/`, which the sidecar's gitignore already covers, and only the lock records it. A concept then names the origin as its `resource`, the work list cannot compare it, and a scheduled librarian reads text no person reviewed. It is a fallback with named costs.

The workflow passes the repository's visibility from the forge. By hand, the script asks `gh` when it is signed in, and otherwise counts the repository as public until `--visibility private` says otherwise.

## Secrets

Each `auth` block names its variables, and every name starts `KNOWLEDGE_INGEST_`. The workflow hands the script the repository secrets of those names and no other, and the script prints no value. For Confluence Cloud, store an API token with read scopes and an expiry as the token, and the account's email as the user. For a repository, a fine-grained token with Contents read. By hand, set the same names in the environment.

## Turn it on

1. Install the sidecar's ingest files with ktl-sidecar's Step 5, or its repair: the script and its shell half under `.lokf/scripts/`, the workflow, and the pull request template.
2. Copy the sidecar's `templates/ingest.yaml` to `.lokf/ingest.yaml` and replace its examples with your sources.
3. Store each credential as a repository secret of the name the manifest gives.
4. Set the repository variable `KNOWLEDGE_INGEST_ENABLED` to `true`, and turn on *Allow GitHub Actions to create and approve pull requests* under Settings, Actions, General.
5. Start one run from the Actions tab and read its summary.

The workflow runs on Sundays and keeps one pull request open on the branch `knowledge-ingest`, refreshed each week until it is merged. The sidecar's [automation page](../skills/ktl-sidecar/references/automation.md#knowledge-ingestyaml-knowledge-outside-the-repository) has the workflow's jobs and switches.

## By hand

```sh
bash .lokf/scripts/knowledge-ingest.sh --dry-run                 # list and compare, write nothing
bash .lokf/scripts/knowledge-ingest.sh --visibility private      # every entry
bash .lokf/scripts/knowledge-ingest.sh --only platform-runbooks  # one entry
bash .lokf/scripts/knowledge-ingest.sh --prune                   # remove gone and unlisted files no concept cites
bash .lokf/scripts/knowledge-ingest.sh --patch                   # Reference concepts for the entries that ask
```

The librarian runs the first command itself at the start of a live session when the manifest exists. Commit the mirror and the lock with the bundle change, as the person who ran it. A host with no git runs the script the same way, and the lock is its record.

## The pull request

The body is the run's summary: each entry, what moved, what went away, what could not be fetched and why. Then the checklist. Read the diff as you would read the page: is this text something the repository should hold? A page that should not be here comes out of the manifest, not out of the diff. A file marked `gone` or `unlisted` stays until the librarian has asked about the concepts that cite it; `--prune` removes one that no concept cites. A line marked `failed` with a credential's name is a secret not yet set, or expired.

The pull request starts no checks, since the job's own token opened it, and the mirror is text the registrar's conventions do not read. Merge it, and the librarian's next run reads what changed.

## What the librarian does next

The work list names each concept whose mirror file moved, by git history, as it names any moved source. A concept derived from a mirrored page names the mirror file as its `resource` and the origin as a `sources` entry with its title, the entry's `owner` as `author` and the page's `last_modified`. A `Reference` concept, where one is wanted, is the other way round: the origin as `resource` and the mirror under `sources`. The source map gains one row per entry, never per item, and names the entry's folder, so `knowledge-report.sh coverage` counts the mirror as mapped. The librarian's [ingest reference](../skills/ktl-librarian/references/ingest.md) has the rules in full.

The curator and the docent need nothing new. A mirror file is a tracked path, so the curator's evidence-first step quotes it and its moved-source check sees it. The docent opens it to check a value, and names the origin, the version and the retrieval date in its footer.

## What stays out

The first version has no fetcher for Jira. An issue moves whenever anyone comments, service desk customers raise requests without a licence, and most issues carry work rather than knowledge. A host that keeps decisions in labelled issues reaches them through a `command` entry with a client of its own. A scanned PDF has no text layer and is refused. Attachments and images are not fetched; a link to one keeps its origin address. A source that is not text, such as a database, stays a scope descriptor in a concept's `sources`, unless a command can print it.

## Security

The job that holds the secrets has no write token, and the job that writes has no secret. The script fetches only the addresses the manifest names, and caps every body and the mirror as a whole. It refuses a private or link-local address unless the manifest allows them, drops the credential on a redirect to another host, and removes every character a reader cannot see. What it mirrors reaches the scheduled librarian only after a person merges the pull request, so a mirror file holds the same place as any other repository content. The [threat model](threat-model.md#the-ingest-workflow) says the rest.
