---
type: Policy
id: https://knowledge-trust-ladder.example/knowledge/policies/versioning
title: Versioning policy
description: One repository-level semantic version covering all five skills, released together under a single tag, with patch, minor and major decided by Conventional Commits.
genre: reference
resource: docs/releasing.md
sources:
- resource: docs/releasing.md
- resource: README.md
- resource: CONTRIBUTING.md
- resource: CHANGELOG.md
- resource: .github/workflows/publish.yml
generated:
  by: process:ktl-librarian
  at: "2026-10-12T16:12:27Z"
about: []
verified:
- by: process:ktl-librarian
  at: "2026-10-12T23:54:05Z"
- by: human:noelmcloughlin
  at: "2026-09-10T00:00:00Z"
- by: human:noelmcloughlin
  at: "2026-09-26T20:08:48Z"
- by: human:noelmcloughlin
  at: "2026-10-03T09:44:34Z"
stale_after: 2027-10-03
status: draft
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/playbooks/releasing
---

# Overview

`vMAJOR.MINOR.PATCH`. Since 0.15.0 (2026-09-12, `CHANGELOG.md`) the bump is
computed from [Conventional Commits](https://www.conventionalcommits.org/)
and nobody picks a version number: `feat:` is minor; `fix:` and `security:`
are patch; a `BREAKING CHANGE:` footer or `!` after the type is major;
`docs:`, `chore:`, `refactor:`, `style:`, `test:` and `ci:` release nothing -
the change merges and its changelog entries ship with the next release that
does.

All five skills ship together under one tag rather than versioning
independently, so a set pinned to one tag agrees with itself (`README.md`).

One asymmetry to know: tags carry a `v` prefix (`v0.16.0`), and `publish.yml`
refuses a version typed without it, while `CHANGELOG.md` headings never do
(`## [0.16.0]`); the workflow's cross-check strips the `v` before comparing
the two.

## Open questions

- 2026-10-13, human:noelmcloughlin: the table says `!` after the type gives a major release, as `docs/releasing.md` does, but `.releaserc.json` uses the default Angular preset, which may not parse a `feat!:` header. Check what the configuration actually does with `!` before this concept repeats the claim.
