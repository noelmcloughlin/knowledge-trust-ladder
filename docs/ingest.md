# Knowledge outside the repository

The librarian reads the repository, and a bundle cites what the librarian can read. Much of what a team knows lives elsewhere: a wiki space, a document on an intranet address, a file in another repository, the output of a command. The ingest brings a copy in. A manifest names each source, a script writes it as Markdown under `.lokf/mirror/`, and a pull request shows what changed. The librarian then derives concepts from the copy as from any tracked file, citing both the copy and its origin.

Nothing in the trust ladder changes. A concept derived from a wiki page is agent-derived until a person confirms it, as one derived from a README is. Knowledge Trust Ladder (KTL) keeps the same work list, gate and review; the ingest adds reach.

## The three parts

**The manifest**, `.lokf/ingest.yaml`, lists what to mirror: for each entry a place, a selector, who answers for the source and why this repository mirrors it. It holds no token. An `auth` block names environment variables.

**The mirror**, `.lokf/mirror/<entry id>/`, holds one Markdown file per page or document. Each opens with a header: origin, title, version, digest of the bytes fetched, retrieval time and converter. A file is named by the item's stable identity, a page id or a path, never its title, so a retitled page is the same file. Links are made absolute, and a PDF carries a comment before each page so a concept can cite the page.

**The lock**, `.lokf/ingest.lock.yaml`, records the same per item with a status: `ok`, `gone` after a 404 or 410, `unlisted` when the selector no longer returns it, `failed` when a request did not complete, `refused` with the reason. The mirror and the lock change only when content changes.

## The manifest

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
  max_items: 200                 # a selector over this is refused whole, never mirrored in part
  max_item_bytes: 1000000
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

A `command` is code the repository runs with its secrets near, so commit one a person has read. It receives the variables its own `auth` block names, and its last error line goes into the lock. An entry taken out of the manifest loses its folder on the next run, and the summary names each file a concept still cites.

## Sensitivity

A committed mirror is published as far as the repository is, so the script refuses what the repository's visibility does not allow. `public` may be committed anywhere. `internal`, the default, may be committed to a private repository only. `confidential` is never committed: the copy goes to the ignored `.lokf/.cache/mirror/`, a concept names the origin as its `resource`, the work list cannot compare it, and a scheduled librarian reads text no person reviewed.

The workflow passes the repository's visibility from the forge. By hand, the script asks `gh` when it is signed in, and otherwise counts the repository as public until `--visibility private` says otherwise.

## Turn it on

1. Install the ingest files with ktl-sidecar's Step 5, or its repair: the script and its shell half under `.lokf/scripts/`, the workflow and the pull request template.
2. Copy the sidecar's `templates/ingest.yaml` to `.lokf/ingest.yaml` and replace its examples.
3. Store each credential as a repository secret under the name the manifest gives. Every name starts `KNOWLEDGE_INGEST_`, and the workflow hands over those secrets only. For Confluence Cloud, an API token with read scopes and an expiry, with the account's email as the user. A git credential needs git 2.31 or later.
4. Set the repository variable `KNOWLEDGE_INGEST_ENABLED` to `true`, and turn on *Allow GitHub Actions to create and approve pull requests* under Settings, Actions, General.
5. Start one run from the Actions tab and read its summary.

The workflow runs on Sundays and keeps one pull request open on the branch `knowledge-ingest`, refreshed until merged. The sidecar's [automation page](../skills/ktl-sidecar/references/automation.md#knowledge-ingestyaml-knowledge-outside-the-repository) has its jobs and switches.

## By hand

```sh
bash .lokf/scripts/knowledge-ingest.sh --dry-run                 # list and compare, write nothing
bash .lokf/scripts/knowledge-ingest.sh --visibility private      # every entry
bash .lokf/scripts/knowledge-ingest.sh --only platform-runbooks  # one entry
bash .lokf/scripts/knowledge-ingest.sh --prune                   # remove gone and unlisted files no concept cites
bash .lokf/scripts/knowledge-ingest.sh --patch                   # Reference concepts for the entries that ask
```

Set the same variable names in the environment. The librarian runs the first command itself at the start of a live session. Commit the mirror and the lock with the bundle change. A host with no git runs the script the same way, and the lock is its record.

## The pull request

The body is the run's summary, then the checklist. Read the diff as you would read the page: is this text something the repository should hold? A page that should not be here comes out of the manifest, not out of the diff. A file marked `gone` or `unlisted` stays until the librarian has asked about the concepts that cite it. A line marked `failed` with a credential's name is a secret not yet set, or expired; the run shows it as a warning too.

A pull request closed without merging is a no: a scheduled run proposes the mirror again only once the manifest has changed, and a run started by hand proposes it now. The pull request starts no checks, since the job's own token opened it, and the mirror is text the registrar's conventions do not read. Merge it, and the librarian's next run reads what changed.

## What the librarian does next

The work list names each concept whose mirror file moved, by git history, as it names any moved source. A concept derived from a mirrored page names the mirror file as its `resource` and the origin as a `sources` entry, with the entry's `owner` as `author` and the page's `last_modified`. A `Reference` concept is the other way round: the origin as `resource` and the mirror under `sources`. The source map gains one row per entry, naming the entry's folder, so `knowledge-report.sh coverage` counts the mirror as mapped. The librarian's [ingest reference](../skills/ktl-librarian/references/ingest.md) has the rules.

The curator and the docent need nothing new. A mirror file is a tracked path: the curator quotes it under evidence first, and the docent opens it to check a value and names the origin, version and retrieval date in its footer.

## What stays out

There is no fetcher for Jira: issues are unsuitable as knowledge sources. A PDF is supported when its text can be selected and copied in a viewer, which is the case for one saved from a word processor or exported from a wiki. A PDF made by scanning paper holds pictures of pages, so there is no text to copy, and it is refused. Attachments and images are not fetched; a link to one keeps its origin address. A source that is not text, such as a database, is mirrored only when a `command` can print it.

## Security

The job that holds the secrets has no write token, and the job that writes has no secret. The script fetches only the addresses the manifest names and caps every body and the mirror as a whole. It refuses private and link-local addresses unless the manifest allows them, drops the credential on a redirect to another host, and removes every character a reader cannot see apart from the joiners some scripts spell with. A git credential reaches git through its environment, scoped to the entry's address. The [threat model](threat-model.md#the-ingest-workflow) says the rest.
