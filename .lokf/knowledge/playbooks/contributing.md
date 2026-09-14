---
type: Playbook
id: https://lokf-agent-skills.example/knowledge/playbooks/contributing
title: Contributing
description: How to work on the skills - no build step, the local checks to run before opening a pull request, the role boundary a change must respect, and where the release and signing detail now lives.
genre: how-to
resource: CONTRIBUTING.md
generated:
  by: process:lokf-librarian
  at: "2026-09-14T16:00:00Z"
status: draft
references:
  - https://lokf-agent-skills.example/knowledge/playbooks/repository-validation
  - https://lokf-agent-skills.example/knowledge/playbooks/releasing
  - https://lokf-agent-skills.example/knowledge/policies/ai-covenant
  - https://lokf-agent-skills.example/knowledge/policies/code-of-conduct
verified:
- by: process:lokf-librarian
  at: "2026-09-14T16:00:00Z"
---

# Overview

`CONTRIBUTING.md` is now a checklist, not a design log (rewritten
2026-09-14): each rule is a line or two linking to where its reasoning
lives - a code comment, a workflow header, or a page under `docs/` - and
`scripts/validate-repository.sh` holds it to a 1000-word budget so it stays
that way.

There is no build step: the skills are Markdown, YAML, and shell. Clone,
then run `bash scripts/validate-repository.sh`. To try a change end-to-end
before publishing, install from the local clone (`gh skill install
./lokf-agent-skills <skill> --from-local`, or `npx skills add
./lokf-agent-skills --skill <skill>`).

Before a pull request: `validate-repository.sh` (names each check as it
runs; CI runs the same script plus ShellCheck, `actionlint`, markdownlint,
lychee and codespell), `gh skill publish --dry-run` if the GitHub CLI is
present, and a line or two under `CHANGELOG.md`'s `[Unreleased]` when
behaviour changes - the reasoning belongs beside the code, not in the
changelog entry. Files here are deep-linked from the sibling repositories
(LOKF Registrar, and the LOKF Curator), whose own link checks
follow those URLs for real - `validate-repository.sh` check 9 lists the
paths; move one only together with its links, landing this side first.
Pinned action SHAs are bumped by Dependabot, and CI now fails an action that
floats on a tag or branch instead of a commit. The PR template's checklist
is the short form of this list.

A change to what an agent actually *does* must keep the role boundary
intact - the librarian derives facts and never vouches for them; the
curator records verdicts and never derives facts.

Participation is covered by the Contributor Covenant, shared with the
sibling LOKF repositories ([code of conduct](../policies/code-of-conduct.md)).
AI assistance is welcome - these skills exist for agents to run - but the
person submitting is still the author, responsible for defending the change
in review, and an agent may not take part in discussion on their behalf
([the AI covenant](../policies/ai-covenant.md)).

Releasing is maintainer-gated: Conventional Commits decide the version and
`[Unreleased]` is the release note; a merge to `main` promotes the
changelog but never tags, and a maintainer runs `publish.yml` by hand
([releasing](releasing.md)). Signing a commit is required only for a pull
request that records a `human:` confirmation in a knowledge bundle - the
detail moved out of this file to `docs/signing-commits.md`.
