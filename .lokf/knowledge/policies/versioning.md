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
    id: changelog.md
    excerpt: "**A `!` after the type releases a major version.** `.releaserc.json` names the Conventional Commits preset, so a `feat!:` commit no longer releases nothing"
  - resource: .github/workflows/publish.yml
  - resource: .releaserc.json
  - resource: .github/workflows/semantic-release.yml
  - resource: .release/package.json
  - resource: https://github.com/semantic-release/commit-analyzer/blob/v13.0.1/README.md
  - resource: https://github.com/semantic-release/commit-analyzer/blob/v13.0.1/lib/default-release-rules.js
  - resource: https://unpkg.com/conventional-changelog-conventionalcommits@10.4.1/src/parser.js
generated:
  by: process:ktl-librarian
  at: "2026-11-17T20:29:12Z"
about: []
verified:
  - by: process:ktl-librarian
    at: "2026-11-26T02:26:42Z"
  - by: human:noelmcloughlin
    at: "2026-09-10T00:00:00Z"
  - by: human:noelmcloughlin
    at: "2026-09-26T20:08:48Z"
  - by: human:noelmcloughlin
    at: "2026-10-03T09:44:34Z"
  - by: human:noelmcloughlin
    at: "2026-11-13T14:57:53Z"
    revision: "e5826e759a160b3dfb53cece4481eb5b1ba78046"
stale_after: 2027-11-13
relatedTo:
  - https://w3id.org/ktl/knowledge/playbooks/releasing
---

# Overview

`vMAJOR.MINOR.PATCH`. The bump is computed from [Conventional Commits](https://www.conventionalcommits.org/), and nobody picks a version number.

`docs/releasing.md` gives the bump for each type:

- `feat:` is minor.
- `fix:`, `perf:` and `security:` are patch.
- A revert as `git revert` writes it, a subject that starts `Revert` and a body that says `This reverts commit <hash>.`, is a patch, unless the commit it reverts is still unreleased: then neither counts.
- A `BREAKING CHANGE:` footer or `!` after the type is major.
- `docs:`, `chore:`, `refactor:`, `style:`, `test:`, `build:` and `ci:`, and a `revert:` typed by hand without that sentence, release nothing: the change is merged, and its changelog entries are released with the next release that does.

The configuration agrees with that page on `!`.[^changelog.md] `.releaserc.json` names the Conventional Commits preset (`"preset": "conventionalcommits"`). `semantic-release.yml` installs the release tools with `npm ci` from `.release/`, whose lockfile pins every package, each checked by its hash. Among them are `conventional-changelog-conventionalcommits` 10.4.1 and `@semantic-release/commit-analyzer` 13.0.1. That preset's header pattern allows a `!` after the type, so a `feat!:` or `fix!:` commit gives a major release, as a `BREAKING CHANGE:` note does. The workflow's comment says the preset is named because the default, Angular, does not read the `!`. The analyzer's default rules also give `perf:` and a revert a patch, and `.releaserc.json` adds `security:` as a patch. The `plan` job in `semantic-release.yml` counts a commit as one that would release when its subject's type is `feat`, `fix`, `perf` or `security` or carries a `!`, when it has a `BREAKING CHANGE` footer, or when it is a revert that says which commit it reverts. When the commits would release, the job refuses a pull request title that would not, and it takes a revert's own title only over such a revert.

All six skills are released together under one tag rather than versioned independently, so a set pinned to one tag agrees with itself (`docs/architecture.md`).

One asymmetry to know: tags carry a `v` prefix (`v0.16.0`), and `publish.yml` refuses a version typed without it, while `CHANGELOG.md` headings never do (`## [0.16.0]`). The workflow's cross-check strips the `v` before comparing the two.

[^changelog.md]: CHANGELOG.md, the Fixed entry on a `!` after the type
