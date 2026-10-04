---
type: Policy
id: https://knowledge-trust-ladder.example/knowledge/policies/security
title: Security policy
description: How to report a vulnerability privately, supported versions, and a surface table (what executes here, what guards it) that links to the shared threat model instead of restating it.
genre: reference
resource: SECURITY.md
sources:
- resource: SECURITY.md
- resource: scripts/validate-repository.sh
- resource: CHANGELOG.md
generated:
  by: process:ktl-librarian
  at: "2026-10-04T17:27:49Z"
references:
- https://knowledge-trust-ladder.example/knowledge/policies/threat-model
- https://knowledge-trust-ladder.example/knowledge/playbooks/repository-validation
verified:
- by: human:noelmcloughlin
  at: "2026-09-10T00:00:00Z"
- by: human:noelmcloughlin
  at: "2026-09-26T20:21:41Z"
- by: process:ktl-librarian
  at: "2026-10-04T16:34:14Z"
stale_after: 2027-03-26
status: draft
---

# Overview

`SECURITY.md` is a policy, not a threat model. It says how to report, what executes here, and what guards each surface, in a line or two that links to where the reasoning lives: a workflow header, a skill's own guardrail, or [the shared threat model](threat-model.md). It took that shape in 0.17.1 (2026-09-14, `CHANGELOG.md`), when the design moved to `docs/threat-model.md`.

# Reporting a vulnerability

Report through GitHub's private vulnerability reporting, not a public issue or a pull request. Say which file is affected and why it is exploitable. For a template that gets copied into other repositories, say whether the issue is in the template itself or appears only after a consumer customizes it. One person maintains the repository, so expect a first reply in days, not hours, and no bounty.

# Supported versions

Only the latest published tag receives fixes. A security fix is published as a patch release and is noted in `CHANGELOG.md`.

A fix to a template reaches a repository that already has a sidecar only when ktl-sidecar copies the templates there again. Updating the skill, or moving `TRUST_LADDER_SKILLS_REF`, does not touch them. `knowledge-preflight.sh` reports the drift on its `copies` line, and ktl-sidecar's repair re-copies the files.

An automated skill audit, such as Snyk's or Socket's on a skills catalog, gets its answer in the file each finding names and in the threat model's prompt-injection section. A finding that looks unanswered is reported the same way as any other.

# What executes here

The repository is mostly Markdown. Four things in it run, or are run by other systems, and they are the attack surface:

| Surface | What guards it |
| --- | --- |
| the sidecar templates under `skills/ktl-sidecar/templates/`, which the sidecar copies into other repositories, where they run | the template's own design: two jobs, so the agent never meets a write token; a `publish` job that confines the patch to the bundle and refuses a `human:` claim; a preflight and a forge-free gate that only read git and gpg |
| this repository's workflows: `validate.yml` on every pull request; its own copies of the three knowledge workflows; `semantic-release.yml` and `publish.yml`, which write to `main` behind the `release` Environment | actions pinned to commit SHAs, `permissions: {}` at the top of every workflow, and harden-runner in audit mode; each workflow's header comment says why it is shaped as it is |
| `skills/ktl-prose/scripts/prose-check.py`, the one script a skill runs in place, in whichever repository installs it | the standard library only; it reads the files it is given, calls `git show` with an argument list, writes nothing and opens no network connection |
| the five skills' `SKILL.md` and `references/` prose, executed by whichever LLM agent runs it, here and in every consumer | each skill's guardrail for its own input path: content the agent did not author is quoted, never followed, and only an authenticated person's verdict is recorded as one |

A skill's `Scope:` line is prose, not a permission. Run interactively, an agent has whatever access the harness grants it, and only the scheduled workflow enforces its scope. So review what the agent changed before you commit.

# Not covered

- A compromised runner, upstream action or agent harness: the policy is a baseline, not a sandbox. A finding there is still reported, with scope and reproduction.
- Whether a bundle is *true*. The gate proves who vouched, not what they read, and `AI_COVENANT.md` sets the human-accountability rules.
- A reader's own words to ktl-docent. That boundary belongs to the agent harness, not to a Markdown file.

Check 10 of `scripts/validate-repository.sh` fails when `SECURITY.md` outgrows a word budget of 900. Its comment says the file sits between 450 and 800 words and ran to 1,400 to 1,900 before `docs/threat-model.md` took the design.

## Open questions

- 2026-10-03, human:noelmcloughlin: ensrure this concept is check against source again
