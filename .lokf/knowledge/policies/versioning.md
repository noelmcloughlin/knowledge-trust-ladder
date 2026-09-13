---
type: Policy
id: https://lokf-agent-skills.example/knowledge/policies/versioning
title: Versioning policy
description: One repository-level semantic version covering all four skills, released together under a single tag, with patch/minor/major defined by effect on expected behaviour.
genre: reference
resource: CONTRIBUTING.md
generated:
  by: process:lokf-librarian
  at: "2026-09-13T19:00:00Z"
about:
  - https://lokf-agent-skills.example/knowledge/playbooks/releasing
verified:
- by: process:lokf-librarian
  at: "2026-09-13T19:00:00Z"
- by: human:noelmcloughlin
  at: "2026-09-10T00:00:00Z"
stale_after: 2027-09-10
---

# Overview

`vMAJOR.MINOR.PATCH`. Patch is a correction that does not materially change
expected behaviour; minor is a backward-compatible addition or a broader
supported workflow; major is a breaking change to behaviour, structure,
assumptions, or interoperability.

All four skills ship from one tag rather than versioning independently,
because they are designed as a set - the librarian hands off to the curator,
the docent records feedback the librarian consumes - and a consumer pinning
them to different releases could pair skills that disagree about the
frontmatter contract between them.

One asymmetry to know (recorded 2026-09-13): tags carry a `v` prefix
(`v0.16.0`), and `publish.yml` refuses a version typed without it, while
`CHANGELOG.md` headings never do (`## [0.16.0]`); the workflow's cross-check
strips the `v` before comparing the two.
