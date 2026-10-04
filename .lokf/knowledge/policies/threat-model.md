---
type: Policy
id: https://knowledge-trust-ladder.example/knowledge/policies/threat-model
title: Threat model
description: "The security design the three KTL repositories share: repository hardening, the human:-attribution gate on a verified event, and the prompt-injection guard for each input path that reads content it did not author - carried once here so each SECURITY.md can link instead of restate."
genre: reference
resource: docs/threat-model.md
generated:
  by: process:ktl-librarian
  at: "2026-10-04T14:21:43Z"
verified:
- by: process:ktl-librarian
  at: "2026-09-24T22:22:58Z"
references:
- https://knowledge-trust-ladder.example/knowledge/policies/security
- https://knowledge-trust-ladder.example/knowledge/policies/ai-covenant
sources:
- resource: docs/threat-model.md
- resource: CHANGELOG.md
---
# Overview

Added 2026-09-14, when the design moved out of `SECURITY.md` and into this
page across the three KTL repositories (`knowledge-trust-ladder`, KTL
Registrar, KTL Curator). Each repository's `SECURITY.md` says how to report,
what that repository owns, and what it inherits from here, and
`scripts/validate-repository.sh` check 9 records this path among the ones a
sibling depends on.

**Interactive use is advisory, not enforced.** A skill's `Scope:` line is
prose, not a checked permission - an agent run interactively has whatever
access its harness grants, and only the scheduled `knowledge-librarian.yaml`
technically enforces its scope, because nothing else is watching it run.

**Repository hardening**: actions pinned to commit SHAs everywhere including
the copied templates, Dependabot bumping the workflow pins and the templates
bumped by hand, since Dependabot scans only `.github/workflows/`;
`permissions: {}` at the top of every workflow; the agent step running the
reviewed, in-repo wrapper, never a repository variable's content as a
command, with `AGENT_CLI` choosing the agent, `KNOWLEDGE_LIBRARIAN_ENABLED`
arming it, and the workflow triggering only on `schedule` and
`workflow_dispatch`;
harden-runner in audit mode on any job installing packages or running
third-party code; the librarian split into a read-only `refresh` job and an
agent-free `publish` job so the write token and the agent never meet, with
the agent's one credential (the `AGENT_API_KEY` secret or, with
`AGENT_USE_JOB_TOKEN`, the job's own token, holding `contents: read` and
`copilot-requests: write`) exported into the agent's environment only, under
a credential-shaped name the wrapper checks (2026-09-24); the release
workflow split the same way, a `pack` job that installs the toolkit and
validates under `contents: read` and an `attach` job that runs no
third-party packages, holds `contents: write`, and checks each zip, the bundle's and any Copilot skill's, against
the checksum `pack` made before uploading it (2026-09-24); every
write to `main` behind the `release` Environment's required reviewers, which
are configured by hand or the gate exists in name only, with release tooling
installed with `npm install --ignore-scripts`; `main`
blocking deletion, force-pushes, and non-linear history, deliberately nothing
more, since a stricter ruleset would also reject the release job's own
commit; secret scanning and push protection as GitHub settings nothing in CI
can assert still hold; CodeQL and dependency review skipped where there is
nothing for them to scan.

**The librarian's pen (added 2026-10-02)**: `knowledge-apply.sh` is the only writer of `.lokf/knowledge/`. ktl-librarian describes each change as an operation in `.lokf/patch.yaml`, and the script stamps `generated`, refuses an operation that would name a person as its actor, refuses to rewrite text a person wrote or to delete a concept a person confirmed or left a note on, and writes nothing unless every operation passes. The scheduled wrapper applies the file after the agent has finished and refuses a run that changed anything else, so the agent never writes the bundle itself. `publish` reads the same refusals off the patched tree with `knowledge-provenance.sh --unattended`; `docs/threat-model.md` lists it under repository hardening.

**Human attribution**: a `verified` event whose actor starts with `human:`,
or a `generated` record written that way, is a claim, not a credential - just
a string in Markdown that any writer can type. `knowledge-registrar.yaml`'s
`provenance` job is the authority: it requires an approving review from the
named account or their verified signature on the introducing commit,
evidence GitHub holds rather than evidence the bundle asserts. That job
reads the events themselves - whole, from the frontmatter, against every
parent of a commit and keyed by the concept's `id` - so a re-dated event
counts while a rename, a merge and an example in a body code fence do not,
and conventions rule 10 keeps those fields to spellings a line reader and a
parser agree on. ktl-curator writes `human:` only for
an authenticated identity - `gh api user`, `glab api user`, or a signing
key the forge lists under the stated login - and without one refuses the
two verbs that assert a person vouched for something while the three that
assert nothing about who checked what stay available; it refuses to run a
review session unattended, and its report flags an unsigned `human:` commit
rather than trusting it silently. Where GitHub is not the forge, or as a second opinion
where it is, `knowledge-provenance.sh` (2026-09-17) does the signature half
against public keys the repository carries under `.lokf/curators/`, one GPG
or SSH key per curator id, and refuses a change that adds an id's key and
that id's confirmation together. The optional `attestation` job is off
unless `KNOWLEDGE_CURATION_ENVIRONMENT` names an environment, and naming one
whose required reviewers are empty makes it self-approve instantly. Where
`.lokf/` is gitignored no pull request ever carries the bundle, so the CI
half never runs and the curator's in-session rules are the whole of it, and
a host with no git at all has only its platform's version history. None of
this proves anyone read the source - it raises the cost of forgery, not the
truth of a confirmation.

**Prompt-injection guards**, one per input path: ktl-librarian
resolves a `.lokf/feedback.md` entry only from the source it names, never its
own wording, and ktl-curator only counts waiting entries with `grep -c`;
ktl-curator quotes a fetched source to a person rather than
acting on it; ktl-docent treats fetched or repository content as text to
quote, never instructions, is read-only on the bundle besides, and since
2026-09-23 adds a feedback entry through `knowledge-feedback.sh` rather than
by opening `feedback.md`, so the librarian is the only skill that reads what
a reader wrote; its one write path asks once per session first; and
ktl-prose never opens `.lokf/feedback.md`, rewords only in a live session on
a request addressed to it, and its check script refuses a rewording that
touches a concept a person wrote or confirmed, or a byte of frontmatter. The
registrar's `provenance` job, which reads pull-request metadata, runs no
agent: event fields enter through `env:`, API reads are narrowed to logins,
SHAs and a verification flag, the `human:<id>` is held to a login's
characters, the token is read-only, and a path git still has to quote is
refused (2026-09-19). If a guard
fails, the only unattended write path is `knowledge-librarian.yaml`'s
`publish` job, which re-derives the touched paths from the patch's own
`git apply --numstat` on a clean checkout the agent never shared, confines
them to `.lokf/knowledge`, `knowledge_bundle`, `.lokf/feedback.md` and `.lokf/questions.md` (the
only pathspecs the patch is built from), and refuses a patch that touches a person's record: an event added, changed or removed in any YAML layout, a person's note added or removed, or text a person wrote changed.
Inside `refresh`, the wrapper snapshots `.git/config` and `.git/hooks`
before the agent call and restores them from an `EXIT` trap, and keeps its
own checks in a `main()` called last, so neither a failed agent nor a
cancelled job leaves a poisoned config behind.

**A person's record is never removed without that person.** `docs/threat-model.md` has the `provenance` job collect the actor of every `human:` event a pull request adds, changes or removes. A `verified` event struck out, or gone with its concept, needs the same approval or signature as one that is added, and a person's `generated` record may give way only to another person's.

**The ledger of readers' questions.** A handled feedback entry leaves `feedback.md` for `.lokf/questions.md`, which the pen writes and only programs read. The librarian keeps a reader's words out of `log.md` and out of every concept, since the curator opens both. `knowledge-report.sh` builds from the ledger the one prompt of the retrieval test, which an agent answers from an empty directory and whose reply is read for concept paths only.
