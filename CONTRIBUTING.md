# Contributing to Knowledge Trust Ladder

*This file is a checklist, not a design log. Each rule is a line or two that links to where its reasoning lives: a code comment, a workflow header, or a page under `docs/`. `bash scripts/validate-repository.sh` holds the file to a word budget so it stays that way.*

Thanks for your interest in improving `knowledge-trust-ladder`.

## Development setup

There is no build step: the skills are Markdown, YAML and shell.

```bash
git clone https://github.com/noelmcloughlin/knowledge-trust-ladder.git
cd knowledge-trust-ladder
bash scripts/validate-repository.sh
```

To try a change end-to-end before publishing, install from your local clone instead of GitHub:

```bash
gh skill install ./knowledge-trust-ladder ktl-sidecar --from-local
# or:
npx skills add ./knowledge-trust-ladder --skill ktl-sidecar
```

## Layout

| Path | Responsibility |
| --- | --- |
| `skills/ktl-sidecar/SKILL.md` | One-shot bootstrap: creates `.lokf/` from `templates/`. Router only; its `references/` carry the portability and automation detail. |
| `skills/ktl-sidecar/templates/` | Every file the sidecar writes, copied verbatim, never inlined into `SKILL.md`. |
| `skills/ktl-librarian/SKILL.md` | Day to day: scrape, build, audit and hand off `.lokf/` concepts. Facts, never verdicts. |
| `skills/ktl-curator/SKILL.md` | A human curator's assistant: the trust report, and the review session that records a person's Confirm / Wrong / Retire / Later. Verdicts, never facts. |
| `skills/ktl-docent/SKILL.md` | The reader's side: answers from the bundle with each concept's trust label, and records misses in `.lokf/feedback.md`. Read-only on the bundle. |
| `skills/*/references/*.md` | Detail loaded only when the router points to it, which keeps each `SKILL.md` small. |
| `scripts/` | The repository contract CI runs on every PR. `validate-repository.sh` is the entry point and runs the layout tests; `smoke-test-install.sh` installs all four skills into a throwaway repo. |

[docs/repository-layout.md](docs/repository-layout.md) shows the whole tree, workflows and docs included.

## Before opening a pull request

- Run `bash scripts/validate-repository.sh`. It names each check as it runs, and CI runs the same script plus ShellCheck, `actionlint`, markdownlint, lychee and codespell.
- Run `gh skill publish --dry-run` if you have the GitHub CLI: the Agent Skills spec check `validate.yml` runs.
- If a change alters what a skill *does*, not just its wording, add a line or two under `## [Unreleased]` in `CHANGELOG.md`. The reasoning belongs beside the code.
- Files here are deep-linked from the sibling repositories, whose link checks follow those URLs for real; check 9 lists the paths. Move one only together with their links, and when a change *there* needs something new *here*, land this side first.
- Copy a change under `skills/ktl-sidecar/templates/` over this repository's own copy in the same pull request. Check 11 names the pairs, and `knowledge-librarian.yaml` is the one exception.
- When the commits would release, the pull request title carries the releasing type too (`feat:`, `fix:`, `security:`): a squash merge takes its subject from the title, and the `plan` job refuses a mismatch.
- Dependabot bumps the pinned action SHAs, and CI fails an action that is not pinned to a commit.
- Sign a pull request that records a `human:` confirmation, with GPG or SSH ([signing your commits](docs/signing-commits.md)). A repository running the forge-free gate also carries your public key under `.lokf/curators/`, landed in its own pull request first. The same page says how to export it.
- The PR template's checklist is the short form of this list.

## Editing scope

This repository packages and distributes the four skills. It does not second-guess their operational content on its own. A change to what an agent should actually *do* (a new Golden Rule interpretation, a different sidecar step, a new curator verb) needs its *why* in the pull request. It must also keep the role boundary intact: the librarian derives facts from the repository and never vouches for them, and the curator records a person's verdicts and never derives facts.

## Code of conduct

Participation here is covered by the [Contributor Covenant](CODE_OF_CONDUCT.md), the same one the sibling LOKF repositories use.

## Using AI tools

AI assistance is welcome; these skills exist for agents to run. You are still the author of whatever you submit, responsible for understanding and defending it in review, and an agent may not take part in discussion on your behalf. The full rules are in [AI_COVENANT.md](AI_COVENANT.md).

## Releasing (maintainers)

Commits typed with [Conventional Commits](https://www.conventionalcommits.org/) decide the version, and `## [Unreleased]` is the release note. On a merge to `main`, [`semantic-release.yml`](.github/workflows/semantic-release.yml) promotes the changelog and commits it, but never tags. A maintainer then runs [`publish.yml`](.github/workflows/publish.yml) by hand with the version to ship, typed **with** its `v`, and the workflow cross-checks it against the promoted changelog before anything reaches the registry. All four skills ship together under that one tag. After a release that changes a template, copy it into the sibling repositories from that tag; moving their `TRUST_LADDER_SKILLS_REF` changes only the skill their scheduled run installs. [How the LOKF repositories release](docs/releasing.md) has the whole pipeline and the repository settings it depends on. [Signing your commits](docs/signing-commits.md) is required only for a pull request that records a `human:` confirmation. A releasing merge here almost always needs a same-day follow-up bumping the scaffolding template's own skills pin: [why, and the fix](docs/releasing.md#after-a-releasing-merge-to-knowledge-trust-ladder-expect-one-follow-up).
