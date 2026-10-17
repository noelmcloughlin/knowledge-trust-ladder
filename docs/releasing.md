# How the three repositories release

[`knowledge-trust-ladder`](https://github.com/noelmcloughlin/knowledge-trust-ladder), [KTL Registrar](https://github.com/noelmcloughlin/obsidian-ktl-registrar) and [KTL Curator](https://github.com/noelmcloughlin/obsidian-ktl-curator) release the same way. Each repository's `semantic-release.yml` runs the same pinned [semantic-release](https://semantic-release.gitbook.io/) tool. This page is the shared part. Each workflow's own header comment carries that repository's detail and the reasons behind it.

## The version is computed; you write the commit message

Nobody picks a version number. Commits typed with [Conventional Commits](https://www.conventionalcommits.org/) decide it:

| Commit type | Release |
| --- | --- |
| `feat:` | minor |
| `fix:`, `security:` | patch |
| `BREAKING CHANGE:` in a footer, or `!` after the type | major |
| `docs:`, `chore:`, `refactor:`, `style:`, `test:`, `ci:` | none: the change merges, releases nothing, and its changelog entries wait for the next release that does |

Type the commit for what the change *is*. A behaviour change is a `feat:` even when most of the diff is prose. If a pull request should release and its commits are typed too quietly, squash-merge it and give the squash commit the right type.

The reverse trap is a squash merge that takes its subject from the pull request *title*, which GitHub defaults to the branch name in words, with no type. So a typed `fix:` commit reaches `main` as "Fix the thing (#46)" and releases nothing. The `plan` job refuses a pull request whose commits would release but whose title would not. Type the title like a commit. The workflow listens for `edited` pull requests as well as pushes, so retitling re-runs the check on its own.

The release note is `CHANGELOG.md`'s `## [Unreleased]` section, written as you go: a line or two per change, with the detail left to the code's comments. The pipeline releases only what has already been written up.

`changelog-release.mjs check` refuses an empty section. The `plan` job runs it on each pull request, so a forgotten entry fails the pull request rather than the release. The check runs only when the pull request's own commits would release, so a `chore:`, `docs:` or `ci:` pull request, or a Dependabot bump, is not asked for notes.

## What happens on a merge to `main`

1. `semantic-release` computes the next version from the commits since the last release, and stops if none warrant one.
2. `changelog-release.mjs check` refuses to proceed if `## [Unreleased]` is empty.
3. That section is retitled `## [X.Y.Z] - YYYY-MM-DD`, a fresh empty `## [Unreleased]` is inserted above it, and the result is committed to `main`. In `knowledge-trust-ladder`, where tagging is a separate later step, a second qualifying merge before `publish.yml` runs computes the same version again, and its entries merge into the still-untagged section, which takes the new version and date.
4. From here the repositories differ:

| Repository | Tag | Then |
| --- | --- | --- |
| `knowledge-trust-ladder` | None from this workflow. `gh skill publish` is the one tag creator, so a maintainer runs `publish.yml` by hand with the version to release, typed with its `v` (`v0.16.0`); the workflow cross-checks it against the promoted changelog first. Tags carry the `v`, changelog headings never do. | The six skills publish to the registry under that one tag. `publish.yml` then dispatches `knowledge-release.yaml`, which attaches the bundle to the release as `knowledge-vX.Y.Z-knowledge-trust-ladder.zip` when it changed since the last release that carries one. |
| KTL Registrar, KTL Curator | Bare `X.Y.Z`, Obsidian's convention, after `package.json`, `manifest.json` and `versions.json` are bumped as `npm version` would. | `release.yml` builds, attests provenance and opens a **draft** release carrying `main.js`, `manifest.json` and `styles.css`; a maintainer reviews and publishes it. A hand-pushed tag takes the same path. Publishing the draft is a person's event, not the token's, so it fires `knowledge-release.yaml` once `KNOWLEDGE_RELEASE_ENABLED` is `true` there; no dispatch is needed. |

Everything from step 3 on runs behind the `release` GitHub Environment. **Configure required reviewers on it once, in each repository's Settings → Environments**, or a qualifying merge is released unattended. Creating the environment does not do that for you.

## After a releasing merge to `knowledge-trust-ladder`, what follows

The scaffolding template's `TRUST_LADDER_SKILLS_REF` sits one release behind. When `semantic-release.yml` promotes the changelog, the new heading exists but its tag does not yet, so the release commit moves the pin to the newest tag a host can clone. It moves nothing under `.github/workflows/`, which `GITHUB_TOKEN` may not push.

The pin is two values, `TRUST_LADDER_SKILLS_REF` and `TRUST_LADDER_SKILLS_SHA`, the commit the tag names, and the install step refuses a tag that names any other commit. Check 15 of `validate-repository.sh` requires the pin to name one of the two newest releases, a tag that carries `skills/ktl-librarian`, and the commit that tag names. Never bump the pin by hand: that commit triggers a needless release, and the next promotion moves the pin anyway.

The sibling repositories carry byte-identical copies of the templates and their own pin. Only the first line of `.lokf/justfile`, which names the host, and its `schema :=` line are a sibling's own. The copies and the pin move together from one tag, because the skill a tag installs is written against the wrapper, gate and preflight that tag includes. Once a sibling turns on its scheduled librarian, the pin decides which agent instructions run unattended.

Each sibling keeps itself current. Its `knowledge-sync.yaml` reads the pin and this repository's newest release each week. When the pin is behind, it runs the sibling's `.lokf/scripts/knowledge-sync.sh` and opens one pull request with the diff: the copies, the pin, and the changelog entry under `## [Unreleased]` and `### Security`. `publish.yml` asks the siblings named in the `KNOWLEDGE_SYNC_HOSTS` repository variable to do so as soon as the tag exists, with the `KNOWLEDGE_SYNC_DISPATCH_TOKEN` secret. The sidecar's [automation.md](../skills/ktl-sidecar/references/automation.md#knowledge-syncyaml-keeping-the-sidecar-current) says what each sibling sets up.

To open the pull requests yourself on the day of a release, run `scripts/sync-sidecar.sh --pr <tag> <sibling>...` from this repository once the tag is on origin. It runs that tag's copy of `knowledge-sync.sh` in each sibling, on a branch of its own, `sync-<tag>`, from origin's default branch; a sibling with uncommitted changes is skipped. Without `--pr`, `--push` or `--commit` it leaves the sync uncommitted on the branch, with the commit command printed, and the diff is the review. Once the pull requests are merged, `scripts/sync-sidecar.sh --finish <tag> <sibling>...` puts each sibling back on its default branch, brings it up to date and removes the branch. A release that touched neither the templates nor the librarian skill needs no sync, and both say so.

## What the repository settings mean for you

Three settings explain what a pull request waits on, or refuses, in every one of these repositories:

- **Changes reach `main` by pull request, but no ruleset enforces it.** A ruleset that requires pull requests, or passing status checks, would also reject the release job's own push of the promoted changelog, and `github-actions[bot]` cannot be put on a ruleset's bypass list. So open a pull request anyway, and treat a red check as yours to fix: CI runs on every pull request and is read before merge, but it is not what blocks one.
- **"Require signed commits" as a branch rule is off, and must stay off.** A commit made inside a runner is unsigned: GitHub only auto-signs commits made through the web UI or API. So the rule would reject the release job's promotion commit and break every release.
- **Sign your own commits anyway.** It is required only for a pull request that records a `human:` confirmation in a knowledge bundle, and worth doing on all of them: [Signing your commits](signing-commits.md).
