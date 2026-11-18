---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/releasing
title: Releasing
description: "How a release happens: `semantic-release.yml` computes the version from Conventional Commits and promotes `CHANGELOG.md` on merge to `main` but never tags, and a maintainer's `publish.yml` run checks that version against the changelog, lets `gh skill publish` create the tag and release, dispatches `knowledge-release.yaml` to attach the bundle's zip, its domain vocabulary, its evidence table and, once `KNOWLEDGE_M365_ENABLED` is `true`, the Copilot zips, and asks the sibling hosts to sync."
genre: how-to
resource: .github/workflows/publish.yml
generated:
  by: process:ktl-librarian
  at: "2026-11-17T20:29:12Z"
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
    id: docs-releasing.md
    excerpt: An index holds only one pending publisher for those details at a time
  - resource: .github/workflows/semantic-release.yml
  - resource: .github/scripts/changelog-release.mjs
  - resource: .releaserc.json
  - resource: .github/workflows/knowledge-release.yaml
    id: knowledge-release.yaml
    excerpt: It stops on a name two files define differently
  - resource: CHANGELOG.md
    id: changelog.md
    excerpt: "`.releaserc.json` names the Conventional Commits preset, so a `feat!:` commit no longer releases nothing"
  - resource: https://github.com/semantic-release/commit-analyzer/blob/v13.0.1/README.md
  - resource: https://github.com/semantic-release/commit-analyzer/blob/v13.0.1/lib/default-release-rules.js
  - resource: https://github.com/conventional-changelog/conventional-changelog/blob/conventional-changelog-conventionalcommits-v8.0.0/packages/conventional-changelog-conventionalcommits/src/parser.js
  - resource: .github/workflows/pypi.yml
  - resource: .pypi
verified:
  - by: process:ktl-librarian
    at: "2026-11-18T00:02:42Z"
---

# Overview

A person no longer hand-picks the version, but two tools never race to tag it. `semantic-release.yml`'s `release` job runs on every push to `main`, behind the `release` GitHub Environment. `@semantic-release/commit-analyzer` computes the next version from Conventional Commits since the last *tag*, using `.releaserc.json`'s `releaseRules`. Those rules add one type, `security:`, as a patch. A commit they do not match falls to the analyzer's default rules, where `fix:`, `perf:` and a revert give a patch, `feat:` a minor release, and a `BREAKING CHANGE:` note a major one. `docs/releasing.md` counts a revert only as `git revert` writes it, and counts neither the revert nor the commit it reverts while that commit is still unreleased. The analyzer reads each commit with the Conventional Commits preset,[^changelog.md] which `.releaserc.json` names and `semantic-release.yml` pins as `conventional-changelog-conventionalcommits@8.0.0` beside `@semantic-release/commit-analyzer@13.0.1`. That preset's header pattern allows a `!` after the type, so a `feat!:` commit gives a major release, as `docs/releasing.md` says. The `plan` job counts such a commit as one that would release.

Semantic-release always runs with `--dry-run`, so it never writes, commits, tags, or publishes anything here. `@semantic-release/exec` calls `.github/scripts/changelog-release.mjs check` with the computed version, which refuses to proceed if `CHANGELOG.md`'s `## [Unreleased]` section is empty, and `notes`, which supplies the release notes.

An empty `[Unreleased]` passes `check` when that version is already promoted and waits for `publish.yml`. A push with nothing new, such as a docs merge after a promotion, still finds the releasing commit since the last tag and asks for that version. `notes` then writes no `next_version`, so nothing is promoted twice. A failing `check` also writes its reason as a GitHub annotation. A plain shell step afterward:

- reads the version `--dry-run` computed;
- promotes that section to a dated heading itself;
- moves the `ktl` pin in the sidecar's `templates/pyproject.toml` to the newest tag, whose package `publish.yml` put on PyPI;
- commits both directly as `chore(release): <version> - changelog promoted [skip ci]`.

The template pins `ktl` one release behind, because the new changelog heading exists before its tag. Check 15 of `validate-repository.sh` requires the pin to name one of the two newest releases, and that tag to carry `skills/ktl-librarian` and the sync manifest.[^docs-releasing.md] `gh skill publish` stays this repository's only tag creator, for the reasons below.

Two qualifying merges to `main` between one `publish.yml` run and the next compute the *same* next version twice. The next version is computed from the last tag, and `gh skill publish` is a separate, later, human-triggered step. `promote` now checks whether the top released heading's version is still untagged. If so, it folds the new entries into it by `###` subsection instead of inserting a second heading for the same version. That was the bug that wrote two `## [0.19.0] - 2026-09-17` headings, orphaning the second merge's entries above an empty `[Unreleased]`. Check 14 in `playbooks/repository-validation.md` proves the fold and would have caught the original duplication. The fold leaves out an entry the pending section already holds, with the indented lines under it, and keeps an entry that differs below its first line, because a pull request stacked on another still carries the other's entries under `[Unreleased]`, and check 14 proves that each entry is listed once.

The `plan` job also calls `changelog-release.mjs check` as its own step, not only inside `--dry-run`. Semantic-release detects a pull-request event and skips every plugin lifecycle hook, including `@semantic-release/exec`'s. So the `check` the paragraph before describes never ran on a pull request until this fix, and an empty `[Unreleased]` would have merged silently. That step reads the pull request's own commits first, from the merge-base of the base branch and the head commit. `HEAD` is GitHub's trial merge with that day's `main`, so on a branch that `main` has moved past it would read `main`'s commits too. It runs `check` only when one of them would release, as the pinned commit-analyzer counts them, so a `perf:` commit and a revert count too. So a `chore:` or `docs:` pull request, a Dependabot action bump among them, is not failed for notes it was never going to release.

When the commits would release, a second step requires the pull request *title* to carry a releasing type, because a squash merge takes its subject from the title. GitHub's default title has none: pull request #46 merged that way and released nothing, its notes left waiting in `[Unreleased]`. The trigger names `edited` alongside the default pull-request types, because retitling is how that check is cleared and the default types never fire on a title change. Without it, the remedy the error message asks for could not clear the check.

Releases are still never tag-triggered. `gh skill publish` creates the tag *and* the GitHub release itself, so a tag-push trigger would race the tag the command is about to create. `workflow_dispatch` keeps the timing an explicit human decision. The `release` environment, once it has required reviewers, adds a maintainer-approval gate in front of the `contents: write` scope, the same Environment that `semantic-release.yml`'s write-scoped job now waits behind too.

Each `publish.yml` run validates:

- that the input is `vMAJOR.MINOR.PATCH`;
- that the tag does not already exist;
- that the bare version matches the top released heading in CHANGELOG.md, skipping `## [Unreleased]`, which catches a typed version nobody wrote release notes for.

These checks, the repository contract and the sidecar scripts' tests under `tests/` (run with pytest) run in a read-only `verify` job, which installs the test packages by hash from `tests/requirements.txt`, compiled from `tests/requirements.in`. The `publish` job holds the write token behind the `release` Environment, needs `verify` and runs neither (`CHANGELOG.md`). It checks again that the tag is still free, since the tag may have been made while the run waited, then runs `gh skill publish --dry-run`. `gh skill publish` tags the head of `main`, so the job publishes only while `main` is still the commit `verify` checked. After a merge during the run, a maintainer runs the workflow again. Once it has published, the job reads the tag back, and requests no bundle zip, package or sync when the tag names another commit. The version is typed *with* the `v` (`v0.16.0`). The changelog heading never carries one, and the cross-check strips it before comparing.

It then dispatches `knowledge-release.yaml` for the new tag. That workflow attaches the bundle to the release as `knowledge-vX.Y.Z-knowledge-trust-ladder.zip` when the bundle changed since the last release that carries one. The zip is named after the repository, or after the name its `KNOWLEDGE_RELEASE_NAME` variable sets. Beside it, the workflow attaches the docent as a Microsoft 365 Copilot skill, `ktl-docent-m365-vX.Y.Z-knowledge-trust-ladder.zip`, once the repository variable `KNOWLEDGE_M365_ENABLED` is `true`, since the Copilot skill is unfinished.[^knowledge-release.yaml] It attaches one zip per instructions file under `.lokf/m365/`, each with its own checksum and attested alongside the bundle zip. If the builder is missing or refuses the bundle, the release carries the bundle zip alone.

When the host's `.lokf/justfile` names a domain vocabulary on its `schema :=` line, the workflow also attaches that file as `schema-<tag>-<name>.yaml`, with its own `.sha256` and attestation. A federation that admits the bundle can then validate it on its own terms. The line may name any file in the repository, such as a linkml-sidecar schema, but never one outside it, and the released copy imports LOKF core as `lokf`. A release whose only change is the schema packs again, and any other local file the schema imports is merged into the released copy, so a composite of two `lokf adapt` copies is released as one file. The merge stops the release on a name two files define differently. The release identifies that file by the tag and the schema's own file name alone, in the asset name and its `.sha256`, never by a `version:` slot inside the schema, so the schema's own `version:` can read the same across several releases that change its content.[^knowledge-release.yaml]

When the bundle changed, the workflow also attaches its evidence table as `evidence-<tag>-<name>.tsv`, with its own `.sha256` and attestation. The host's `knowledge-report.sh evidence` writes it from frontmatter alone: one row for each concept's `generated` record and one for each `verified` event, with a `check` column that says whether a person's event is a first confirmation, the same person confirming again or a second person's re-check. A sidecar whose script has no `evidence` form gets a notice, and its release carries no table.

On a public repository the release also carries the files' signed build provenance, as `provenance-<tag>-<name>.intoto.jsonl`, which `gh attestation verify --bundle` reads.

The dispatch is needed because GitHub starts no workflow from a release made with `GITHUB_TOKEN`, so that workflow's own release trigger never fires here. If the dispatch fails, the job fails and names the manual run to make.

`publish.yml` then asks the hosts named in the `KNOWLEDGE_SYNC_HOSTS` repository variable, as `owner/repo` separated by spaces, to run their `knowledge-sync.yaml` for the new tag. The dispatch needs the `KNOWLEDGE_SYNC_DISPATCH_TOKEN` secret, a token with Actions write on each host. Unset, or set to `false`, the variable asks nobody, and each host syncs on its own schedule. A host that cannot be asked is reported, and the others go ahead. A fine-grained token reaches one owner's repositories alone, so a host under another owner is reported and syncs on its schedule. `ktl gh plan` names a host that was renamed.

`docs/releasing.md` states this release-process detail for the three KTL repositories in one place. All six skills are released together under one tag, so a consumer can pin them to a single release. Required reviewers on the `release` Environment wait until releases have downstream users, so until then a qualifying merge is released unattended. A maintainer then adds them in each repository's settings, or with `ktl gh apply --recommended`, and `ktl gh check --strict` names a repository without one. Changes reach `main` by pull request, but no ruleset enforces it, and "Require signed commits" as a branch rule is off and must stay off.

The sibling repositories (the two Obsidian plugins) carry byte-identical copies of the sidecar templates and their own skills pin. Only the first line of `.lokf/justfile`, which names the host, and its `schema :=` line are a sibling's own.

Each sibling keeps itself current. Its `knowledge-sync.yaml` reads the `ktl` pin in `.lokf/pyproject.toml` and asks its package index for the newest release each week. When the pin is behind, it runs the sibling's own `.lokf/scripts/knowledge-sync.sh`, which reads what to copy from the release's `templates/knowledge-sync.manifest`, and opens one pull request with the diff: the copies, the pin, and the changelog entry under `## [Unreleased]` and `### Security`. A later week's run refreshes that one pull request to the newest release until it is merged. The branch the sync pushes carries no workflow a release wrote (`CHANGELOG.md`). `publish` keeps every workflow as the default branch has it, and holds the release's workflow changes for a person, or for a reviewer of the Environment that `KNOWLEDGE_SYNC_REVIEW_ENVIRONMENT` names. The header of `knowledge-sync.sh` says what a sync copies, adds and refuses.

A new template goes in the manifest and in ktl-sidecar's Step 5 table, and nowhere else, because the preflight and contract check 11 read the manifest.

To open a sibling's pull request on the day of a release, once its `ktl` package is on PyPI, a maintainer starts the sibling's `knowledge-sync.yaml` by hand with the tag, or runs `.lokf/scripts/knowledge-sync.sh --pr <tag>` in a clone of it.

The pin and the copies move together because the skill a tag installs is written against the wrapper, gate and preflight that tag includes. Once a sibling turns on its scheduled librarian, the pin also decides which instructions run unattended. A release that touched neither the templates nor the librarian skill needs no sync, and the workflow and the script both say so. The template's pin is never bumped by hand, which would cut a pointless release.

Both checks read the `workflow_dispatch` version input through an `env:` variable rather than interpolating `${{ inputs.version }}` straight into the shell script. That hardening change closes a script-injection vector without changing what the checks verify.

# The ktl package on PyPI

`publish.yml` also dispatches `pypi.yml` for the new tag. It builds two packages from the tag: `ktl`, which carries the skills, and `knowledge-trust-ladder`, which holds no code and installs `ktl` at the same version. It checks that a second build makes the same bytes. It uploads only when the repository variable `PYPI_RELEASE_ENABLED` is `testpypi` or `true`, through the `testpypi` or `pypi` Environment, limited to tags matching `v*`. A required reviewer on each is recommended, since a pushed tag runs its own copy of `pypi.yml`, which can drop every check in it. `ktl gh apply --recommended` adds one, and `ktl gh check --strict` names an Environment without one. After an upload to PyPI, it attaches a `.sha256` file for each package file to the GitHub release, and the files' signed provenance as `provenance-<tag>-packages.intoto.jsonl`.

Before the first upload to each index, a maintainer registers a pending publisher for `ktl`. An index holds only one pending publisher for the same owner, repository, workflow and Environment at a time. So the first upload creates `ktl` and then fails at `knowledge-trust-ladder`. The maintainer then registers that project's publisher with the same details and runs the failed job again.[^docs-releasing.md]

[^changelog.md]: CHANGELOG.md, 0.57.0, Fixed
[^knowledge-release.yaml]: .github/workflows/knowledge-release.yaml, the Pack the domain vocabulary step (quoted) and the Pack the Copilot skills step

[^docs-releasing.md]: docs/releasing.md, The ktl package on PyPI (quoted), and for check 15 the section on what follows a releasing merge
