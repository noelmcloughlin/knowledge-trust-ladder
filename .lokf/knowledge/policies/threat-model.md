---
type: Policy
id: https://w3id.org/ktl/knowledge/policies/threat-model
title: Threat model
description: "The security design the three KTL repositories share, kept in one place so each SECURITY.md can link to it: repository hardening, the human:-attribution gate on a verified event, and the prompt-injection guard for each input path that reads content it did not author."
genre: reference
resource: docs/threat-model.md
generated:
  by: process:ktl-librarian
  at: "2026-10-26T20:05:58Z"
verified:
  - by: process:ktl-librarian
    at: "2026-10-20T23:23:33Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T01:15:05Z"
references:
  - https://w3id.org/ktl/knowledge/policies/security
  - https://w3id.org/ktl/knowledge/policies/ai-covenant
sources:
  - resource: docs/threat-model.md
  - resource: CHANGELOG.md
  - resource: scripts/validate-repository.sh
  - resource: skills/ktl-sidecar/templates/scripts/knowledge-conventions.sh
status: draft
---

# Overview

The page was added on 2026-09-14, when the design moved out of `SECURITY.md` and into it across the three KTL repositories (`knowledge-trust-ladder`, KTL Registrar, KTL Curator). Each repository's `SECURITY.md` says how to report, what that repository owns, and what it inherits from here. `scripts/validate-repository.sh` check 9 records this path and six of its headings, the sync workflow's and the website's since 3114239 among them, as ones a sibling depends on.

**Interactive use is advisory, not enforced.** A skill's `Scope:` line is prose, not a checked permission. An agent run interactively has whatever access its harness grants, and only the scheduled `knowledge-librarian.yaml` enforces its scope, because nothing is watching it run.

The skills ktl-curator, ktl-librarian, ktl-prose, ktl-sidecar and ktl-website also run the repository's scripts from `.lokf/scripts/`. Anyone who can commit to the repository can change those scripts, so a skill runs them as the repository's code. ktl-website's build also runs `site.config.mjs`, the site's files under `website/`, and the commands `site.config.mjs` names, or a `gen-doc` recipe it finds, to build the schema's pages and the data, and they are the repository's code too. The preflight's `copies` line cannot check them, because the preflight is one of them.

Since 2026-10-05, ktl-docent runs none of them. It runs its own copies of `knowledge-report.sh` and `knowledge-feedback.sh`, which a check in `knowledge-trust-ladder` holds byte-identical to their templates, so a question runs no code the repository supplies. That holds only where the skill comes from a source the reader trusts, since a repository that holds its own copy of a skill supplies the instructions and the scripts.

**Repository hardening**:

- Actions are pinned to commit SHAs everywhere, including the six templates under `skills/ktl-sidecar/templates/github/` and `skills/ktl-website/templates/github/`. Dependabot bumps the workflow pins, and the templates are bumped by hand, since Dependabot scans only `.github/workflows/`.
- `permissions: {}` is at the top of every workflow.
- The agent step runs the reviewed, in-repo wrapper, never a repository variable's content as a command. `AGENT_CLI` chooses the agent, `KNOWLEDGE_LIBRARIAN_ENABLED` turns it on, and the workflow triggers only on `schedule` and `workflow_dispatch`. A domain host's members script takes the job token as `KNOWLEDGE_FEDERATE_TOKEN`, removes it from its own environment, and hands it to `gh` alone, to verify attestations.
- harden-runner runs in audit mode on any job that installs packages or runs third-party code.
- The librarian is split into an `earlier` job whose token can read pull requests and nothing else, a read-only `refresh` job and an agent-free `publish` job. So the write token and the agent never meet. The agent's one credential is the `AGENT_API_KEY` secret or, with `AGENT_USE_JOB_TOKEN`, the job's own token, holding `contents: read` and `copilot-requests: write`. It is exported into the agent's environment only, under a credential-shaped name the wrapper checks (2026-09-24).
- Every secret lives in an Environment limited to the default branch. The librarian's agent key, the sync token and the ingest credentials each belong in the Environment of the one workflow that reads them, `knowledge-librarian`, `knowledge-sync` or `knowledge-ingest`, since a repository secret can be read by a workflow on any branch, and a workflow file runs on a push to the branch that carries it, with a `permissions:` key that can raise its own token. The templates still read a same-named repository secret too, so a host works while it moves them. Every host should move them. A private repository on GitHub Free has no Environments, and its secrets stay readable from any branch there.
- A host's sync runs no code from the release, and the branch it pushes carries no workflow the release wrote. `knowledge-sync.yaml`'s `sync` job reads the release as data, under `contents: read` and with no git credential on disk. Its `publish` job applies only the copies, the pin and the changelog, and holds the release's workflow changes for a person.
- The release workflow is split the same way (2026-09-24). A `pack` job installs the toolkit and validates under `contents: read`. An `attach` job runs no third-party packages, holds `contents: write`, and checks each zip, the bundle's and any Copilot skill's, against the checksum `pack` made before uploading it. The release step, the sidecar's `knowledge-sync.sh` and its `knowledge-sync.yaml` workflow move the skill pin together.
- A domain host's federation build reads the members' releases and never runs them. It fetches only the files the member concepts name, over http or https from a public address. A local path needs `--allow-local`, and a private address needs a person's `private_addresses: allow` on the Domain concept, which a pull request's check does not take as it stands. Each connection to a member checks the address it opens, so a name that answers a public address to the check and a private one to the connection (DNS rebinding) reaches nothing; through a proxy, the proxy resolves the name, and only the check before the request applies (0.56.1). It checks each file against the checksum a person confirmed. For a GitHub release it checks the attestation too, signed by the member's own release workflow, and it stops without `gh`. It refuses a zip holding a symbolic link, a path outside its root, a hidden file such as a `.git` folder, a file a browser runs, or more than a size limit unpacked. It also refuses a distribution name that is not one plain file name. It runs the host's report on each member with git pointed at no repository. A member of a member is confirmed by that member domain, not by the host's person, so it brings content, not code. Its `check` and `build` jobs hold a read token, which reaches `gh` alone. Only `publish` can write, and it checks the workspace zip against the checksum `build` wrote, which catches a fault in the transfer.
- Every write to `main` waits behind the `release` Environment's required reviewers. Those reviewers are configured by hand, or the Environment exists in name only. Release tooling is installed with `npm install --ignore-scripts`.
- `main` blocks deletion, force-pushes and non-linear history, and nothing more, since a stricter ruleset would also reject the release job's commit.
- Secret scanning and push protection are on. They are GitHub settings nothing in CI can assert, so keeping them on is a maintainer responsibility.
- No tracked file holds a character a reader cannot see, which `knowledge-trust-ladder`'s contract checks (2026-10-04).
- CodeQL and dependency review are skipped where there is nothing for them to scan.
- The skill a scheduled run installs is pinned to a commit: the install step installs nothing unless the release tag still names the commit it named when the pin was set.
- Every workflow that installs the lokf toolkit does so with `uv sync --locked`. So each file is checked against the hash `.lokf/uv.lock` records, and a lock that is missing or out of date fails the job.
- The Python halves of the conventions script and the pen name one PyYAML release, and take no file uploaded after a set date.
- Where there is no Python, ktl-librarian and ktl-sidecar read LOKF's schema from GitHub by commit, never by tag, so the file cannot change under them (2026-10-05). The contract in `knowledge-trust-ladder` fails a tag or a branch in that URL, and two pages that pin different commits.

**The sync workflow** keeps a host's sidecar and site copies, and its skill pin, at the newest release, and runs no agent. Its `sync` job clones the release without a checkout and copies only what `knowledge-sync.manifest` names. It refuses a copy path outside the host's tree or inside a `.git` folder, where a copy would be git's own configuration, which can name a command git runs. Its `publish` job runs the default branch's copy of `knowledge-sync.sh --apply`. That refuses a path the manifest does not allow, and a deletion, a rename, a link or an unusual mode. It keeps every workflow as the default branch has it and sets the pin itself.

The branch the sync pushes carries no workflow the release wrote, since a workflow on the pushed branch would run before review, with the repository's secrets and a token it can raise. A person applies the held workflow changes after reading them, or approves them in a review Environment with required reviewers, after which a job pushes them. `KNOWLEDGE_SYNC_TOKEN`, scoped to Contents, Pull requests and Workflows for that repository alone and kept in the `knowledge-sync` Environment, reaches the `publish` and `push-workflows` jobs alone. It lets them push one branch, `knowledge-sync`, and open or edit one pull request, which a person reviews before the pin moves. Its force-push touches only that branch, leased to the commit the `earlier` job read, so a commit added since is never lost. Run by hand, the script copies the workflows too, and runs the sidecar's checks on the synced copies unless given `--no-checks`, so a person who syncs that way runs the release's code on their own machine.

**The website** is built by `knowledge-website.yaml`'s `build` job, which runs npm's packages, the lokf toolkit, `just` and the repository's own code: `site.config.mjs`, the files under `website/`, and the commands that build the schema's pages and the data. It holds a read-only token and no secret. `npm ci --ignore-scripts` runs no package's install script, and Astro's telemetry is off. Its `deploy` job runs harden-runner and GitHub's deploy action, on the default branch alone, once the repository variable is set, in the `github-pages` Environment, which GitHub limits to the default branch. A pull request's build runs that pull request's code, as any check does, and anyone who can read the repository can download its artifact.

The sync copies a file only when it is inside the repository, and follows a link only when the link ends inside it. An SVG that holds a script, an event handler or a `javascript:` address is left out. Raw HTML in the Markdown passes as GitHub renders a README. A tag GitHub allows keeps the attributes it allows, an address that is not http, https, mailto, a path or a fragment is dropped, and anything else is shown as text. A project site shares its origin with every other project site of its owner, so a script on one would run with all of them. A private repository should set harden-runner's egress policy to `block` in the `build` job, with the package registries allowed. `BROWSE` publishes its databases whole, and is off unless `site.config.mjs` turns it on.

**The ingest workflow**, `knowledge-ingest.yaml`, mirrors the sources `.lokf/ingest.yaml` names into `.lokf/mirror/`, and runs no agent. It fetches each address under `contents: read` with no git credential on disk, caps each body and the mirror as a whole, refuses a private or link-local address the manifest does not allow, at each connection as well as before the request, so DNS rebinding cannot reach one, and removes every character a reader cannot see, apart from the joiners that Persian, Arabic and Indic scripts and emoji spell with. Git resolves a `git` entry's name itself, so for it only the check before the fetch applies. A `command` entry runs only a tracked, committed script, with no shell and a clean environment. The job holds only the `KNOWLEDGE_INGEST_` secrets the manifest names, and its `publish` job refuses a patch touching anything but `.lokf/mirror/` and the lock. What it fetches reaches the scheduled librarian only after a person merges the pull request, so the mirror holds the same place as any other repository content, reviewed before the librarian reads it.

**The librarian's pen (added 2026-10-03)**: the librarian writes the bundle only through `knowledge-apply.sh`. ktl-librarian describes each change as an operation in `.lokf/patch.yaml`, and the script stamps `generated`. It refuses an operation that would name a person as its actor. It refuses to rewrite text a person wrote, or to delete a concept a person confirmed or left a note on. It writes nothing unless every operation passes. The pen also compares each concept it is about to write with the file it read. It refuses the patch when a person's event or note would differ, however the operations spelt it.

The scheduled wrapper applies the file after the agent has finished and refuses a run that changed anything else, so the agent never writes the bundle itself. `publish` checks the patched tree for the same refusals with `knowledge-provenance.sh --unattended`. `docs/threat-model.md` lists the pen under repository hardening.

**Human attribution**: a `verified` event whose actor starts with `human:`, or a `generated` record written that way, is a claim, not a credential. It is a string in Markdown that any writer can type. The realistic threat is not an outside attacker but **another agent** driving `ktl-curator` and recording confirmations nobody gave.

`knowledge-registrar.yaml`'s `provenance` job is the authority. It requires an approving review from the named account, or their verified signature on the introducing commit: evidence GitHub holds, rather than evidence the bundle asserts. That job reads the events themselves: whole, from the frontmatter, against every parent of a commit, and keyed by the concept's `id`. So a re-dated event counts, while a rename, a merge and an example in a body code fence do not. Conventions rule 10 keeps those fields to spellings a line reader and a parser agree on.

ktl-curator writes `human:` only for an authenticated identity: `gh api user`, `glab api user`, or a signing key the forge lists under the stated login. Without one, it refuses the two verbs that assert a person vouched for something, while the three that assert nothing about who checked what stay available. It refuses to run a review session unattended, and its report flags an unsigned `human:` commit rather than trusting it silently.

`knowledge-provenance.sh` (2026-09-17) does the signature half where GitHub is not the forge, or as a second opinion where it is. It checks against public keys the repository carries under `.lokf/curators/`, one GPG or SSH key per curator id. It refuses a change that adds an id's key and that id's confirmation together. The optional `attestation` job is off unless `KNOWLEDGE_CURATION_ENVIRONMENT` names an environment, and naming one whose required reviewers are empty makes it self-approve instantly.

Where `.lokf/` is gitignored, no pull request ever carries the bundle, so the CI half never runs and the curator's in-session rules are the whole of it. A host with no git at all has only its platform's version history. None of this proves anyone read the source: it raises the cost of forgery, not the truth of a confirmation.

**Prompt-injection guards**, one per input path, across the six skills that read content they did not author:

- ktl-librarian resolves a `.lokf/feedback.md` entry only from the source it names, never from the entry's own wording, and ktl-curator only counts the waiting entries, with `grep -c`.
- ktl-curator quotes a fetched source to a person rather than acting on it.
- ktl-docent treats fetched or repository content as text to quote, never instructions, and is read-only on the bundle besides. Since 2026-09-23 it adds a feedback entry through `knowledge-feedback.sh` (its own copy since 2026-10-05), rather than by opening `feedback.md`. So the librarian is the only skill that reads what a reader wrote. Its one write path asks once per session first. A Disagreement may name its concept, which must be a concept file in the bundle's lowercase spelling. `knowledge-report.sh` reads that path back to mark the concept disputed, and reads nothing else of the entry.
- ktl-prose never opens `.lokf/feedback.md`, and rewords only in a live session, on a request addressed to it. Its check script refuses a rewording that touches a concept a person wrote or confirmed, or a byte of frontmatter, or that adds a character no reader sees.
- The registrar's `provenance` job, which reads pull-request metadata, runs no agent. Event fields enter through `env:`, API reads are narrowed to logins, SHAs and a verification flag, and the `human:<id>` is held to a login's characters. The token is read-only, and a path git still has to quote is refused (2026-09-19).
- The librarian's `earlier` job, which lists the pull requests the workflow opened, runs no agent either and reads no title, body or comment. It counts a pull request only when its branch is `knowledge-librarian/...` in this repository, and matches each value it takes against a pattern. Only the hashes of the feedback entries those pull requests handled leave the job, since the entries are readers' words.
- A file under `.lokf/mirror/` is a copy of a page or document from outside the repository, written by the ingest and merged by a person before the librarian reads it. The librarian derives from it as from any source: text to derive from, never instructions. So a reviewer of the ingest pull request reads the diff as the source page, and the manifest decides what comes in.

If a guard fails, the only unattended write path is `knowledge-librarian.yaml`'s `publish` job. It re-derives the touched paths from the patch's own `git apply --numstat`, on a clean checkout the agent never shared. It confines them to `.lokf/knowledge`, `knowledge_bundle`, `.lokf/feedback.md` and `.lokf/questions.md`, the only pathspecs the patch is built from. It separately refuses a patch that adds a `by: human:` line. It refuses a patch that touches a person's record: an event added, changed or removed in any YAML layout, a person's note added or removed, or text a person wrote changed.

Inside `refresh`, the wrapper snapshots `.git/config` and `.git/hooks` before the agent call and restores them from an `EXIT` trap. It keeps its own checks in a `main()` called last, so neither a failed agent nor a cancelled job leaves a poisoned config behind.

**A person's record is never removed without that person.** `docs/threat-model.md` says the `provenance` job collects the actor of every `human:` event a pull request adds, changes or removes. A `verified` event struck out, or gone with its concept, needs the same approval or signature as one that is added. A person's `generated` record may be replaced only by another person's.

**The ledger of readers' questions.** A handled feedback entry moves from `feedback.md` to `.lokf/questions.md`, which the pen writes and only programs read. The librarian keeps a reader's words out of `log.md`, out of every concept and out of its hand-off, since the curator opens the first two and a person reads the third. From the ledger, `knowledge-report.sh` builds the one prompt of the retrieval test. An agent answers it from an empty directory, and its reply is read for concept paths only.

**The librarian's hand-off (2026-10-04).** The patch file may carry up to ten lines for the person reviewing the pull request, in the agent's own words. It is the one free text that passes from the job that ran the agent to the pull request. The pen holds each line to printable text with no backtick and writes none of it to the bundle.

Once the agent returns, the wrapper removes whatever is at the paths the workflow reads, so a file or a link the agent left there is gone. The retrieval test calls the agent again, with readers' words in its prompt, after the pen has written the hand-off. So the wrapper writes the pen's lines there again once that call returns. `publish` cleans the lines again and shows them in a code block, where nothing renders, and the curator never opens a pull request body.

**A confirmation covers the text the person saw (2026-10-04).** The label *confirmed by a person* holds while `generated.at` is no later than the confirmation. The pen restamps every change it writes, and conventions rule 13 fails a pull request in which any other writer changes a confirmed concept's content and leaves `generated` as it was. Rule 14 covers the commit that records the confirmation. On a pull request, such a commit may change what the concept says only when the person is also recorded as its author, as *Correct now* records them.

**What this does not cover.** Ordinary repository content the librarian scrapes while building concepts, such as READMEs, docs and code, has no per-entry guard. Nothing here filters what a reader asks `ktl-docent`. Nor does any of this make a repository a sandbox.

**A skills repository.** A skills repository is the case where the content the librarian scrapes is all instructions, since every `SKILL.md` is written for an agent to follow. The same guards hold there. The librarian reads each source as data, writes only `patch.yaml` through the pen, and holds `contents: read` in a scheduled run. An instruction in a source can still shape what a concept says. Only the person reviewing the pull request catches that, since the pen checks a patch's form and never its truth.

## Open questions

- 2026-10-19, human:noelmcloughlin: do a fresh check with sources and ask curator questions on deviations if any exist.
- 2026-10-19, human:noelmcloughlin: needs refresh from sources
