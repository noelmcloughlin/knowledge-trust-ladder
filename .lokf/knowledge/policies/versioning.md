---
type: Policy
id: https://lokf-agent-skills.example/knowledge/policies/versioning
title: Versioning policy
description: One repository-level semantic version covering all four skills, released together under a single tag, with patch/minor/major computed from Conventional Commits rather than hand-picked.
genre: reference
resource: docs/releasing.md
generated:
  by: process:lokf-librarian
  at: "2026-09-14T16:00:00Z"
status: draft
about:
  - https://lokf-agent-skills.example/knowledge/playbooks/releasing
verified:
- by: process:lokf-librarian
  at: "2026-09-17T14:02:11Z"
- by: human:noelmcloughlin
  at: "2026-09-10T00:00:00Z"
stale_after: 2027-09-10
---

# Overview

`vMAJOR.MINOR.PATCH`. As of 2026-09-14 the bump is computed from
[Conventional Commits](https://www.conventionalcommits.org/), not hand-picked
or defined by effect on behaviour: `feat:` is minor; `fix:` and `security:`
are patch; a `BREAKING CHANGE:` footer or `!` after the type is major;
`docs:`, `chore:`, `refactor:`, `style:`, `test:` and `ci:` release nothing -
the change merges and its changelog entries ship with the next release that
does. This superseded the previous qualitative definition (patch/minor/major
by effect on expected behaviour), which `CONTRIBUTING.md` carried until this
date and no longer states anywhere in the repository.

All four skills ship from one tag rather than versioning independently,
because they are designed as a set - the librarian hands off to the curator,
the docent records feedback the librarian consumes - and a consumer pinning
them to different releases could pair skills that disagree about the
frontmatter contract between them.

One asymmetry to know: tags carry a `v` prefix (`v0.16.0`), and `publish.yml`
refuses a version typed without it, while `CHANGELOG.md` headings never do
(`## [0.16.0]`); the workflow's cross-check strips the `v` before comparing
the two.

## Open questions

- 2026-09-18, process:lokf-curator: unauthenticated session, no `gh` login to attribute to a person - two claims aren't backed by the cited `resource` (`docs/releasing.md`) - (1) "superseded the previous qualitative definition... which CONTRIBUTING.md carried until this date and no longer states anywhere in the repository" (not verified true or false, just uncited here); (2) the "designed as a set... disagree about the frontmatter contract between them" reasoning for one shared tag (README.md states the "agrees with itself" conclusion but not this specific reasoning). Fourth concept this session with the same citation gap (see also lokf-librarian skill, Why a registrar role, Security policy) - worth raising with lokf-librarian as a general pattern rather than fixing per-concept.
