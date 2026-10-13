---
type: Policy
id: https://knowledge-trust-ladder.example/knowledge/policies/versioning
title: Versioning policy
description: One repository-level semantic version covering all five skills, released together under a single tag, with patch, minor and major decided by Conventional Commits.
genre: reference
resource: docs/releasing.md
sources:
- resource: docs/releasing.md
- resource: docs/architecture.md
- resource: CONTRIBUTING.md
- resource: CHANGELOG.md
- resource: .github/workflows/publish.yml
- resource: .releaserc.json
- resource: .github/workflows/semantic-release.yml
- resource: https://github.com/semantic-release/commit-analyzer/blob/v13.0.1/README.md
- resource: https://github.com/semantic-release/commit-analyzer/blob/v13.0.1/lib/default-release-rules.js
- resource: https://github.com/conventional-changelog/conventional-changelog/blob/conventional-changelog-angular-v8.3.1/packages/conventional-changelog-angular/src/parser.js
generated:
  by: process:ktl-librarian
  at: "2026-10-13T15:08:54Z"
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

`vMAJOR.MINOR.PATCH`. Since 0.15.0 (2026-09-12, `CHANGELOG.md`) the bump is computed from [Conventional Commits](https://www.conventionalcommits.org/), and nobody picks a version number.

`docs/releasing.md` gives the bump for each type: `feat:` is minor, `fix:` and `security:` are patch, and a `BREAKING CHANGE:` footer or `!` after the type is major. `docs:`, `chore:`, `refactor:`, `style:`, `test:` and `ci:` release nothing: the change is merged, and its changelog entries are released with the next release that does.

The configuration differs from that page on `!`. `.releaserc.json` names no preset, so `@semantic-release/commit-analyzer` reads each commit with its default, the Angular preset, whose header pattern has no place for `!`. A `feat!:` or `fix!:` commit therefore has no type, and no release rule matches it. Only a `BREAKING CHANGE:` note gives a major release. The analyzer's default rules also give `perf:` and a revert a patch, and `.releaserc.json` adds `security:` as a patch. The `plan` job in `semantic-release.yml` counts a commit with `!` as one that would release.

All five skills are released together under one tag rather than versioned independently, so a set pinned to one tag agrees with itself (`docs/architecture.md`).

One asymmetry to know: tags carry a `v` prefix (`v0.16.0`), and `publish.yml` refuses a version typed without it, while `CHANGELOG.md` headings never do (`## [0.16.0]`). The workflow's cross-check strips the `v` before comparing the two.

## Open questions

- 2026-10-13, human:noelmcloughlin: the table says `!` after the type gives a major release, as `docs/releasing.md` does, but `.releaserc.json` uses the default Angular preset, which may not parse a `feat!:` header. Check what the configuration actually does with `!` before this concept repeats the claim.
- 2026-10-13, process:ktl-librarian: `docs/releasing.md` and the `plan` job in `.github/workflows/semantic-release.yml` treat `!` after the type as breaking. `.releaserc.json` names no preset, and the default Angular preset of commit-analyzer, which the workflow pins at 13.0.1, has no place for `!` in its header pattern, so a `feat!:` commit releases nothing. Which should change: the preset, or the page and the plan job?
