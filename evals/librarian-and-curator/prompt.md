---
name: librarian-and-curator
description: "Question 4 of the docent holdout (tests/docent-holdout.yaml): the answer should rest on playbooks/ktl-librarian-skill.md and playbooks/ktl-curator-skill.md."
tags: [docent, holdout]
runs: 1
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: "ktl-docent answers from the bundle, and the answer names playbooks/ktl-librarian-skill.md and playbooks/ktl-curator-skill.md among the concepts it rests on."
---

Use the ktl-docent skill to answer this question from the `.lokf/knowledge` bundle in the current directory.

How do ktl-librarian and ktl-curator relate?
