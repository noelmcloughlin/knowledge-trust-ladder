---
type: Policy
id: https://lokf-agent-skills.example/knowledge/policies/threat-model
title: Threat model
description: "The security design the three LOKF repositories share: repository hardening, the human:-attribution gate on a verified event, and the prompt-injection guard for each skill's own input path - carried once here so each SECURITY.md can link instead of restate."
genre: reference
resource: docs/threat-model.md
generated:
  by: process:lokf-librarian
  at: "2026-09-14T23:10:00Z"
references:
- https://lokf-agent-skills.example/knowledge/policies/security
- https://lokf-agent-skills.example/knowledge/policies/ai-covenant
verified:
- by: process:lokf-librarian
  at: "2026-09-14T23:10:00Z"
---

# Overview

Added 2026-09-14, when `policies/security.md`'s ~1,900-word design moved out
of `SECURITY.md` and into this page across the three LOKF repositories
(`lokf-agent-skills`, LOKF Registrar, LOKF Curator). Its section headings are
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
agent-free `publish` job so the write token and the agent never meet; every
write to `main` behind the `release` Environment's required reviewers; `main`
blocking deletion, force-pushes, and non-linear history, deliberately nothing
more, since a stricter ruleset would also reject the release job's own
commit; secret scanning and push protection as GitHub settings nothing in CI
can assert still hold; CodeQL and dependency review skipped where there is
nothing for them to scan.

**Human attribution**: a `verified` event whose actor starts with `human:` is
a claim, not a credential - just a string in Markdown that any writer can
type. `knowledge-registrar.yaml`'s `provenance` job is the authority: it
requires an approving review from the named account or their verified
signature on the introducing commit, evidence GitHub holds rather than
evidence the bundle asserts. lokf-curator writes `human:` only for
`gh api user`'s authenticated identity, refuses to run a review session
unattended, and its report flags an unsigned `human:` commit rather than
trusting it silently. None of this proves anyone read the source - it raises
the cost of forgery, not the truth of a confirmation.

**Prompt-injection guards**, one per skill's input path: lokf-librarian
resolves a `.lokf/feedback.md` entry only from the source it names, never its
own wording; lokf-curator quotes a fetched source to a person rather than
acting on it; lokf-docent treats fetched or repository content as text to
quote, never instructions, and is read-only on the bundle besides. If a guard
fails, the only unattended write path is `knowledge-librarian.yaml`'s
`publish` job, which re-derives the touched paths from the patch's own
`git apply --numstat` on a clean checkout the agent never shared, confines
them to the bundle, and refuses a patch adding a `by: human:` claim.
