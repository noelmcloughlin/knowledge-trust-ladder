---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/repository-validation
title: "Repository validation"
description: "What continuous integration checks on every pull request and weekly: the repository contract, the Agent Skills specification, shell and workflow linting, the install smoke test, Markdown linting, link checking and spelling."
genre: how-to
resource: .github/workflows/validate.yml
sources:
- resource: .github/workflows/validate.yml
- resource: scripts/validate-repository.sh
- resource: scripts/smoke-test-install.sh
- resource: CONTRIBUTING.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
references:
  - https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
  - https://knowledge-trust-ladder.example/knowledge/references/open-skills-cli
  - https://knowledge-trust-ladder.example/knowledge/playbooks/contributing
---

# Overview

`validate.yml` runs on every push and pull request, and weekly on Mondays at 06:00 UTC. It has five jobs, each on a hardened runner with actions pinned to commit SHAs. `CONTRIBUTING.md` says to run the contract locally first: continuous integration runs the same script plus the linters.

# The jobs

1. **Validate repository contract and Agent Skills spec.** Sets up `uv`, runs `bash scripts/validate-repository.sh`, then `gh skill publish --dry-run`, which checks every skill against the Agent Skills specification.
2. **Lint shell scripts** with ShellCheck.
3. **Lint GitHub Actions workflows** with actionlint, and check that every action is pinned to a commit.
4. **Smoke-test the install path.** With Node set up, `scripts/smoke-test-install.sh` installs all five skills into a throwaway repository with `npx skills add`, and checks that each is discovered, that its files arrived, and that `ktl-prose`'s installed script runs.
5. **Lint Markdown and check links** with markdownlint, lychee and codespell.

# The repository contract

`scripts/validate-repository.sh` is the entry point, and it names each check as it runs. Among them:

- the five skill directories and their frontmatter;
- relative link targets;
- the paths the sibling repositories link into, which must not move;
- `CONTRIBUTING.md` and `SECURITY.md` under their word budgets;
- the sidecar templates byte-identical to this repository's own copies, with the conventions, preflight, feedback and provenance scripts exercised on fixtures;
- `CHANGELOG.md` with no version promoted twice;
- the librarian template's skills pin at a current release;
- the old repository and skill names kept out;
- the Microsoft 365 Copilot skills building reproducibly from this bundle, with the Copilot template carrying the docent's trust labels word for word;
- `prose-check.py` giving the expected verdict on fixtures and on this repository's own bundle.

It ends with one line, PASS or FAIL.

# The bundle's own gate

The bundle has a gate of its own, `knowledge-registrar.yaml`, which runs on every pull request touching `.lokf/**`: `lokf validate --check-refs` and the eleven conventions, and the `provenance` job that ties each new `human:` confirmation to that person's approval or signature. It is the sidecar's template, used here as in any consumer.
