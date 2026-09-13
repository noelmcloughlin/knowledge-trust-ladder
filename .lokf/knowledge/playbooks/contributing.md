---
type: Playbook
id: https://lokf-agent-skills.example/knowledge/playbooks/contributing
title: Contributing
description: How to work on the skills - no build step, the local checks to run before opening a pull request, and the role boundary a change must respect.
genre: how-to
resource: CONTRIBUTING.md
generated:
  by: process:lokf-librarian
  at: "2026-09-13T19:00:00Z"
status: draft
references:
  - https://lokf-agent-skills.example/knowledge/playbooks/repository-validation
  - https://lokf-agent-skills.example/knowledge/policies/ai-covenant
  - https://lokf-agent-skills.example/knowledge/policies/code-of-conduct
verified:
- by: process:lokf-librarian
  at: "2026-09-13T19:00:00Z"
---

# Overview

There is no build step: the skills are Markdown, YAML, and one shell script.
Clone, then run `bash scripts/validate-repository.sh`. To try a change
end-to-end before publishing, install from the local clone
(`gh skill install ./lokf-agent-skills <skill> --from-local`, or
`npx skills add ./lokf-agent-skills --skill <skill>`).

Before a pull request: the repository-contract script, `gh skill publish
--dry-run` if the GitHub CLI is present, `shellcheck` on any changed script,
and a `CHANGELOG.md` entry under `[Unreleased]` when behaviour changes.
Workflow changes are linted by `actionlint` in CI.

What a pull request waits on, or does not (recorded 2026-09-13): changes
reach `main` by pull request as a convention the maintainer holds to, not a
ruleset, and required status checks are deliberately off too - both rules
apply to direct pushes and would reject the release job's own `[skip ci]`
promotion commit. CI still runs on every pull request and is read before
merge, so a red check is the contributor's to fix, not a net that catches
it. Signing commits is required only for a pull request that records a
`human:` confirmation ([the registrar gate](../policies/security.md)), and
worth doing on all of them.

The repository is Apache-2.0 licensed. A change to what an agent actually
*does* must keep the role boundary intact - the librarian derives facts and
never vouches for them; the curator records verdicts and never derives facts.
