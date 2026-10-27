---
name: security-contact
description: "Question 8 of the docent holdout (tests/docent-holdout.yaml): the answer should rest on policies/security.md."
tags: [docent, holdout]
runs: 1
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: "ktl-docent answers from the bundle, and the answer names policies/security.md among the concepts it rests on."
---

Use the ktl-docent skill to answer this question from the `.lokf/knowledge` bundle in the current directory.

Who do I contact to report a security issue, and is that policy confirmed by a person?
