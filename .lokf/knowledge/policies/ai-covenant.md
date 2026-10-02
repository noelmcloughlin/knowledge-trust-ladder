---
type: Policy
id: https://knowledge-trust-ladder.example/knowledge/policies/ai-covenant
title: "AI covenant"
description: "Community norms for AI use: contributors own what they submit regardless of tooling, AI must not post autonomously in discussions, AI co-authorship in commit messages is discouraged, and repository-owned agents land every change as a reviewed pull request."
genre: reference
resource: AI_COVENANT.md
sources:
- resource: AI_COVENANT.md
- resource: CONTRIBUTING.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
references:
  - https://knowledge-trust-ladder.example/knowledge/policies/code-of-conduct
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
---

# Overview

`AI_COVENANT.md` establishes community norms for responsible AI use in the project, and applies to this repository and the two Obsidian plugin repositories. It is adapted from the LinkML AI Covenant. Its core principle: everything you contribute is yours, regardless of what tools helped create it. When you submit code, documentation, issues or comments with AI assistance, you are the author, responsible for understanding it, verifying it, defending it in review, and ensuring it meets project standards.

# Reviews and discussions

AI review tools provide automated quality checks, not human reviews. Their comments are suggestions, a pull request owner may close them without response, and a pull request still requires human approval. AI tools may help a person think before taking part in a discussion, but AI systems must not be used to post comments, replies or messages directly in issues, discussions, chat channels or mailing lists. Every discussion contribution reflects a human position the author is prepared to explain, revise and defend.

# Repository-owned agent automation

Some of what runs here is a scheduled or on-demand agent, such as `ktl-librarian`, that proposes changes on its own initiative. The core principle still applies. Such an agent commits as either a clearly labeled bot identity or the maintainer who invoked it, never both, and carries no AI co-authorship trailer. Every change it proposes lands as a pull request and requires a human maintainer's approval; an agent's own review does not satisfy that. It runs with least privilege, in a read-only job that hands its change to a separate privileged job, and the contract that it edits only `.lokf/knowledge/` is checked after it runs. A skill that records a person's judgment, such as `ktl-curator` writing a `human:` event, may write only what that person said about that item, in that session. An agent's output is nobody's contribution until a human has reviewed and approved it.

# Disclosure

Required: attribute the idea to AI when proposing a fix to code you do not fully understand. Appreciated: say which ideas are AI-generated and which are your own when brainstorming. Not required: routine use of AI for writing code, issues or pull request descriptions, and AI co-authorship in commit messages, which is actively discouraged.
