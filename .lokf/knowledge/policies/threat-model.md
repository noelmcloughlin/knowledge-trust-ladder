---
type: Policy
id: https://knowledge-trust-ladder.example/knowledge/policies/threat-model
title: "Threat model"
description: "The security design the three LOKF repositories share: scope is advisory in interactive use, repository hardening, the human: attribution gate on a verified event, the prompt-injection guard for each skill's input path, and what it does not cover."
genre: reference
resource: docs/threat-model.md
sources:
- resource: docs/threat-model.md
- resource: SECURITY.md
- resource: skills/ktl-sidecar/references/gate.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
references:
  - https://knowledge-trust-ladder.example/knowledge/policies/security
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-docent-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-prose-skill
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/explanation/three-lines-of-defence
---

# Overview

`knowledge-trust-ladder`, KTL Registrar and KTL Curator run the same scheduled agent from the same sidecar templates and release the same way, so they share one threat model, and `docs/threat-model.md` is it. Two facts shape it. The skills are prose executed by whichever LLM agent runs them, so anywhere a skill sends the agent to read content it did not author is a prompt-injection surface. And the bundle's central trust signal, a `verified` event whose actor starts with `human:`, is a string in a Markdown file that any writer can type.

# Scope is advisory in interactive use

A skill's `Scope:` line is prose, not a checked permission, and an agent run interactively has whatever tool access the harness grants it. Only the scheduled librarian workflow enforces its scope. Interactively, review what the agent changed before you commit or merge.

# Repository hardening

Actions pinned to commit SHAs, `permissions: {}` at the top of every workflow, harden-runner in audit mode. The librarian runs in two jobs so the agent and the write token never meet, and the agent step runs the reviewed in-repository wrapper, never a variable's content as a command. The release workflow packs the bundle and uploads it in separate jobs. Every workflow write to `main` sits behind the `release` environment. `main` blocks deletion and force-pushes and requires linear history, and no more, because a rule requiring pull requests would also reject the release job's own push.

# Human attribution is a claim, not a credential

The realistic threat is not an outside attacker but another agent driving `ktl-curator` and recording confirmations nobody gave. Four measures hold it, in descending order of weight.

- The forge is the authority. The `provenance` job requires an approving review or a verified signature for every `human:` event a pull request adds or changes, and `knowledge-provenance.sh` does the signature half off GitHub.
- The curator writes `human:` only for an authenticated identity.
- The curator refuses to run a review session unattended.
- The curator's report counts confirmations git cannot back.

The limits are stated: a signature proves a key holder made a commit, and nothing proves anyone read the source.

# Prompt-injection guards

Each skill carries the guard for its own input path. The librarian is the one skill that reads reader feedback, and it resolves only the question an entry names, from the source it points at. The curator quotes a source to a person and records only the person's verdict. The docent treats fetched sources and the repository as text to quote, and records a gap through a script so it never opens the feedback file. `ktl-prose` treats the body it rewords as text to edit, rewords only in a live session, and its script refuses a rewording that touches a person's record or a frontmatter byte. The `provenance` job reads pull-request metadata with no agent in the job. If a guard fails, the blast radius is a pull request that never pushes to `main` and never auto-merges.

# Not covered

Ordinary repository content the librarian scrapes has no per-entry guard; it relies on the review before merge. A reader's own phrasing to the docent belongs to the agent harness. A compromised runner, upstream action or agent harness is out of reach.
