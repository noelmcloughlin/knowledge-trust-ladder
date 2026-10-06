---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/releasing
title: Releasing
description: "How a release happens: `semantic-release.yml` computes the version from Conventional Commits and promotes `CHANGELOG.md` on merge to `main` but never tags, and a maintainer's `publish.yml` run checks that version against the changelog, lets `gh skill publish` create the tag and release, and dispatches `knowledge-release.yaml` to attach the bundle and Copilot zips."
genre: how-to
resource: .github/workflows/publish.yml
generated:
  by: process:ktl-librarian
  at: "2026-10-05T12:41:36Z"
status: draft
dependsOn:
- https://knowledge-trust-ladder.example/knowledge/references/gh-skill-cli
references:
- https://knowledge-trust-ladder.example/knowledge/playbooks/docent-in-m365-copilot
- https://knowledge-trust-ladder.example/knowledge/policies/versioning
- https://knowledge-trust-ladder.example/knowledge/playbooks/repository-validation
- https://knowledge-trust-ladder.example/knowledge/playbooks/contributing
sources:
- resource: .github/workflows/publish.yml
- resource: docs/releasing.md
- resource: .github/workflows/semantic-release.yml
- resource: .github/scripts/changelog-release.mjs
- resource: .releaserc.json
- resource: .github/workflows/knowledge-release.yaml
- resource: scripts/sync-sidecar.sh
- resource: CHANGELOG.md
verified:
- by: process:ktl-librarian
  at: "2026-10-06T11:10:52Z"
---

# Overview

A person no longer hand-picks the version, but two tools never race to tag it. `semantic-release.yml`'s `release` job runs on every push to `main`, behind the `release` GitHub Environment. `@semantic-release/commit-analyzer` computes the next version from Conventional Commits since the last *tag*, using `.releaserc.json`'s `releaseRules`: the Angular preset's defaults (`fix:` -> patch, `feat:` -> minor, a `BREAKING CHANGE:` footer or `!` -> major) plus one addition, `security:` -> patch.

Semantic-release always runs with `--dry-run`, so it never writes, commits, tags, or publishes anything here. `@semantic-release/exec` calls `.github/scripts/changelog-release.mjs check`, which refuses to proceed if `CHANGELOG.md`'s `## [Unreleased]` section is empty, and `notes`, which supplies the release notes. A plain shell step afterward:

- reads the version `--dry-run` computed;
- promotes that section to a dated heading itself;
- moves the librarian template's `TRUST_LADDER_SKILLS_REF` to the newest tag a host can clone;
- commits both directly as `chore(release): <version> - changelog promoted [skip ci]`.

The pin is two values, so the same step moves `TRUST_LADDER_SKILLS_SHA` to the commit that tag names: the install step refuses a tag that names any other commit. Only the template's pin moves. `GITHUB_TOKEN` may not push a change under `.github/workflows/`, so this repository's own copy keeps its old pin, which check 11 ignores (2026-09-24). `gh skill publish` stays this repository's one and only tag creator, for the reasons below.

Because the next version is computed from the last tag, and `gh skill publish` is a separate, later, human-triggered step, two qualifying merges to `main` between one `publish.yml` run and the next compute the *same* next version twice. `promote` now checks whether the top released heading's version is still untagged. If so, it folds the new entries into it by `###` subsection instead of inserting a second heading for the same version. That was the bug that wrote two `## [0.19.0] - 2026-09-17` headings, orphaning the second merge's entries above an empty `[Unreleased]`. Check 14 in `playbooks/repository-validation.md` proves the fold and would have caught the original duplication.

The `plan` job also calls `changelog-release.mjs check` as its own step, not only inside `--dry-run`. Semantic-release detects a pull-request event and skips every plugin lifecycle hook, including `@semantic-release/exec`'s. So the `check` this page's next section describes never ran on a pull request until this fix, and an empty `[Unreleased]` would have merged silently. That step reads the pull request's own commits first, and runs `check` only when one of them would release (the types `.releaserc.json` acts on). So a `chore:` or `docs:` pull request, a Dependabot action bump among them, is not failed for notes it was never going to release.

When the commits would release, a second step requires the pull request *title* to carry a releasing type, because a squash merge takes its subject from the title. GitHub's default title has none: pull request #46 merged that way and released nothing, its notes left waiting in `[Unreleased]`. The trigger names `edited` alongside the default pull-request types, because retitling is how that check is cleared and the default types never fire on a title change. Without it, the remedy the error message asks for could not clear the check.

Releases are still never tag-triggered. `gh skill publish` creates the tag *and* the GitHub release itself, so a tag-push trigger would race the tag the command is about to create. `workflow_dispatch` keeps the timing an explicit human decision. The `release` environment adds a maintainer-approval gate in front of the `contents: write` scope, the same Environment that `semantic-release.yml`'s write-scoped job now waits behind too.

Each `publish.yml` run validates:

- that the input is `vMAJOR.MINOR.PATCH`;
- that the tag does not already exist;
- that the bare version matches the top released heading in CHANGELOG.md, skipping `## [Unreleased]`, which catches a typed version nobody wrote release notes for.

It then sets up `uv` and re-runs the repository contract and `gh skill publish --dry-run`, and only then publishes. The version is typed *with* the `v` (`v0.16.0`). The changelog heading never carries one, and the cross-check strips it before comparing.

Since 2026-09-24 it then dispatches `knowledge-release.yaml` for the new tag. That workflow attaches the bundle to the release as `knowledge-vX.Y.Z-knowledge-trust-ladder.zip` (the repository's name, or the one its `KNOWLEDGE_RELEASE_NAME` variable sets) when the bundle changed since the last release that carries one. Beside it (since 2026-09-24) it attaches the docent as a Microsoft 365 Copilot skill, `ktl-docent-m365-vX.Y.Z-knowledge-trust-ladder.zip`: one zip per instructions file under `.lokf/m365/`, each with its own checksum and attested alongside the bundle zip. If the builder is missing or refuses the bundle, the release carries the bundle zip alone. The dispatch is needed because GitHub starts no workflow from a release made with `GITHUB_TOKEN`, so that workflow's own release trigger never fires here. If the dispatch fails, the job fails and names the manual run to make.

This release-process detail moved out of `CONTRIBUTING.md` on 2026-09-14 to `docs/releasing.md`, which states it for the three KTL repositories in one place. All five skills are released together under one tag, so a consumer can pin them to a single release. The `release` Environment's required reviewers are configured once, by hand, in each repository's settings, or a qualifying merge is released unattended. Changes reach `main` by pull request, but no ruleset enforces it, and "Require signed commits" as a branch rule is off and must stay off.

The sibling repositories (the two Obsidian plugins and ai-linkmo) carry byte-identical copies of the sidecar templates and their own skills pin. Since 2026-09-24 `scripts/sync-sidecar.sh <tag> <sibling>...` brings each up to one release. It refuses anything but a tag that is on origin and carries `skills/ktl-librarian`. It copies that tag's templates over the copies the sibling already has. It adds a template the sibling lacks when ktl-sidecar puts it on every host or a copy there cannot run without it. It reports any other, and adds nothing more. Then it moves the sibling's `TRUST_LADDER_SKILLS_REF` to the same tag, and its `TRUST_LADDER_SKILLS_SHA` to the commit that tag names. It runs the sidecar's checks there, prints a draft changelog line and the commit command, and never commits.

The pin and the copies move together because the skill a tag installs is written against the wrapper, gate and preflight that tag includes, and once a sibling turns on its scheduled librarian, the pin decides which instructions run unattended. A release that touched neither the templates nor the librarian skill needs no sync. The template's pin is never bumped by hand, which would cut a pointless release. The sibling's pull request is opened after the tag exists, since a sibling merged before its pin's tag fails at the install step on its next scheduled run.

Both checks read the `workflow_dispatch` version input through an `env:` var rather than interpolating `${{ inputs.version }}` straight into the shell script. That hardening change (2026-09-12) closes a script-injection vector without changing what the checks verify.
