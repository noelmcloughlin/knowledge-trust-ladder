---
type: Policy
id: https://knowledge-trust-ladder.example/knowledge/policies/security
title: "Security policy"
description: "How to report a vulnerability privately, which versions receive fixes, the four things in this repository that execute and what holds each, and what the policy does not cover."
genre: reference
resource: SECURITY.md
sources:
- resource: SECURITY.md
- resource: docs/threat-model.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
references:
  - https://knowledge-trust-ladder.example/knowledge/policies/threat-model
  - https://knowledge-trust-ladder.example/knowledge/policies/versioning
---

# Overview

`SECURITY.md` is a policy, not a threat model. It says how to report, what executes in the repository, and what holds each surface, with a line or two per item that links to where the reasoning lives. The repository contract holds the file to a word budget.

# Reporting a vulnerability

Use GitHub's private vulnerability reporting, not a public issue or a pull request. Say which file is affected and why it is exploitable, and, for a template that gets copied into other repositories, whether the issue is in the template itself or appears only after a consumer customizes it. One person maintains the repository: expect a first reply in days, not hours, and no bounty.

# Supported versions

Only the latest published tag receives fixes, shipped as a patch release and noted in `CHANGELOG.md`. A fix to a template reaches a repository that already has a sidecar only when its copies are laid down again; the preflight reports the drift on its `copies` line, and the sidecar's repair re-copies the files. An automated skill audit, such as Snyk's or Socket's, gets its answer in the file each finding names and in the threat model.

# What executes here

The repository is mostly Markdown. Four things in it run, or are run by other systems, and are the attack surface:

- The sidecar's templates, six scripts and three workflows copied into other repositories, held by their own design: two jobs so the agent never meets a write token, a `publish` job that confines the patch to the bundle and refuses a `human:` claim, and a preflight and a forge-free gate that only read git and gpg.
- This repository's own workflows, held by actions pinned to commit SHAs, `permissions: {}` at the top of every workflow, and harden-runner in audit mode.
- `skills/ktl-prose/scripts/prose-check.py`, the one script a skill runs in place: standard library only, it reads the files it is given and calls `git show` with an argument list, writes nothing and opens no network connection.
- The five skills' prose, executed by whichever LLM agent runs it, held by each skill's guardrail for its own input path: content the agent did not author is quoted, never followed, and only an authenticated person's verdict is recorded as one.

A skill's `Scope:` line is prose, not a permission. Run interactively, an agent has whatever access the harness grants it, so review what it changed before you commit.

# Not covered

A compromised runner, upstream action or agent harness. Whether a bundle is true: the gate proves who vouched, not what they read. A reader's own words to `ktl-docent`, which belong to the agent harness.
