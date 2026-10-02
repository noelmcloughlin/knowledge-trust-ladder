---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/okf
title: "OKF"
description: "The Open Knowledge Format, Google Cloud's specification for a folder of Markdown concept files with YAML frontmatter, which LOKF profiles."
definition: "Google Cloud's Open Knowledge Format: a folder of Markdown files, one concept per file, with YAML frontmatter in which only `type` is required, plus the v0.2 provenance, trust and lifecycle fields."
abbreviation: OKF
genre: reference
resource: skills/ktl-librarian/SKILL.md
sources:
- resource: skills/ktl-librarian/SKILL.md
- resource: README.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/glossary/lokf
definedBy:
  - https://knowledge-trust-ladder.example/knowledge/references/okf-specification
---

# Overview

OKF is the Open Knowledge Format, published by Google Cloud. Its Golden Rule, as the librarian skill repeats it, is "OKF first": one concept per file, the file path is the concept id, `type` is the only strictly required field, and consumers are permissive. Every LOKF bundle is also a valid OKF bundle.

# What this family takes from it

The README quotes OKF's fourth goal: to "standardize the small set of frontmatter fields making an agent-maintained corpus trustable, without prescribing any runtime". This family is such a runtime. OKF's v0.2 fields `generated`, `verified`, `sources`, `status` and `stale_after` become the ladder each claim climbs, and its section 7 actor strings (`human:<id>`, `process:<id>`) are what every trust label is computed from.

OKF puts a fixed taxonomy of concept types and domain-specific schemas out of scope. The README notes that LOKF brings both into scope by construction: a domain's own types get a schema of their own.
