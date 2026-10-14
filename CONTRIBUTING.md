# Contributing to Knowledge Trust Ladder

*This file is a checklist, not a design log. Each rule is a line or two that links to where its reasoning lives: a code comment, a workflow header, or a page under `docs/`. `bash scripts/validate-repository.sh` fails when the file outgrows its word budget, so it stays that way.*

Thanks for your interest in improving `knowledge-trust-ladder`.

## Development setup

The skills need no build step: they are Markdown, YAML, shell and Python. Only `website/` builds (`npm run build`).

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
| `skills/*/templates/` | Every file a skill writes into a host, copied verbatim, never inlined into `SKILL.md`. |
| `skills/ktl-librarian/SKILL.md` | Day to day: scrape, build, audit and hand off `.lokf/` concepts. Facts, never verdicts. |
| `skills/ktl-curator/SKILL.md` | A human curator's assistant: the trust report, and the review session that records a person's Confirm / Wrong / Retire / Later. Verdicts, never facts. |
| `skills/ktl-docent/SKILL.md` | The reader's side: answers from the bundle with each concept's trust label, and records misses in `.lokf/feedback.md`. Read-only on the bundle. `scripts/` holds its copies of two sidecar scripts. |
| `skills/ktl-prose/SKILL.md` | The librarian's copy editor: rewords a concept body an agent wrote, in plain English, before a person confirms it. Wording, never facts. `scripts/prose-check.py` is its check. |
| `skills/ktl-website/SKILL.md` | Lays `website/` down from `templates/`, this repository's own site (check 11w). |
| `skills/*/references/*.md` | Detail loaded only when the router points to it, which keeps each `SKILL.md` small. |
| `scripts/` | The repository contract CI runs on every pull request: `validate-repository.sh` checks this repository's files; `smoke-test-install.sh` and `smoke-test-website.sh` install the skills and build the site in throwaway repos. |
| `tests/` | The sidecar scripts' behavioural tests; `conftest.py` says how to run them. |

[docs/repository-layout.md](docs/repository-layout.md) shows the whole tree, workflows and docs included.

## Before opening a pull request

- Run `bash scripts/validate-repository.sh` and `pytest`. CI runs both plus ShellCheck, `actionlint`, markdownlint, lychee and codespell.
- Run `gh skill publish --dry-run` if you have the GitHub CLI: the Agent Skills spec check `validate.yml` runs.
- If a change alters what a skill *does*, not just its wording, add a line or two under `## [Unreleased]` in `CHANGELOG.md`. The reasoning belongs beside the code.
- Files here are deep-linked from the sibling repositories, whose link checks follow those URLs; check 9 lists the paths. Move one only together with their links, and when a change *there* needs something new *here*, merge this side first.
- Copy a change under a skill's `templates/` over each of this repository's copies, ktl-docent's included, in the same pull request. Checks 11, 11a and 11w name the pairs and hold each byte-identical, `knowledge-librarian.yaml` apart from its skills pin, which the release commit moves in the template only.
- When the commits would release, the pull request title carries the releasing type too (`feat:`, `fix:`, `security:`): a squash merge takes its subject from the title, and the `plan` job refuses a mismatch.
- Dependabot bumps the pinned action SHAs, and CI fails an action that is not pinned to a commit.
- Sign a pull request that records a `human:` confirmation, with GPG or SSH ([signing your commits](docs/signing-commits.md)). A repository running the forge-free gate also carries your public key under `.lokf/curators/`, added first in a pull request of its own.
- The pull request template's checklist is the short form of this list.

## Editing scope

This repository packages and distributes the four skills and two helpers, `ktl-prose` and `ktl-website`. It does not revise what they tell an agent to do on its own initiative. A change to what an agent should actually *do* (a new Golden Rule interpretation, a different sidecar step, a new curator verb) needs its *why* in the pull request. It must also keep the role boundary intact: the librarian derives facts from the repository and never vouches for them, and the curator records a person's verdicts and never derives facts. `ktl-prose` changes wording, and never a fact, a frontmatter byte or a concept a person vouched for. `ktl-website` presents the bundle, never writing it.

## Code of conduct

Participation here is covered by the [Contributor Covenant](CODE_OF_CONDUCT.md), the same one the sibling KTL repositories use.

## Using AI tools

AI assistance is welcome; these skills exist for agents to run. You remain the author of what you submit and defend it in review yourself, and an agent may not take part in discussion on your behalf; [AI_COVENANT.md](AI_COVENANT.md) has the full rules.

## Releasing (maintainers)

Commits typed with [Conventional Commits](https://www.conventionalcommits.org/) decide the version, and `## [Unreleased]` is the release note. On a merge to `main`, [`semantic-release.yml`](.github/workflows/semantic-release.yml) promotes the changelog and commits it, but never tags. A maintainer then runs [`publish.yml`](.github/workflows/publish.yml) by hand with the version to release, typed **with** its `v`, and the workflow cross-checks it against the promoted changelog before anything reaches the registry. All six skills are released together under that one tag.

After a release that changes a template or `skills/ktl-librarian/`, run `scripts/sync-sidecar.sh <tag> obsidian-ktl-curator obsidian-ktl-registrar` once the tag is on origin. It copies that release's templates over each sibling's copies, moves `TRUST_LADDER_SKILLS_REF` and `TRUST_LADDER_SKILLS_SHA` to that tag and its commit, runs the sidecar's checks there, and leaves the diff for a person to review. The pin and the copies move together, from one tag, because once a sibling turns on its scheduled librarian, the pin decides which instructions run unattended.

[How the three repositories release](docs/releasing.md) has the whole pipeline and the repository settings it depends on. The template's own pin moves by itself at each release: [what follows a releasing merge](docs/releasing.md#after-a-releasing-merge-to-knowledge-trust-ladder-what-follows).
