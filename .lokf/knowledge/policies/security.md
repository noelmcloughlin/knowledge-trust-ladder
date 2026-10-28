---
type: Policy
id: https://w3id.org/ktl/knowledge/policies/security
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
  at: "2026-10-28T00:35:16Z"
references:
  - https://w3id.org/ktl/knowledge/policies/threat-model
  - https://w3id.org/ktl/knowledge/playbooks/repository-validation
verified:
  - by: human:noelmcloughlin
    at: "2026-09-10T00:00:00Z"
  - by: human:noelmcloughlin
    at: "2026-09-26T20:21:41Z"
  - by: process:ktl-librarian
    at: "2026-10-27T01:03:06Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T00:41:54Z"
  - by: human:noelmcloughlin
    at: "2026-10-19T22:35:12Z"
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

The repository is mostly Markdown. Five things in it run, or are run by other systems, and they are the attack surface:

| Surface | What guards it |
| --- | --- |
| `skills/ktl-sidecar/templates/`: fourteen scripts and six workflows that the sidecar copies into other repositories, where they run | The template's own design. Separate jobs mean the agent never meets a write token. A `publish` job confines the patch to the bundle and refuses a `human:` claim. A preflight and a forge-free gate only read git and gpg. Each workflow reads its secrets from an Environment limited to the default branch. A domain host's federation build runs nothing a member's zip holds, and refuses a hidden file or a path-like name in one. A host's sync runs no code from the release, and the branch it pushes carries no workflow the release wrote, since those wait for a person. |
| `.github/workflows/`: `validate.yml` on every pull request; `knowledge-registrar.yaml`, `knowledge-librarian.yaml`, `knowledge-release.yaml` and `knowledge-website.yaml`, this repository's own copies of the templates; `semantic-release.yml` and `publish.yml`, which write to `main` behind the `release` Environment; `docent-eval.yml`, which runs an agent weekly under the `docent-eval` Environment with a read-only token | Actions pinned to commit SHAs, `permissions: {}` at the top of every workflow, and harden-runner in audit mode. Each workflow's header comment says why it is shaped as it is. |
| `skills/ktl-prose/scripts/prose-check.py` and `skills/ktl-docent/scripts/`: the scripts a skill runs in place, in whichever repository installs it | `prose-check.py` uses the standard library only. It reads the files it is given and the skill's own word list, calls `git show` with an argument list, and writes nothing. The docent's two are byte-identical copies of the sidecar's templates: `knowledge-report.sh` reads the bundle and git, and `knowledge-feedback.sh` writes one line to `.lokf/feedback.md`. None opens a network connection. |
| `skills/ktl-website/templates/`: the site's build scripts and one workflow that the website skill copies into other repositories, where they run, and `scripts/website-preflight.sh`, run in place | The workflow's `build` job runs npm's packages without their install scripts, the lokf toolkit, `just`, and the repository's own site code and build commands, under a read-only token with no secret. Its `deploy` job runs harden-runner and GitHub's deploy action, and only once a repository variable is set. The sync copies only files inside the repository and passes raw HTML as GitHub renders it. The preflight writes nothing, and runs the sidecar's preflight and report. |
| The six skills' `SKILL.md` and `references/` prose, executed by whichever LLM agent runs it, here and in every consumer | Each skill's guardrail for its own input path: content the agent did not author is quoted, never followed, and only an authenticated person's verdict is recorded as one. |

Each row in `SECURITY.md` links to the section of the threat model that holds its reasoning. The sidecar's templates link to the prompt-injection guards and the sync workflow, the workflows to repository hardening and the docent eval, the website's templates to the website, and the skills' prose to the prompt-injection guards and human attribution.

A skill's `Scope:` line is prose, not a permission. Run interactively, an agent has whatever access the harness grants it, and only the scheduled workflow enforces its scope. So review what the agent changed before you commit. Five skills also run the scripts in the repository's `.lokf/scripts/`: ktl-curator, ktl-librarian, ktl-prose, ktl-sidecar and ktl-website. ktl-website runs the site's code under `website/` too. Anyone who can commit to the repository can change that code. ktl-docent runs only its own scripts, so a question runs none of the repository's code.

# Not covered

- A compromised runner, upstream action or agent harness: the policy is a baseline, not a sandbox. A finding in one is still reported, with scope and reproduction.
- Whether a bundle is *true*. The gate proves who vouched, not what they read, and `AI_COVENANT.md` sets the human-accountability rules.
- A proxy's own egress. The threat model says why a proxy must refuse a private address itself.
- A reader's own words to ktl-docent. That boundary belongs to the agent harness, not to a Markdown file.

Check 10 of `scripts/validate-repository.sh` fails when `SECURITY.md` outgrows a word budget of 900. Its comment says the file sits between 450 and 800 words, and was 1,400 to 1,900 before `docs/threat-model.md` took the design.
