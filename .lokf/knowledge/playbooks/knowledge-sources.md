---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/knowledge-sources
title: "Knowledge sources"
description: "The map of the repository locations this bundle was derived from, the class each yields, and how to re-check each one on a future refresh."
genre: how-to
resource: .
sources:
- resource: README.md
- resource: docs
- resource: skills
- resource: CONTRIBUTING.md
- resource: SECURITY.md
- resource: AI_COVENANT.md
- resource: CODE_OF_CONDUCT.md
- resource: .github/workflows
- resource: scripts
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
---

# Overview

This bundle is derived from the repository's own README, docs and skill pages. The librarian's first run records where it looked, so that every later run is a re-check against this map rather than fresh discovery. This bundle was derived again in full on 2026-10-02, after a plain-prose pass over every source below, with the earlier bundle emptied first so that no confirmation rested on a source text that had changed under it.

# The map

| Source | What it yields | Re-check by |
| --- | --- | --- |
| `README.md` | the explanations of the roles, the registrar, intended use and the distribution repository; the glossary terms LOKF and OKF; the trust labels | reading it whole; it is the front page and changes with every release |
| `docs/three-lines.md`, `docs/three-lines-critics.md` | the three-lines explanation | reading both; the critics page cites external papers by DOI, which are not fetched |
| `docs/obsidian.md`, `skills/ktl-sidecar/references/portability.md` | the Obsidian playbook and the hosts-and-doorways explanation | reading both; the host-by-host section is where behaviour changes land |
| `docs/m365.md`, `skills/ktl-sidecar/references/m365.md`, `skills/ktl-sidecar/templates/m365/` | the Copilot playbook | reading the docs page; the sidecar page carries the toolkit versions tried |
| `docs/releasing.md`, `.github/workflows/publish.yml`, `.github/workflows/semantic-release.yml`, `CHANGELOG.md` | the releasing playbook and the versioning policy | reading the docs page and each workflow's header comment; the changelog's top heading is the current version |
| `.github/workflows/validate.yml`, `scripts/validate-repository.sh`, `scripts/smoke-test-install.sh` | the repository-validation playbook | reading the workflow's job list and the script's numbered checks |
| `CONTRIBUTING.md` | the contributing playbook | reading it; the repository contract holds it under 1,000 words |
| `SECURITY.md`, `docs/threat-model.md` | the security policy and the threat model | reading both; the threat model is shared with the sibling repositories |
| `AI_COVENANT.md`, `CODE_OF_CONDUCT.md` | the two conduct policies | reading them; the code of conduct is adapted from the Contributor Covenant and changes rarely |
| `skills/<name>/SKILL.md` and `references/` for each of the five skills | one playbook per skill, and the domain-schemas explanation | reading each skill's page; a change to what a skill does needs a `CHANGELOG.md` line, which is the cheap signal |
| `skills/ktl-curator/references/trust-fields.md` | the trust-label glossary term | reading its table; the docent and the Copilot template must say the same words |
| the external specifications and tools the README and skills link | the seven reference concepts | the URLs are recorded as resources and never fetched by the gate; a version change shows up in `.lokf/pyproject.toml`'s floor or the README's schema link |

# What is left out on purpose

`docs/examples/` holds dated captures of the docent and the curator and is not a source of facts. `CHANGELOG.md`'s released sections are a record of the past. `skills/ktl-sidecar/templates/` is what the sidecar lays down in a host, described through the sidecar playbook rather than concept by concept. The `.assets/` figures are images.
