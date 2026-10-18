---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/releasing
title: Releasing
description: "How a release happens: `semantic-release.yml` computes the version from Conventional Commits and promotes `CHANGELOG.md` on merge to `main` but never tags, and a maintainer's `publish.yml` run checks that version against the changelog, lets `gh skill publish` create the tag and release, dispatches `knowledge-release.yaml` to attach the bundle, domain schema and Copilot zips, and asks the sibling hosts to sync."
genre: how-to
resource: .github/workflows/publish.yml
generated:
  by: process:ktl-librarian
  at: "2026-10-18T10:22:18Z"
status: draft
dependsOn:
  - https://w3id.org/ktl/knowledge/references/gh-skill-cli
references:
  - https://w3id.org/ktl/knowledge/playbooks/docent-in-m365-copilot
  - https://w3id.org/ktl/knowledge/policies/versioning
  - https://w3id.org/ktl/knowledge/playbooks/repository-validation
  - https://w3id.org/ktl/knowledge/playbooks/contributing
sources:
  - resource: .github/workflows/publish.yml
  - resource: docs/releasing.md
  - resource: .github/workflows/semantic-release.yml
  - resource: .github/scripts/changelog-release.mjs
  - resource: .releaserc.json
  - resource: .github/workflows/knowledge-release.yaml
  - resource: scripts/sync-sidecar.sh
  - resource: CHANGELOG.md
  - resource: https://github.com/semantic-release/commit-analyzer/blob/v13.0.1/README.md
  - resource: https://github.com/semantic-release/commit-analyzer/blob/v13.0.1/lib/default-release-rules.js
  - resource: https://github.com/conventional-changelog/conventional-changelog/blob/conventional-changelog-angular-v8.3.1/packages/conventional-changelog-angular/src/parser.js
verified:
  - by: process:ktl-librarian
    at: "2026-10-12T23:54:05Z"
---

# Overview

A person no longer hand-picks the version, but two tools never race to tag it. `semantic-release.yml`'s `release` job runs on every push to `main`, behind the `release` GitHub Environment. `@semantic-release/commit-analyzer` computes the next version from Conventional Commits since the last *tag*, using `.releaserc.json`'s `releaseRules`. Those rules add one type, `security:`, as a patch. A commit they do not match falls to the analyzer's default rules, where `fix:`, `perf:` and a revert give a patch, `feat:` a minor release, and a `BREAKING CHANGE:` note a major one. The analyzer reads each commit with its default Angular preset, whose header pattern has no place for `!`, so a `feat!:` commit releases nothing. `docs/releasing.md` counts such a commit as a major release, and the `plan` job as one that would release.

Semantic-release always runs with `--dry-run`, so it never writes, commits, tags, or publishes anything here. `@semantic-release/exec` calls `.github/scripts/changelog-release.mjs check` with the computed version, which refuses to proceed if `CHANGELOG.md`'s `## [Unreleased]` section is empty, and `notes`, which supplies the release notes.

Since 0.38.0 an empty `[Unreleased]` passes `check` when that version is already promoted and waits for `publish.yml`. A push with nothing new, such as a docs merge after a promotion, still finds the releasing commit since the last tag and asks for that version. `notes` then writes no `next_version`, so nothing is promoted twice. A failing `check` also writes its reason as a GitHub annotation. A plain shell step afterward:

- reads the version `--dry-run` computed;
- promotes that section to a dated heading itself;
- moves the librarian template's `TRUST_LADDER_SKILLS_REF` to the newest tag a host can clone;
- commits both directly as `chore(release): <version> - changelog promoted [skip ci]`.

The pin is two values, so the same step moves `TRUST_LADDER_SKILLS_SHA` to the commit that tag names: the install step refuses a tag that names any other commit. Only the template's pin moves. `GITHUB_TOKEN` may not push a change under `.github/workflows/`, so this repository's own copy keeps its old pin, which check 11 ignores (2026-09-24). `gh skill publish` stays this repository's only tag creator, for the reasons below.

Two qualifying merges to `main` between one `publish.yml` run and the next compute the *same* next version twice. The next version is computed from the last tag, and `gh skill publish` is a separate, later, human-triggered step. `promote` now checks whether the top released heading's version is still untagged. If so, it folds the new entries into it by `###` subsection instead of inserting a second heading for the same version. That was the bug that wrote two `## [0.19.0] - 2026-09-17` headings, orphaning the second merge's entries above an empty `[Unreleased]`. Check 14 in `playbooks/repository-validation.md` proves the fold and would have caught the original duplication. Since 0.42.0 the fold leaves out an entry the pending section already holds, because a pull request stacked on another still carries the other's entries under `[Unreleased]`, and check 14 proves that each entry is listed once.

The `plan` job also calls `changelog-release.mjs check` as its own step, not only inside `--dry-run`. Semantic-release detects a pull-request event and skips every plugin lifecycle hook, including `@semantic-release/exec`'s. So the `check` the paragraph before describes never ran on a pull request until this fix, and an empty `[Unreleased]` would have merged silently. That step reads the pull request's own commits first, and runs `check` only when one of them would release (the types `.releaserc.json` acts on). So a `chore:` or `docs:` pull request, a Dependabot action bump among them, is not failed for notes it was never going to release.

When the commits would release, a second step requires the pull request *title* to carry a releasing type, because a squash merge takes its subject from the title. GitHub's default title has none: pull request #46 merged that way and released nothing, its notes left waiting in `[Unreleased]`. The trigger names `edited` alongside the default pull-request types, because retitling is how that check is cleared and the default types never fire on a title change. Without it, the remedy the error message asks for could not clear the check.

Releases are still never tag-triggered. `gh skill publish` creates the tag *and* the GitHub release itself, so a tag-push trigger would race the tag the command is about to create. `workflow_dispatch` keeps the timing an explicit human decision. The `release` environment adds a maintainer-approval gate in front of the `contents: write` scope, the same Environment that `semantic-release.yml`'s write-scoped job now waits behind too.

Each `publish.yml` run validates:

- that the input is `vMAJOR.MINOR.PATCH`;
- that the tag does not already exist;
- that the bare version matches the top released heading in CHANGELOG.md, skipping `## [Unreleased]`, which catches a typed version nobody wrote release notes for.

It then sets up `uv` and re-runs the repository contract, the sidecar scripts' tests under `tests/` (run with pytest) and `gh skill publish --dry-run`, and only then publishes. The version is typed *with* the `v` (`v0.16.0`). The changelog heading never carries one, and the cross-check strips it before comparing.

Since 2026-09-24 it then dispatches `knowledge-release.yaml` for the new tag. That workflow attaches the bundle to the release as `knowledge-vX.Y.Z-knowledge-trust-ladder.zip` when the bundle changed since the last release that carries one. The zip is named after the repository, or after the name its `KNOWLEDGE_RELEASE_NAME` variable sets. Beside it (since 2026-09-24) it attaches the docent as a Microsoft 365 Copilot skill, `ktl-docent-m365-vX.Y.Z-knowledge-trust-ladder.zip`. It attaches one zip per instructions file under `.lokf/m365/`, each with its own checksum and attested alongside the bundle zip. If the builder is missing or refuses the bundle, the release carries the bundle zip alone. Since 0.46.0, when the host's `.lokf/justfile` names a domain schema on its `schema :=` line, the workflow also attaches that file as `schema-<tag>-<name>.yaml`, with its own `.sha256` and attestation. A federation that admits the bundle can then validate it on its own terms. The name must be a file in `.lokf/`, not a path.

The dispatch is needed because GitHub starts no workflow from a release made with `GITHUB_TOKEN`, so that workflow's own release trigger never fires here. If the dispatch fails, the job fails and names the manual run to make.

Since 0.47.0 `publish.yml` then asks the hosts named in the `KNOWLEDGE_SYNC_HOSTS` repository variable, as `owner/repo` separated by spaces, to run their `knowledge-sync.yaml` for the new tag. The dispatch needs the `KNOWLEDGE_SYNC_DISPATCH_TOKEN` secret, a token with Actions write on each host. Unset, or set to `false`, the variable asks nobody, and each host syncs on its own schedule. A host that cannot be asked is reported, and the others go ahead.

This release-process detail moved out of `CONTRIBUTING.md` on 2026-09-14 to `docs/releasing.md`, which states it for the three KTL repositories in one place. All six skills are released together under one tag, so a consumer can pin them to a single release. The `release` Environment's required reviewers are configured once, by hand, in each repository's settings, or a qualifying merge is released unattended. Changes reach `main` by pull request, but no ruleset enforces it, and "Require signed commits" as a branch rule is off and must stay off.

The sibling repositories (the two Obsidian plugins) carry byte-identical copies of the sidecar templates and their own skills pin. Only the first line of `.lokf/justfile`, which names the host, and its `schema :=` line are a sibling's own. Since 0.47.0 each sibling keeps itself current. Its `knowledge-sync.yaml` reads the pin and this repository's newest release each week. When the pin is behind, it runs the sibling's own `.lokf/scripts/knowledge-sync.sh`, which reads what to copy from the release's `templates/knowledge-sync.manifest`, and opens one pull request with the diff: the copies, the pin, and the changelog entry under `## [Unreleased]` and `### Security`. A later week's run refreshes that one pull request to the newest release until it is merged. The header of `knowledge-sync.sh` says what a sync copies, adds and refuses.

A new template goes in the manifest and in ktl-sidecar's Step 5 table, and nowhere else, because the preflight and contract check 11 read the manifest.

To open the pull requests on the day of a release, a maintainer runs `scripts/sync-sidecar.sh --pr <tag> <sibling>...` from this repository once the tag is on origin. The script:

- refuses anything but a release tag that is on origin and carries `skills/ktl-librarian/SKILL.md`;
- runs each sibling's own copy of `knowledge-sync.sh`, or the tag's copy in a sibling that has none, on a branch of its own, `sync-<tag>`, from origin's default branch;
- skips a sibling with uncommitted changes;
- without `--pr`, `--push` or `--commit`, leaves the sync uncommitted on the branch with the commit command printed, so the diff is the review.

Once the pull requests are merged, `scripts/sync-sidecar.sh --finish <tag> <sibling>...` puts each sibling back on its default branch, brings it up to date and removes the branch.

The pin and the copies move together because the skill a tag installs is written against the wrapper, gate and preflight that tag includes. Once a sibling turns on its scheduled librarian, the pin also decides which instructions run unattended. A release that touched neither the templates nor the librarian skill needs no sync. The template's pin is never bumped by hand, which would cut a pointless release. A tag that is not on origin is refused, because a sibling's scheduled librarian clones from there and would fail to install.

Both checks read the `workflow_dispatch` version input through an `env:` variable rather than interpolating `${{ inputs.version }}` straight into the shell script. That hardening change (2026-09-12) closes a script-injection vector without changing what the checks verify.
