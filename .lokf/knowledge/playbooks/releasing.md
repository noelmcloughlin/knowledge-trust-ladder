---
type: Playbook
id: https://lokf-agent-skills.example/knowledge/playbooks/releasing
title: Releasing
description: semantic-release.yml computes the version and promotes CHANGELOG.md on merge to main but never tags, folding into a still-unpublished section rather than doubling it; a workflow_dispatch run of publish.yml then validates that version against the promoted changelog, re-checks the contract and spec, and lets gh skill publish create the tag and release.
genre: how-to
resource: .github/workflows/publish.yml
generated:
  by: process:lokf-librarian
  at: "2026-09-17T22:45:00Z"
status: draft
dependsOn:
- https://lokf-agent-skills.example/knowledge/references/gh-skill-cli
references:
  - https://lokf-agent-skills.example/knowledge/policies/versioning
  - https://lokf-agent-skills.example/knowledge/playbooks/repository-validation
  - https://lokf-agent-skills.example/knowledge/playbooks/contributing
verified:
- by: process:lokf-librarian
  at: "2026-09-17T22:45:00Z"
---

# Overview

A person no longer hand-picks the version, but two tools never race to tag
it. `semantic-release.yml`'s `release` job runs on every push to `main`,
behind the `release` GitHub Environment: `@semantic-release/commit-analyzer`
computes the next version from Conventional Commits since the last *tag*,
using `.releaserc.json`'s `releaseRules` - the Angular preset's defaults
(`fix:` -> patch, `feat:` -> minor, a `BREAKING CHANGE:` footer or `!` ->
major) plus one addition, `security:` -> patch. Semantic-release always
runs with `--dry-run`, so it never writes, commits, tags, or publishes
anything here; `@semantic-release/exec` calls
`.github/scripts/changelog-release.mjs check`, which refuses to proceed if
`CHANGELOG.md`'s `## [Unreleased]` section is empty, and `notes`, which
supplies the release notes. A plain shell step
afterward reads the version `--dry-run` computed, promotes that section to a
dated heading itself, and commits the change directly - `gh skill publish`
stays this repository's one and only tag creator, per the reasoning below.

Because the next version is computed from the last tag and `gh skill publish`
is a separate, later, human-triggered step, two qualifying merges to `main`
between one `publish.yml` run and the next compute the *same* next version
twice. `promote` now checks whether the top released heading's version is
still untagged and, if so, folds the new entries into it by `###` subsection
instead of inserting a second heading for the same version - the bug that
shipped two `## [0.19.0] - 2026-09-17` headings on 2026-09-17, orphaning the
second merge's entries above an empty `[Unreleased]`. The `plan` job also
calls `changelog-release.mjs check` as its own step, not only inside
`--dry-run`: semantic-release detects a pull-request event and skips every
plugin lifecycle hook, including `@semantic-release/exec`'s, so the `check`
this page's next section describes never ran on a pull request until this
fix, and an empty `[Unreleased]` would have merged silently. That step reads
the pull request's own commits first and runs `check` only when one of them
would release - the types `.releaserc.json` acts on - so a `chore:` or
`docs:` pull request, a Dependabot action bump among them, is not failed for
notes it was never going to ship. When they would release, the same step
also requires the pull request *title* to carry a releasing type, because a
squash merge takes its subject from the title and GitHub's default title
has none - pull request #46 merged that way on 2026-09-17 and released
nothing, its notes left waiting in `[Unreleased]`. Check 14 in
`playbooks/repository-validation.md` proves the fold and would have caught
the original duplication.

Releases are still never tag-triggered. `gh skill publish` creates the tag
*and* the GitHub release itself, so a tag-push trigger would race the tag the
command is about to create; `workflow_dispatch` keeps the timing an explicit
human decision, and the `release` environment adds a maintainer-approval gate
in front of the `contents: write` scope - the same Environment
`semantic-release.yml`'s write-scoped job now sits behind too.

Each `publish.yml` run validates that the input is `vMAJOR.MINOR.PATCH`, that
the tag does not already exist, and that the bare version matches the top
released heading in CHANGELOG.md, skipping `## [Unreleased]` (catching a
typed version nobody wrote release notes for), then re-runs the repository contract and `gh skill publish
--dry-run`, and only then publishes. The version is typed *with* the `v`
(`v0.16.0`); the changelog heading never carries one, and the cross-check
strips it before comparing. This release-process detail moved out of
`CONTRIBUTING.md` on 2026-09-14 to `docs/releasing.md`, which states it for
the three LOKF repositories in one place. All four skills ship together
under one tag, so a consumer can pin them to a single release.

Both checks read the `workflow_dispatch` version input through an `env:`
var rather than interpolating `${{ inputs.version }}` straight into the
shell script - a hardening change (2026-09-12) that closes a
script-injection vector without changing what the checks verify.
