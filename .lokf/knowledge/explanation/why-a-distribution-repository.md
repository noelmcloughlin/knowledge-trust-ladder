---
type: Explanation
id: https://lokf-agent-skills.example/knowledge/explanation/why-a-distribution-repository
title: Why the skills live in their own repository
description: Why the four skills are published from a dedicated, installable repository rather than copied into each project that uses them.
genre: explanation
resource: README.md
generated:
  by: process:lokf-librarian
  at: "2026-09-09T10:00:00Z"
status: draft
references:
  - https://lokf-agent-skills.example/knowledge/references/gh-skill-cli
  - https://lokf-agent-skills.example/knowledge/references/open-skills-cli
verified:
- by: process:lokf-librarian
  at: "2026-09-16T09:10:00Z"
---

# Overview

The skills began embedded in a project that used them, which meant every other
repository wanting them had to copy directories by hand - and copies drift.
A dedicated repository makes them installable (`gh skill install`,
`npx skills add`), pinnable to a release, and reviewable in one place with a
single changelog.

This repository is the sole canonical source. Other projects, including the one
the skills originated in, consume the published release like any other user
rather than maintaining a parallel copy - which is also why this bundle exists:
the repository dogfoods its own skills on itself.
