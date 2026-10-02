---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
title: "ktl-sidecar skill"
description: "The procedure that creates a .lokf/ sidecar from bundled templates, tooling, docs, a dummy skeleton and the knowledge_bundle doorway link, or repairs one missing file, then hands off to ktl-librarian."
genre: how-to
resource: skills/ktl-sidecar/SKILL.md
sources:
- resource: skills/ktl-sidecar/SKILL.md
- resource: skills/ktl-sidecar/references/automation.md
- resource: skills/ktl-sidecar/references/gate.md
- resource: skills/ktl-sidecar/references/portability.md
- resource: skills/ktl-sidecar/references/prerequisites.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
hasPart:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/open-bundle-in-obsidian
references:
  - https://knowledge-trust-ladder.example/knowledge/references/lokf-toolkit
  - https://knowledge-trust-ladder.example/knowledge/explanation/hosts-and-doorways
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
definedBy:
  - https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
---

# Overview

`ktl-sidecar` creates a fresh `.lokf/` sidecar inside the repository it is invoked from: a machine-readable, SPARQL-queryable LOKF knowledge bundle, with its directory, tooling, docs and a small dummy skeleton. Then it hands off to `ktl-librarian` to fill the bundle with real knowledge. Every file is copied from the skill's `templates/` folder, never retyped. The skill runs once, or again to repair a missing or broken sidecar file. It never authors real concepts, and it never overwrites a concept file.

A small or mid-tier model is enough for it: the steps copy templates and substitute placeholders, and mistakes are caught by a grep and a person's sign-off.

# Steps

1. **Gather the host project's facts.** Run the preflight, `templates/scripts/knowledge-preflight.sh`, and read its screen first. It names the host and shell, whether the tree is under git and on which forge, whether `uv` is present, which skill copies are installed, and whether the session is attended. Resolve every placeholder from real project sources: the project name and description from a manifest or the README, a lowercase slug, the owner from `CODEOWNERS` or manifest authors, today's date, and `<BASE_IRI>`. The base IRI must end with `/` and sit in a namespace the project controls, never the code host's repository URL. Decide now whether `.lokf/` is tracked or gitignored.
2. **Create the skeleton and copy the templates.** `pyproject.toml`, `.gitignore`, `.gitattributes`, `justfile`, `README.md`, `knowledge/index.md`, `knowledge/log.md`, two dummy services and, by default, `queries.http`. Substitute the placeholders as literal text through Python, not `sed`, so no value can change what the command does.
3. **Point agents and people at the bundle.** At the repository root, add only and never overwrite: `llms.txt`, a one-paragraph aside in the README, and the `knowledge_bundle` link, `ln -s .lokf/knowledge knowledge_bundle`, or a junction on Windows.
4. **Verify the skeleton.** Grep for leftover placeholder tokens; zero hits means fully resolved.
5. **Validate the skeleton.** `just lokf-install && just lokf-validate` from `.lokf/`. With no `uv`, cross-check the raw schema by hand and say so.
6. **Lay down the automation.** The registrar gate, the scheduled librarian workflow and its wrapper, the release workflow, the conventions, preflight, provenance and feedback scripts, and the Copilot builder with the docent's instructions file. The workflows are skipped for a gitignored bundle; two scripts and the `m365/` folder land regardless. Check whether commits are signed, and show the three `git config` lines without running them.
7. **Hand off to ktl-librarian.** Say which values were guessed, whether validation ran, which optional pieces were added, whether `.lokf/` is tracked, and whether the doorway was created.

# Where the detail lives

`references/automation.md` covers the librarian loop, the release asset and the feedback script, and how to wire each. `references/gate.md` covers the registrar workflow, commit signing and the forge-free gate. `references/portability.md` says what each kind of host loses and the substitute. `references/prerequisites.md` translates every preflight line into who fixes it and what to send them. `references/m365.md` says what Copilot allows.
