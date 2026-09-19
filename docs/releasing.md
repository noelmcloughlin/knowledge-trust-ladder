# How the three repositories release

The three repositories - [`knowledge-trust-ladder`](https://github.com/noelmcloughlin/knowledge-trust-ladder), [LOKF Registrar](https://github.com/noelmcloughlin/obsidian-lokf-registrar), and the [LOKF Curator](https://github.com/noelmcloughlin/obsidian-lokf-curator) - release the same way, from the same pinned [semantic-release](https://semantic-release.gitbook.io/) tool, run by each repository's `semantic-release.yml`. This page is the shared part. Each workflow's own header comment carries that repository's detail and the reasons behind it.

## The version is computed, you write commit message

Nobody picks a version number. Commits typed with [Conventional Commits](https://www.conventionalcommits.org/) decide it:

| Commit type | Release |
| --- | --- |
| `feat:` | minor |
| `fix:`, `security:` | patch |
| `BREAKING CHANGE:` in a footer, or `!` after the type | major |
| `docs:`, `chore:`, `refactor:`, `style:`, `test:`, `ci:` | none: the change merges, releases nothing, and its changelog entries ship with the next release that does |

Type the commit for what the change *is*. A behaviour change is a `feat:` even when most of the diff is prose. If a pull request should release and its commits are typed too quietly, squash-merge it and give the squash commit the right type. The reverse trap is the common one: a squash merge takes its subject from the pull request *title*, and GitHub's default title is the branch name in words, with no type, so a typed `fix:` commit reaches `main` as "Fix the thing (#46)" and releases nothing. In `knowledge-trust-ladder` the `plan` job refuses a pull request whose commits would release but whose title would not; type the title like a commit. The workflow listens for `edited` pull requests as well as pushes, so retitling re-runs the check on its own.

The release note is `CHANGELOG.md`'s `## [Unreleased]` section, written as you go: a line or two per change, with the detail left to the code's comments. The pipeline releases only what has already been written up. `changelog-release.mjs check` refuses an empty section; the `plan` job runs it directly, not only inside the dry run, because semantic-release skips its own plugins' hooks - including this one - on a pull-request event, so a forgotten entry fails the pull request rather than the release. It runs only when the pull request's own commits would release, so a `chore:`, `docs:` or `ci:` pull request - a Dependabot bump among them - is not asked for notes it was never going to ship.

## What happens on a merge to `main`

1. `semantic-release` computes the next version from the commits since the last release, and stops if none warrant one.
2. `changelog-release.mjs check` refuses to proceed if `## [Unreleased]` is empty.
3. That section is retitled `## [X.Y.Z] - YYYY-MM-DD`, a fresh empty `## [Unreleased]` is inserted above it, and the result is committed to `main` - unless the top released section already carries that exact version with no matching tag, in which case the new entries fold into it by subsection instead of adding a second heading. That case is possible only in `knowledge-trust-ladder`, where tagging is a separate, later step (below): a second qualifying merge before a maintainer runs `publish.yml` computes the same next version again, since it is still derived from the last *tag*.
4. From here the repositories differ:

| Repository | Tag | Then |
| --- | --- | --- |
| `knowledge-trust-ladder` | None from this workflow. `gh skill publish` is the one tag creator, so a maintainer runs `publish.yml` by hand with the version to ship, typed with its `v` (`v0.16.0`); the workflow cross-checks it against the promoted changelog first. Tags carry the `v`, changelog headings never do. | The four skills publish to the registry under that one tag. |
| LOKF Registrar, LOKF Curator | Bare `X.Y.Z`, Obsidian's convention, after `package.json`, `manifest.json` and `versions.json` are bumped as `npm version` would. | `release.yml` builds, attests provenance and opens a **draft** release carrying `main.js`, `manifest.json` and `styles.css`; a maintainer reviews and publishes it. A hand-pushed tag takes the same path. |

Everything from step 3 on runs behind the `release` GitHub Environment. **Configure required reviewers on it once, in each repository's Settings → Environments**, or a qualifying merge ships unattended; creating the environment does not do that for you.

## After a releasing merge to `knowledge-trust-ladder`, expect one follow-up

The scaffolding template pins its own `TRUST_LADDER_SKILLS_REF` to the release it ships in - so every time a `feat:`, `fix:` or `security:` merge lands, the template that merged *is already one release behind itself*: the changelog heading exists (step 3, above) but its tag does not yet, so the newest pin a host could actually clone is the release before it. `validate-repository.sh`'s check 15 catches this and fails `publish.yml` with the version to pin. The fix is always the same one-line commit - bump `TRUST_LADDER_SKILLS_REF` to the newest tag that exists - and it folds into the same pending release rather than cutting another one (the step 3 rule above). This is expected, not a sign anything is broken; budget for it as the last step of every release that touches the template.

## What the repository settings mean for you

Three settings explain what a pull request waits on, or refuses, in every one of these repositories:

- **Changes reach `main` by pull request, but no ruleset enforces it.** A ruleset that requires pull requests, or passing status checks, also rejects the release job's own push of the promoted changelog, and `github-actions[bot]` cannot be put on a ruleset's bypass list, which accepts roles, teams, GitHub Apps and Dependabot. A ruleset may still block deletion and force-pushes and require linear history. So the pull-request discipline is a convention held to by the maintainer: open one anyway. CI runs on every pull request and is read before merge; it is just not what blocks one, so treat a red check as yours to fix.
- **"Require signed commits" as a branch rule is deliberately off, and must stay off.** A commit made inside a runner is unsigned - GitHub only auto-signs commits made through the web UI or API - so the rule would reject the release job's promotion commit and break every release.
- **Sign your own commits anyway.** It is required only for a pull request that records a `human:` confirmation in a knowledge bundle, and worth doing on all of them: [Signing your commits](signing-commits.md).
