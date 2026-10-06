---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/contributing
title: Contributing
description: "How to work on the skills: no build step, the local checks to run before opening a pull request, the role boundary a change must respect, and which pages now hold the release and signing detail."
genre: how-to
resource: CONTRIBUTING.md
generated:
  by: process:ktl-librarian
  at: "2026-10-06T11:10:52Z"
status: draft
references:
- https://knowledge-trust-ladder.example/knowledge/playbooks/repository-validation
- https://knowledge-trust-ladder.example/knowledge/playbooks/releasing
- https://knowledge-trust-ladder.example/knowledge/policies/ai-covenant
- https://knowledge-trust-ladder.example/knowledge/policies/code-of-conduct
sources:
- resource: CONTRIBUTING.md
- resource: docs/signing-commits.md
verified:
- by: process:ktl-librarian
  at: "2026-10-06T11:10:52Z"
---

# Overview

`CONTRIBUTING.md` is a checklist, not a design log. Each rule is a line or two linking to where its reasoning is written: a code comment, a workflow header, or a page under `docs/`. `scripts/validate-repository.sh` holds it to a word budget so it stays that way.

There is no build step: the skills are Markdown, YAML, shell and one Python script. The repository packages and distributes the four skills and the `ktl-prose` helper, and all five are released together under one tag. Clone, then run `bash scripts/validate-repository.sh`. To try a change end-to-end before publishing, install from the local clone (`gh skill install ./knowledge-trust-ladder <skill> --from-local`, or `npx skills add ./knowledge-trust-ladder --skill <skill>`).

Before a pull request:

- run `validate-repository.sh`, which names each check as it runs (CI runs the same script plus ShellCheck, `actionlint`, markdownlint, lychee and codespell);
- run `gh skill publish --dry-run` if the GitHub CLI is present;
- add a line or two under `CHANGELOG.md`'s `[Unreleased]` when behaviour changes. The reasoning belongs beside the code, not in the changelog entry.

Files here are deep-linked from the sibling repositories (KTL Registrar, and the KTL Curator), whose own link checks follow those URLs for real. `validate-repository.sh` check 9 lists the paths. Move one only together with its links, and when a change there needs something new here, merge this side first.

A change under `skills/ktl-sidecar/templates/` is copied over each of this repository's copies, ktl-docent's included, in the same pull request. Checks 11 and 11a name the pairs and hold each byte-identical, `knowledge-librarian.yaml` apart from its skills pin, which the release commit moves in the template only. When the commits would release, the pull request title carries the releasing type too (`feat:`, `fix:`, `security:`), because a squash merge takes its subject from the title and the `plan` job refuses a mismatch. Pinned action SHAs are bumped by Dependabot, and CI fails an action that floats on a tag or branch instead of a commit. The pull request template's checklist is the short form of this list.

A change to what an agent should actually *do* needs its *why* in the pull request, and must keep the role boundary intact:

- the librarian derives facts and never vouches for them;
- the curator records verdicts and never derives facts;
- `ktl-prose` changes wording and never a fact, a frontmatter byte or a concept a person vouched for.

Participation is covered by the Contributor Covenant, shared with the sibling KTL repositories ([code of conduct](../policies/code-of-conduct.md)). AI assistance is welcome, since these skills exist for agents to run. But the person submitting is still the author, responsible for defending the change in review. An agent may not take part in discussion on their behalf ([the AI covenant](../policies/ai-covenant.md)).

Releasing is maintainer-gated. Conventional Commits decide the version, and `[Unreleased]` is the release note. A merge to `main` promotes the changelog but never tags, and a maintainer runs `publish.yml` by hand ([releasing](releasing.md)).

After a release that changes a template or `skills/ktl-librarian/`, and once the tag is on origin, `scripts/sync-sidecar.sh <tag> obsidian-ktl-curator obsidian-ktl-registrar`:

- copies that release's templates over each sibling's copies;
- moves each sibling's `TRUST_LADDER_SKILLS_REF` to the same tag, and `TRUST_LADDER_SKILLS_SHA` to the commit that tag names;
- runs the sidecar's checks there;
- leaves the diff for a person to review and commit.

The pin and the copies move together because, once a sibling turns on its scheduled librarian, the pin decides which instructions run unattended.

Signing a commit is required only for a pull request that records a `human:` confirmation in a knowledge bundle (`docs/signing-commits.md`). A repository running the forge-free gate also needs the signer's public key under `.lokf/curators/`, added first in a pull request of its own.
