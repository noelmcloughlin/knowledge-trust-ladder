---
type: Policy
id: https://knowledge-trust-ladder.example/knowledge/policies/ai-covenant
title: AI covenant
description: Community norms for AI use - contributors own what they submit regardless of tooling, AI must not post autonomously in discussions, AI co-authorship in commit messages is discouraged, and a repository-owned agent (e.g. ktl-librarian) must commit under a bot or maintainer identity with no trailer either way and land only as a human-reviewed PR.
genre: reference
resource: AI_COVENANT.md
generated:
  by: process:ktl-librarian
  at: "2026-09-09T18:00:00Z"
verified:
- by: process:ktl-librarian
  at: "2026-09-17T14:02:11Z"
- by: human:noelmcloughlin
  at: "2026-09-10T00:00:00Z"
stale_after: 2027-09-10
---

# Overview

The core principle is ownership: everything submitted is the contributor's,
whatever tools helped create it, and they must be able to understand, verify,
and defend it. AI review comments are suggestions, not requirements.

Discussions are for human judgement - AI must not directly post comments in
issues, Slack, or mailing lists. Disclosure is required when proposing changes
to code the contributor does not fully understand, and AI co-authorship
trailers in commit messages are actively discouraged. Adapted from the LinkML
AI Covenant.

A dedicated **Repository-Owned Agent Automation** section covers the case
this repository actually runs into: an agent (`ktl-librarian`, scheduled or
interactive) proposing changes with nobody drafting alongside it. It commits
as a labeled bot identity or the invoking maintainer - never both, and never
with an AI co-authorship trailer either way; every such change lands as a PR
requiring human approval, never a direct push or an agent's own approval;
and a skill recording a person's verdict (`ktl-curator`'s `verified:
human:<id>`) may write only what that person said about that specific item,
never inferred or self-supplied.
