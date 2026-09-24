---
type: Policy
id: https://knowledge-trust-ladder.example/knowledge/policies/security
title: Security policy
description: How to report a vulnerability privately, supported versions, and a surface table (what executes here, what holds it) that links to the shared threat model instead of restating it.
genre: reference
resource: SECURITY.md
sources:
- resource: SECURITY.md
- resource: scripts/validate-repository.sh
- resource: CHANGELOG.md
generated:
  by: process:ktl-librarian
  at: "2026-09-24T01:00:00Z"
status: draft
references:
- https://knowledge-trust-ladder.example/knowledge/policies/threat-model
- https://knowledge-trust-ladder.example/knowledge/playbooks/repository-validation
verified:
- by: human:noelmcloughlin
  at: "2026-09-10T00:00:00Z"
stale_after: 2027-03-10
---

# Overview

Rewritten 2026-09-14 from a single file of up to ~1,900 words into a short policy plus
[the shared threat model](threat-model.md): report a vulnerability through
GitHub's private vulnerability reporting, never a public issue or PR, naming
the affected file and whether a template issue is in the template itself or
appears only after a consumer customizes it - one maintainer, so expect a
reply in days, not hours, no bounty. Only the latest published tag receives
fixes, as a patch release noted in `CHANGELOG.md`. A template fix reaches a
repository that already has a sidecar only when its copies are laid down
again - updating the skill or moving `TRUST_LADDER_SKILLS_REF` does not
touch them - so `knowledge-preflight.sh` reports the drift on its `copies`
line and ktl-sidecar's repair re-copies the files. A finding from an
automated skill audit (Snyk, Socket) is answered in the file it names and in
the threat model's prompt-injection section.

A surface table names what executes and what holds it, each cell a line or
two linking out rather than explaining: the sidecar templates copied into
other repositories, held by the librarian workflow's two-job design, the
`publish` job's confinement and `human:` refusal, the preflight and the
forge-free gate; this repository's
workflows, held by pinned actions, `permissions: {}`, and harden-runner; and
the four skills' prose, executed by whichever agent runs it, held by each
skill's own guardrail for its input path. A skill's `Scope:` line is prose,
not a permission - only the scheduled workflow enforces its scope, so an
interactive session's guard is a person reviewing what the agent changed.

Not covered: a compromised runner, upstream action, or agent harness (a
baseline, not a sandbox - report a finding there anyway); whether a bundle is
*true*, which `AI_COVENANT.md` addresses; and a reader's own words to
ktl-docent, a boundary the agent harness owns, not a Markdown file.

A word budget (check 10, 900 words) holds this file to a policy's shape; the
design that used to live here now lives once in the linked threat model.
