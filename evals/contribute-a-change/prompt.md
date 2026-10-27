---
name: contribute-a-change
description: "Question 5 of the docent holdout (tests/docent-holdout.yaml): the answer should rest on playbooks/contributing.md."
tags: [docent, holdout]
runs: 1
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: "ktl-docent answers from the bundle, and the answer names playbooks/contributing.md among the concepts it rests on."
---

Use the ktl-docent skill to answer this question from the `.lokf/knowledge` bundle in the current directory.

How do I contribute a change to these skills?
