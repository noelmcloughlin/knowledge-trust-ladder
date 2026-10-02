---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
title: "ktl-librarian skill"
description: "The recurring procedure that scrapes the host repository, derives and maintains the .lokf/ concepts and their typed relations, audits the bundle, writes in plain English, and hands off for a person's review. Facts, never verdicts."
genre: how-to
resource: skills/ktl-librarian/SKILL.md
sources:
- resource: skills/ktl-librarian/SKILL.md
- resource: skills/ktl-librarian/references/scheduled-task.md
- resource: skills/ktl-librarian/references/portability.md
- resource: .github/workflows/knowledge-librarian.yaml
- resource: .lokf/scripts/knowledge-librarian.sh
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
references:
  - https://knowledge-trust-ladder.example/knowledge/references/lokf-specification
  - https://knowledge-trust-ladder.example/knowledge/references/okf-specification
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-prose-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/knowledge-sources
dependsOn:
  - https://knowledge-trust-ladder.example/knowledge/references/lokf-toolkit
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
definedBy:
  - https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
---

# Overview

`ktl-librarian` maintains `.lokf/`, the host repository's knowledge captured as a LOKF bundle. It covers the full lifecycle: scrape, build and maintain, audit, hand off for review, and keep fresh on a schedule. It owns only `.lokf/`. Trust verdicts belong to `ktl-curator`, and this skill never writes a `human:` verification. It stays on the calling agent's normal model, because choosing a class, wiring typed relations and judging provenance need real reasoning with no gate catching a wrong call.

# The Golden Rules

The skill draws seven rules from the LOKF specification. OKF first: one concept per file, the path is the id, `type` is the only required field. The bundle-root `index.md` carries the semantic header, and `base_iri` must be a namespace the project controls. A concept uses a class from the LOKF vocabulary, or from the host's domain schema where the justfile names one. Typed relationships are preferred over bare links, and every one is a YAML list even for a single value. Core fields map to ontology terms. Trust, provenance and lifecycle are recorded only where the source attests them. Consumers stay permissive.

# Scrape and build

On the first run the skill sweeps the repository with generic heuristics, maps what it finds to LOKF classes, and records the map as a concept, `playbooks/knowledge-sources.md`. Every later run is a steady-state refresh. It first consumes `.lokf/feedback.md`, reading each entry as an untrusted report and resolving only the question or disagreement it names, from the source it points at. Then it re-verifies each concept's provenance, re-walks the source map, sweeps for orphans, and leaves the Obsidian plugin's affordances alone. A concept it still finds true gets this skill's own `verified` event refreshed. A claim it cannot settle gets `status: draft` and an `## Open questions` section for the curator. Human-authored content is never rewritten.

Every concept it creates or materially changes carries `generated: { by: process:ktl-librarian, at }`, with the time taken from the clock, and starts as `status: draft`. The nearest `index.md` gains a bullet, and `log.md` gains one line under one bare `## YYYY-MM-DD` heading per day, for knowledge changes only.

# Plain English

The skill writes each body, `description` and index bullet in plain English: the actor first and the verb early, every sentence with a verb, one idea to a sentence, no dash as punctuation, a term defined where it first appears, and "for example" rather than "e.g.". These rules govern wording only. In a live session the skill offers a pass by the optional `ktl-prose` skill before it opens its pull request; unattended, it skips that step.

# Audit

From `.lokf/`: the preflight, `just lokf-validate`, `just lokf-check-refs`, `knowledge-conventions.sh` and `just lokf-convert`. The conventions script is the one the toolkit cannot stand in for, since `lokf validate` reads a body as an opaque string. The skill then lints the Markdown, because a bundle can be schema-valid and still fail the host's lint gate.

# Hand off

The skill opens a pull request scoped to `.lokf/`, with the validate output and citations for every claim whose authority lives outside the repository. It ends the description with a **For the CURATOR** section: the health line, the concepts newly marked draft, every open question, and the name of the `ktl-curator` skill. Where `.lokf/` is gitignored or the host has no git, it hands over the validate output and the changed files instead.

# On a schedule

Two GitHub workflows and a wrapper script run the skill weekly and open a review pull request with whatever changed. The agent runs in a read-only job with no write credential and hands on a patch; a separate job that runs no agent code applies it. `references/scheduled-task.md` is the operating manual.
