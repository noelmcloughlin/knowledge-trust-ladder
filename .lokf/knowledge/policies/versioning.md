---
type: Policy
id: https://w3id.org/ktl/knowledge/policies/versioning
title: Versioning policy
description: One repository-level semantic version covering all six skills, released together under a single tag, with patch, minor and major decided by Conventional Commits.
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
  - resource: https://github.com/conventional-changelog/conventional-changelog/blob/conventional-changelog-conventionalcommits-v8.0.0/packages/conventional-changelog-conventionalcommits/src/parser.js
generated:
  by: process:ktl-librarian
  at: "2026-10-27T02:56:06Z"
about: []
verified:
  - by: process:ktl-librarian
    at: "2026-10-27T01:22:29Z"
  - by: human:noelmcloughlin
    at: "2026-09-10T00:00:00Z"
  - by: human:noelmcloughlin
    at: "2026-09-26T20:08:48Z"
  - by: human:noelmcloughlin
    at: "2026-10-03T09:44:34Z"
stale_after: 2027-10-03
status: draft
relatedTo:
  - https://w3id.org/ktl/knowledge/playbooks/releasing
---

# Overview

`vMAJOR.MINOR.PATCH`. Since 0.15.0 (2026-09-12, `CHANGELOG.md`) the bump is computed from [Conventional Commits](https://www.conventionalcommits.org/), and nobody picks a version number.

`docs/releasing.md` gives the bump for each type: `feat:` is minor, `fix:` and `security:` are patch, and a `BREAKING CHANGE:` footer or `!` after the type is major. `docs:`, `chore:`, `refactor:`, `style:`, `test:` and `ci:` release nothing: the change is merged, and its changelog entries are released with the next release that does.

The configuration agrees with that page on `!` since 0.56.3 (`CHANGELOG.md`). `.releaserc.json` names the Conventional Commits preset (`"preset": "conventionalcommits"`), and `semantic-release.yml` pins `conventional-changelog-conventionalcommits@8.0.0` beside `@semantic-release/commit-analyzer@13.0.1`. That preset's header pattern allows a `!` after the type, so a `feat!:` or `fix!:` commit gives a major release, as a `BREAKING CHANGE:` note does. The workflow's comment says the preset is named because the default, Angular, does not read the `!`. The analyzer's default rules also give `perf:` and a revert a patch, and `.releaserc.json` adds `security:` as a patch. The `plan` job in `semantic-release.yml` counts a commit with `!` as one that would release.

All six skills are released together under one tag rather than versioned independently, so a set pinned to one tag agrees with itself (`docs/architecture.md`).

One asymmetry to know: tags carry a `v` prefix (`v0.16.0`), and `publish.yml` refuses a version typed without it, while `CHANGELOG.md` headings never do (`## [0.16.0]`). The workflow's cross-check strips the `v` before comparing the two.

## Open questions

- 2026-10-27, human:noelmcloughlin: change the preset: set `"preset": "conventionalcommits"` in `.releaserc.json` and pin `conventional-changelog-conventionalcommits` beside commit-analyzer in `semantic-release.yml`, so `!` after the type gives a major release as `docs/releasing.md` says. The page and the `plan` job stay as they are; the fix lands outside `.lokf/`, in its own change.
