---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/contributing
title: Contributing
description: "How to work on the skills: no build step but the website's, the local checks to run before opening a pull request, the role boundary a change must respect, and which pages now hold the release and signing detail."
genre: how-to
resource: CONTRIBUTING.md
generated:
  by: process:ktl-librarian
  at: "2026-10-19T12:30:15Z"
status: draft
references:
  - https://w3id.org/ktl/knowledge/playbooks/repository-validation
  - https://w3id.org/ktl/knowledge/playbooks/releasing
  - https://w3id.org/ktl/knowledge/policies/ai-covenant
  - https://w3id.org/ktl/knowledge/policies/code-of-conduct
sources:
  - resource: CONTRIBUTING.md
  - resource: docs/signing-commits.md
verified:
  - by: process:ktl-librarian
    at: "2026-10-16T23:58:13Z"
---

# Overview

`CONTRIBUTING.md` is a checklist, not a design log. Each rule is a line or two linking to where its reasoning is written: a code comment, a workflow header, or a page under `docs/`. `scripts/validate-repository.sh` holds it to a word budget so it stays that way.

The skills need no build step: they are Markdown, YAML, shell and Python, and only `website/` builds (`npm run build`). The repository packages and distributes the four skills and two helpers, `ktl-prose` and `ktl-website`, and all six are released together under one tag. Clone, then run `bash scripts/validate-repository.sh`. The sidecar scripts' behavioural tests are under `tests/`, and `conftest.py` there says how to run them. To try a change end-to-end before publishing, install from the local clone (`gh skill install ./knowledge-trust-ladder <skill> --from-local`, or `npx skills add ./knowledge-trust-ladder --skill <skill>`).

Before a pull request:

- run `bash scripts/validate-repository.sh` and `pytest` (CI runs both plus ShellCheck, `actionlint`, markdownlint, lychee and codespell);
- run `gh skill publish --dry-run` if the GitHub CLI is present;
- add a line or two under `CHANGELOG.md`'s `[Unreleased]` when behaviour changes. The reasoning belongs beside the code, not in the changelog entry.

The sibling repositories link deep into files here, and their own link checks follow those URLs. `validate-repository.sh` check 9 lists the paths. Move one only together with its links, and when a change there needs something new here, merge this side first.

A change under a skill's `templates/` is copied over each of this repository's copies, ktl-docent's included, in the same pull request. Checks 11, 11a and 11w name the pairs and hold each byte-identical. The one exception is the skills pin in `knowledge-librarian.yaml`, which the release commit moves in the template only.

When the commits would release, the pull request title carries the releasing type too (`feat:`, `fix:`, `security:`). A squash merge takes its subject from the title, and the `plan` job refuses a mismatch. Pinned action SHAs are bumped by Dependabot, and CI fails an action that floats on a tag or branch instead of a commit. The pull request template's checklist is the short form of this list.

A change to what an agent should actually *do* needs its *why* in the pull request, and must keep the role boundary intact:

- the librarian derives facts and never vouches for them;
- the curator records verdicts and never derives facts;
- `ktl-prose` changes wording and never a fact, a frontmatter byte or a concept a person vouched for;
- `ktl-website` presents the bundle and never writes it.

Participation is covered by the Contributor Covenant, shared with the sibling KTL repositories ([code of conduct](../policies/code-of-conduct.md)). AI assistance is welcome, since these skills exist for agents to run. But the person submitting is still the author, responsible for defending the change in review. An agent may not take part in discussion on their behalf ([the AI covenant](../policies/ai-covenant.md)).

Releasing is maintainer-gated. Conventional Commits decide the version, and `[Unreleased]` is the release note. A merge to `main` promotes the changelog but never tags, and a maintainer runs `publish.yml` by hand ([releasing](releasing.md)).

After a release that changes a template or `skills/ktl-librarian/`, each sibling's `knowledge-sync.yaml` opens a pull request that moves its copies and pin to the release within a week. To open those pull requests at once, a maintainer runs `scripts/sync-sidecar.sh --pr <tag> ../obsidian-ktl-curator ../obsidian-ktl-registrar` once the tag is on origin, and `--finish <tag>` once they are merged.

The pin and the copies move together because, once a sibling turns on its scheduled librarian, the pin decides which instructions run unattended.

Signing a commit is required only for a pull request that records a `human:` confirmation in a knowledge bundle (`docs/signing-commits.md`). A repository running the forge-free gate also needs the signer's public key under `.lokf/curators/`, added first in a pull request of its own.
