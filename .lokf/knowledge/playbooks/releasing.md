---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/releasing
title: "Releasing"
description: "How the three repositories release: semantic-release.yml computes the version and promotes CHANGELOG.md on a merge to main but never tags; a maintainer runs publish.yml by hand; the siblings sync their templates and pin from the new tag."
genre: how-to
resource: docs/releasing.md
sources:
- resource: docs/releasing.md
- resource: .github/workflows/publish.yml
- resource: .github/workflows/semantic-release.yml
- resource: CONTRIBUTING.md
- resource: scripts/sync-sidecar.sh
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
references:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/docent-in-m365-copilot
  - https://knowledge-trust-ladder.example/knowledge/playbooks/repository-validation
  - https://knowledge-trust-ladder.example/knowledge/playbooks/contributing
dependsOn:
  - https://knowledge-trust-ladder.example/knowledge/references/gh-skill-cli
about:
  - https://knowledge-trust-ladder.example/knowledge/policies/versioning
---

# Overview

`knowledge-trust-ladder`, KTL Registrar and KTL Curator release the same way. Each repository's `semantic-release.yml` runs the same pinned semantic-release tool, and `docs/releasing.md` is the shared part. Nobody picks a version number: commits typed with Conventional Commits decide it, and the release note is `CHANGELOG.md`'s `## [Unreleased]` section, written as you go.

# What happens on a merge to main

1. `semantic-release` computes the next version from the commits since the last release, and stops if none warrant one.
2. `changelog-release.mjs check` refuses to proceed if `## [Unreleased]` is empty. The `plan` job runs the same check on every pull request whose commits would release, so a forgotten entry fails the pull request rather than the release.
3. That section is retitled `## [X.Y.Z] - YYYY-MM-DD`, a fresh empty `## [Unreleased]` is inserted above it, and the result is committed to `main`. If the top released section is still untagged, the new entries fold into it instead.
4. From here the repositories differ. In `knowledge-trust-ladder` this workflow creates no tag: `gh skill publish` is the one tag creator, so a maintainer runs `publish.yml` by hand with the version to ship, typed with its `v`. The workflow cross-checks the typed version against the promoted changelog, runs the repository contract and the dry run, publishes, and dispatches `knowledge-release.yaml` to attach the bundle zip. The two plugins tag a bare `X.Y.Z` and open a draft release a maintainer publishes.

Everything from step 3 on runs behind the `release` GitHub Environment, whose required reviewers must be configured by hand in each repository.

# The common trap

A squash merge takes its subject from the pull request title, and GitHub's default title has no type. So a typed `fix:` commit reaches `main` as "Fix the thing" and releases nothing. The `plan` job refuses a pull request whose commits would release but whose title would not; type the title like a commit.

# After a release of knowledge-trust-ladder

The sidecar template's own skills pin moves itself in the release commit, one release behind by design, and is never bumped by hand. The sibling repositories need a person: after `publish.yml` has tagged a release that changed a template or `skills/ktl-librarian/`, run `scripts/sync-sidecar.sh <tag> <sibling>...` from this repository. It refuses anything but a tag that is on origin and carries the skill. It copies that release's templates over each sibling's copies and moves the sibling's `TRUST_LADDER_SKILLS_REF` to the same tag. Then it runs the sidecar's checks there, and leaves the diff for a person to review and commit as `security(sidecar): ...`. The pin and the copies move together, from one tag, because once a sibling arms its scheduled librarian, the pin decides which instructions run unattended.

# Repository settings

Changes reach `main` by pull request, but no ruleset enforces it, because a ruleset requiring pull requests would also reject the release job's own push. "Require signed commits" as a branch rule is off and must stay off, since a commit made inside a runner is unsigned. Sign your own commits anyway.
