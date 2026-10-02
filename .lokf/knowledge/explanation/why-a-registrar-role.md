---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/why-a-registrar-role
title: "Why a registrar role, and why it is not a skill"
description: "The job none of the skills does, keeping bundle records well-formed and every confirmation tied to a person, and why tooling does it: the lokf toolkit, the knowledge-registrar.yaml gate, and the KTL Registrar plugin in Obsidian."
genre: explanation
resource: README.md
sources:
- resource: README.md
- resource: docs/obsidian.md
- resource: docs/three-lines.md
- resource: skills/ktl-sidecar/references/gate.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/explanation/why-four-roles
  - https://knowledge-trust-ladder.example/knowledge/explanation/three-lines-of-defence
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
---

# Overview

The README calls the registrar the fifth role, which is not a skill. It keeps the records themselves in order: each accession documented, its provenance filed, nothing entered in a form the catalogue cannot read. No person has to do it, and no agent does it either.

# Who does the registrar's work

- The `lokf` toolkit does it on every change, through `lokf validate`.
- Continuous integration does it again on every pull request that touches the bundle, through `knowledge-registrar.yaml`. There it also checks that each new confirmation is backed by that person's approval of the pull request or their signature on the commit.
- In Obsidian there is no continuous integration, so the KTL Registrar plugin checks each record is well-formed as it is typed, live in the editor. `docs/obsidian.md` lists it beside `lokf validate` in the registrar row.

# Why it is not a skill

A skill is prose an agent follows, and `docs/three-lines.md` places the registrar in the second line: it ensures compliance without owning the content. The gate's `validate` and `provenance` jobs return the same verdict whoever opened the change, and that is what makes them a second line that can challenge the first. An agent asked to keep the paperwork honest could be talked out of it; a program cannot. The registrar never judges whether a record is true. A verdict is only ever what the named person said.

# What it proves, and what it does not

The gate raises forgery of a confirmation from typing four lines of YAML to controlling that person's GitHub account or signing key. It proves who vouched, not what they read. That limit is stated on every page that describes it.
