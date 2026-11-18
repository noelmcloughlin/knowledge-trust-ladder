# How the three repositories release

This page is for contributors and maintainers of [`knowledge-trust-ladder`](https://github.com/noelmcloughlin/knowledge-trust-ladder), [KTL Registrar](https://github.com/noelmcloughlin/obsidian-ktl-registrar) and [KTL Curator](https://github.com/noelmcloughlin/obsidian-ktl-curator), which release the same way. Each repository's `semantic-release.yml` runs the same pinned [semantic-release](https://semantic-release.gitbook.io/) tool. Each workflow's own header comment carries that repository's detail and the reasons behind it.

## The version is computed; you write the commit message

Nobody picks a version number. Commits typed with [Conventional Commits](https://www.conventionalcommits.org/) decide it:

| Commit type | Release |
| --- | --- |
| `feat:` | minor |
| `fix:`, `perf:`, `security:` | patch |
| A revert as `git revert` writes it: a subject that starts `Revert`, and a body that says `This reverts commit <hash>.` | patch, unless the commit it reverts is still unreleased: then neither counts |
| `BREAKING CHANGE:` in a footer, or `!` after the type | major |
| `docs:`, `chore:`, `refactor:`, `style:`, `test:`, `build:`, `ci:`, and a `revert:` typed by hand without that sentence | none: the change merges, releases nothing, and its changelog entries wait for the next release that does |

Type the commit for what the change *is*. A behaviour change is a `feat:` even when most of the diff is prose. If a pull request should release and none of its commits has a type that releases, squash-merge it and give the squash commit the right type.

The reverse trap is a squash merge that takes its subject from the pull request *title*, which GitHub defaults to the branch name in words, with no type. So a typed `fix:` commit reaches `main` as "Fix the thing (#46)" and releases nothing. The `plan` job refuses a pull request whose commits would release but whose title would not. Type the title like a commit, and leave a revert's title as GitHub writes it, `Revert "..."`. The workflow runs on `edited` pull requests as well as on pushes, so retitling re-runs the check on its own.

The release note is `CHANGELOG.md`'s `## [Unreleased]` section, written as you go: a line or two per change, with the detail left to the code's comments. The pipeline releases only what has already been written up.

`changelog-release.mjs check` refuses an empty section. The `plan` job runs it on each pull request, so a forgotten entry fails the pull request rather than the release. The check runs only when the pull request's own commits would release, so a `chore:`, `docs:` or `ci:` pull request, or a Dependabot bump, is not asked for notes.

## What happens on a merge to `main`

1. `semantic-release` computes the next version from the commits since the last release, and stops if none warrant one.
2. `changelog-release.mjs check` refuses to proceed if `## [Unreleased]` is empty.
3. That section is retitled `## [X.Y.Z] - YYYY-MM-DD`, a fresh empty `## [Unreleased]` is inserted above it, and the result is committed to `main`. In `knowledge-trust-ladder`, tagging is a separate later step. A second qualifying merge before `publish.yml` runs then computes the same version again, and its entries merge into the still-untagged section, which takes the new version and date.
4. From this step on, the repositories differ:

| Repository | Tag | Then |
| --- | --- | --- |
| `knowledge-trust-ladder` | None from this workflow. `gh skill publish` is the one tag creator, so a maintainer runs `publish.yml` by hand on `main` with the version to release, typed with its `v` (`v0.16.0`); the workflow cross-checks it against the promoted changelog first. `gh skill publish` tags the head of `main`, so the workflow publishes only while `main` is still the commit it checked: after a merge during the run, run it again. Tags carry the `v`, changelog headings never do. | The six skills publish to the registry under that one tag. `publish.yml` then dispatches `knowledge-release.yaml`, which attaches the bundle to the release as `knowledge-vX.Y.Z-knowledge-trust-ladder.zip` when it changed since the last release that carries one, and `pypi.yml`, which builds the `ktl` package from the tag and uploads it to PyPI as version X.Y.Z. |
| KTL Registrar, KTL Curator | Bare `X.Y.Z`, Obsidian's convention, after `package.json`, `manifest.json` and `versions.json` are bumped as `npm version` would. | `release.yml` builds, attests provenance and opens a **draft** release carrying `main.js`, `manifest.json` and `styles.css`; a maintainer reviews and publishes it. A hand-pushed tag takes the same path. Publishing the draft is a person's event, not the token's, so it starts `knowledge-release.yaml` once `KNOWLEDGE_RELEASE_ENABLED` is `true` there; no dispatch is needed. |

Everything from step 3 on runs behind the `release` GitHub Environment. Required reviewers on it wait until releases have downstream users, so until then a qualifying merge is released unattended. Then add them in each repository's Settings → Environments, or with `ktl gh apply --recommended`, which adds you; `ktl gh check --strict` names a repository without one.

## After a releasing merge to `knowledge-trust-ladder`, what follows

The sidecar's `templates/pyproject.toml` pins `ktl` one release behind. When `semantic-release.yml` promotes the changelog, the new heading exists but its tag does not yet, so the release commit moves the pin to the newest tag, whose package `publish.yml` put on PyPI.

Check 15 of `validate-repository.sh` requires the pin to name one of the two newest releases, and that tag to carry `skills/ktl-librarian` and the sync manifest. Never bump the pin by hand: that commit triggers a needless release, and the next promotion moves the pin anyway.

The sibling repositories carry byte-identical copies of the templates and their own pin. Only the first line of `.lokf/justfile`, which names the host, and its `schema :=` line are a sibling's own. The copies and the pin move together from one tag, because the skill a tag installs is written against the wrapper, gate and preflight that tag includes. Once a sibling turns on its scheduled librarian, the pin decides which agent instructions run unattended.

Each sibling keeps itself current. Its `knowledge-sync.yaml` reads the `ktl` pin in `.lokf/pyproject.toml` and asks its package index for the newest release each week. When the pin is behind, it runs the sibling's own `.lokf/scripts/knowledge-sync.sh`, which reads what to copy from the release's `templates/knowledge-sync.manifest`, and opens one pull request with the diff: the copies, the pin, and the changelog entry under `## [Unreleased]` and `### Security`. The sync keeps one pull request open: a later week's run refreshes it to the newest release until it is merged.

`publish.yml` asks the siblings named in the `KNOWLEDGE_SYNC_HOSTS` repository variable to sync once the release's `ktl` package is on PyPI, with the `KNOWLEDGE_SYNC_DISPATCH_TOKEN` secret; after 30 minutes without it, it asks nobody. The variable lists `owner/repo` names, and `false` asks nobody. A fine-grained token reaches one owner's repositories alone, so a host under another owner is reported and syncs on its schedule. `ktl gh plan` names a host that was renamed. The sidecar's [automation.md](../skills/ktl-sidecar/references/automation.md#knowledge-syncyaml-keeping-the-sidecar-current) says what each sibling sets up.

A new template goes in the manifest and in ktl-sidecar's Step 5 table, and nowhere else: the preflight and contract check 11 read the manifest.

To open a sibling's pull request on the day of a release, once its `ktl` package is on PyPI, start the sibling's `knowledge-sync.yaml` by hand with the tag, or run `.lokf/scripts/knowledge-sync.sh --pr <tag>` in a clone of it. A release that touched neither the templates nor the librarian skill needs no sync, and the workflow and the script both say so.

## The ktl package on PyPI

`pypi.yml` builds two packages from the tag: `ktl`, which carries the skills, and `knowledge-trust-ladder`, which holds no code and installs `ktl` at the same version under the repository's name. The build backend comes at the hashes `.pypi/requirements.txt` holds. The workflow checks that the files carry the tag's version, builds them a second time and checks the bytes match, and installs the wheels with no index and the skills from them. It uploads only when the repository variable `PYPI_RELEASE_ENABLED` says where: `testpypi` for TestPyPI, `true` for PyPI. Unset, a release builds and checks the packages and uploads nothing. After an upload to PyPI, it attaches a `.sha256` file for each package file to the GitHub release, and the files' signed provenance as `provenance-<tag>-packages.intoto.jsonl`.

Before the first upload to each index, a maintainer does three things once:

1. Creates the Environment the upload names, `testpypi` or `pypi`, limited to tags matching `v*`. A required reviewer on it is recommended: [Repository hardening](threat-model.md#repository-hardening) says why. It can wait until releases have downstream users, as the reviewer on `release` does. `ktl gh apply --recommended` adds you once the Environment exists, and `ktl gh check --strict` names one without a reviewer.
2. Adds a pending publisher on that index for the project `ktl`, naming owner `noelmcloughlin`, repository `knowledge-trust-ladder`, workflow `pypi.yml` and that Environment.
3. Sets `PYPI_RELEASE_ENABLED`, `testpypi` first, and `true` once a TestPyPI release installs.

An index holds only one pending publisher for those details at a time, so the first upload creates `ktl` and then fails at `knowledge-trust-ladder`. The maintainer then adds a pending publisher for `knowledge-trust-ladder` with the same details and runs the failed job again.

If an upload fails after the tag exists, run the workflow again on the tag: `gh workflow run pypi.yml --ref vX.Y.Z -f tag=vX.Y.Z`. A file the index already holds is skipped, so a repeated run finishes a partial upload. A bad file on PyPI is yanked with a reason, never deleted, since PyPI never takes the same file name twice.

Anyone can check a release's files against the tag. On Linux or macOS, rebuild them with the workflow's command and compare the result with PyPI's file, and with the release's `.sha256` files:

```bash
git clone --branch vX.Y.Z https://github.com/noelmcloughlin/knowledge-trust-ladder ktl-check && cd ktl-check
uv build --python 3.12 --build-constraints .pypi/requirements.txt --require-hashes --out-dir rebuilt
python3 -m pip download --no-deps --dest from-pypi ktl==X.Y.Z
cmp rebuilt/ktl-X.Y.Z-py3-none-any.whl from-pypi/ktl-X.Y.Z-py3-none-any.whl
```

## What the repository settings mean for you

Three settings explain what a pull request waits on, or refuses, in every one of these repositories:

- **Changes reach `main` by pull request, but no ruleset enforces it.** A ruleset that requires pull requests, or passing status checks, would also reject the release job's own push of the promoted changelog, and `github-actions[bot]` cannot be put on a ruleset's bypass list. So open a pull request anyway, and treat a red check as yours to fix: CI runs on every pull request and is read before merge, but it is not what blocks one.
- **"Require signed commits" as a branch rule is off, and must stay off.** A commit made inside a runner is unsigned: GitHub only auto-signs commits made through the web UI or API. So the rule would reject the release job's promotion commit and break every release.
- **Sign your own commits anyway.** It is required only for a pull request that records a `human:` confirmation in a knowledge bundle, and worth doing on all of them: [Signing your commits](signing-commits.md).
