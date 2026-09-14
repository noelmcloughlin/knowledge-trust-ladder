---
type: Playbook
id: https://lokf-agent-skills.example/knowledge/playbooks/repository-validation
title: Repository validation
description: What CI checks on every pull request and weekly - the repository contract, the Agent Skills spec, shell and workflow linting, the install smoke test, and Markdown/link/spelling checks.
genre: how-to
resource: .github/workflows/validate.yml
generated:
  by: process:lokf-librarian
  at: "2026-09-14T18:00:00Z"
status: draft
references:
  - https://lokf-agent-skills.example/knowledge/references/agent-skills-specification
  - https://lokf-agent-skills.example/knowledge/references/open-skills-cli
  - https://lokf-agent-skills.example/knowledge/playbooks/contributing
verified:
- by: process:lokf-librarian
  at: "2026-09-14T16:00:00Z"
---

# Overview

`validate.yml` runs five jobs on every pull request, every push to `main`,
weekly, and on demand. `validate-skills` runs `scripts/validate-repository.sh` -
eleven numbered checks: exactly four skill directories with a case-correct
`SKILL.md` in each, frontmatter `name` matching its directory, no duplicate
`SKILL.md`, every relative Markdown link under `skills/` resolving (fenced
examples excluded), ShellCheck-clean scripts, every stated LOKF class count
agreeing with `lokf-librarian/SKILL.md` Rule 3 (and with
`lokf-curator/references/trust-fields.md`'s own enumeration), the sidecar
layout tests, the paths the two sibling plugin repositories deep-link into by
URL still existing - and, when those siblings are cloned beside this repo,
that the list of them is complete - `CONTRIBUTING.md` and `SECURITY.md` each
staying under their own word budget (1000 and 900, check 10, extended
2026-09-14 when `SECURITY.md`'s design moved to `docs/threat-model.md`), and
(check 11, added 2026-09-14) this repository's copies
of the registrar gate and both sidecar scripts staying byte-identical to
their templates, with `knowledge-conventions.sh` shown to pass on this
bundle and to fail on a synthetic bundle breaking each rule it checks. Then
`gh skill publish --dry-run` runs.

`lint-scripts` runs ShellCheck on every script; `lint-workflows` runs
`actionlint`, pointed by path at this repository's workflows and at the two
workflow templates that get copied into other repositories (it would
otherwise look only under `.github/workflows/`), and (added 2026-09-14) a check that every `uses:`
in this repository's workflows and those templates names a commit SHA or
image digest rather than a floating tag or branch; `smoke-test` installs all
four skills from the checkout into a throwaway consumer repo via
`scripts/smoke-test-install.sh`; `validate-markdown` runs markdownlint,
lychee, and codespell.

The weekly schedule exists because link rot, an upstream `gh skill` change, or
install-path drift would otherwise surface only on the next incidental pull
request.
