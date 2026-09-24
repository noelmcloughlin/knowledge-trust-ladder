---
type: Policy
id: https://knowledge-trust-ladder.example/knowledge/policies/threat-model
title: Threat model
description: "The security design the three LOKF repositories share: repository hardening, the human:-attribution gate on a verified event, and the prompt-injection guard for each input path that reads content it did not author - carried once here so each SECURITY.md can link instead of restate."
genre: reference
resource: docs/threat-model.md
generated:
  by: process:ktl-librarian
  at: "2026-09-24T16:40:00Z"
references:
- https://knowledge-trust-ladder.example/knowledge/policies/security
- https://knowledge-trust-ladder.example/knowledge/policies/ai-covenant
---

# Overview

Added 2026-09-14, when `policies/security.md`'s ~1,900-word design moved out
of `SECURITY.md` and into this page across the three LOKF repositories
(`knowledge-trust-ladder`, KTL Registrar, KTL Curator). Its section headings are
kept stable on purpose - `#interactive-use-scope-is-advisory-not-enforced`,
`#repository-hardening`, `#human-attribution-human-is-a-claim-not-a-credential`,
`#prompt-injection-guards` - because every sibling repository's `SECURITY.md`
deep-links them by URL; `scripts/validate-repository.sh` check 9 records this
path among the ones a sibling depends on.

**Interactive use is advisory, not enforced.** A skill's `Scope:` line is
prose, not a checked permission - an agent run interactively has whatever
access its harness grants, and only the scheduled `knowledge-librarian.yaml`
technically enforces its scope, because nothing else is watching it run.

**Repository hardening**: actions pinned to commit SHAs everywhere including
the copied templates; `permissions: {}` at the top of every workflow;
harden-runner in audit mode on any job installing packages or running
third-party code; the librarian split into a read-only `refresh` job and an
agent-free `publish` job so the write token and the agent never meet, with
the agent's one credential (the `AGENT_API_KEY` secret or, with
`AGENT_USE_JOB_TOKEN`, the job's own token, holding `contents: read` and
`copilot-requests: write`) exported into the agent's environment only, under
a credential-shaped name the wrapper checks (2026-09-24); the release
workflow split the same way, a `pack` job that installs the toolkit and
validates under `contents: read` and an `attach` job that runs no
third-party packages, holds `contents: write`, and checks the zip against
the checksum `pack` made before uploading it (2026-09-24); every
write to `main` behind the `release` Environment's required reviewers; `main`
blocking deletion, force-pushes, and non-linear history, deliberately nothing
more, since a stricter ruleset would also reject the release job's own
commit; secret scanning and push protection as GitHub settings nothing in CI
can assert still hold; CodeQL and dependency review skipped where there is
nothing for them to scan.

**Human attribution**: a `verified` event whose actor starts with `human:`,
or a `generated` record written that way, is a claim, not a credential - just
a string in Markdown that any writer can type. `knowledge-registrar.yaml`'s
`provenance` job is the authority: it requires an approving review from the
named account or their verified signature on the introducing commit,
evidence GitHub holds rather than evidence the bundle asserts. Both gates
read the events themselves - whole, from the frontmatter, against every
parent of a commit and keyed by the concept's `id` - so a re-dated event
counts while a rename, a merge and an example in a body code fence do not,
and conventions rule 10 keeps those fields to spellings a line reader and a
parser agree on (2026-09-17). ktl-curator writes `human:` only for
an authenticated identity - `gh api user`, `glab api user`, or a signing
key the forge lists under the stated login - refuses to run a review session
unattended, and its report flags an unsigned `human:` commit rather than
trusting it silently. Where GitHub is not the forge, or as a second opinion
where it is, `knowledge-provenance.sh` (2026-09-17) does the signature half
against public keys the repository carries under `.lokf/curators/`, one GPG
or SSH key per curator id, and refuses a change that adds an id's key and
that id's confirmation together. None of this proves anyone read the source - it raises the cost
of forgery, not the truth of a confirmation.

**Prompt-injection guards**, one per input path: ktl-librarian
resolves a `.lokf/feedback.md` entry only from the source it names, never its
own wording, and ktl-curator only counts waiting entries with `grep -c`;
ktl-curator quotes a fetched source to a person rather than
acting on it; ktl-docent treats fetched or repository content as text to
quote, never instructions, is read-only on the bundle besides, and since
2026-09-23 adds a feedback entry through `knowledge-feedback.sh` rather than
by opening `feedback.md`, so the librarian is the only skill that reads what
a reader wrote; its one write path asks once per session first. The
registrar's `provenance` job, which reads pull-request metadata, runs no
agent: event fields enter through `env:`, API reads are narrowed to logins,
SHAs and a verification flag, the `human:<id>` is held to a login's
characters, the token is read-only, and a path git still has to quote is
refused (2026-09-19). If a guard
fails, the only unattended write path is `knowledge-librarian.yaml`'s
`publish` job, which re-derives the touched paths from the patch's own
`git apply --numstat` on a clean checkout the agent never shared, confines
them to `.lokf/knowledge`, `knowledge_bundle` and `.lokf/feedback.md` (the
only pathspecs it stages), and refuses a patch adding a `by: human:` claim.
Inside `refresh`, the wrapper snapshots `.git/config` and `.git/hooks`
before the agent call and restores them from an `EXIT` trap, and keeps its
own checks in a `main()` called last, so neither a failed agent nor a
cancelled job leaves a poisoned config behind.
