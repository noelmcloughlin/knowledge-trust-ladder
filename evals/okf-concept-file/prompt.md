---
name: okf-concept-file
description: "Question 2 of the docent holdout (tests/docent-holdout.yaml): the answer should rest on glossary/okf.md and references/okf-specification.md."
tags: [docent, holdout]
runs: 1
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: "ktl-docent answers from the bundle, and the answer names glossary/okf.md and references/okf-specification.md among the concepts it rests on."
---

Use the ktl-docent skill to answer this question from the `.lokf/knowledge` bundle in the current directory.

What does OKF require of a concept file?
