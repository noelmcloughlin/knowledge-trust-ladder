---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/lokf
title: LOKF
description: The Linked Open Knowledge Format, the semantic profile of OKF this bundle is written in, which binds every field to a public vocabulary so the bundle projects to RDF.
definition: Linked Open Knowledge Format - a semantic profile of OKF in which every field, type, and relationship is bound to a public vocabulary, so the same Markdown expands losslessly to JSON-LD and RDF.
abbreviation: LOKF
genre: reference
resource: README.md
sources:
- resource: README.md
- resource: skills/ktl-librarian/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-09-24T16:52:47Z"
status: draft
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/lokf-specification
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/glossary/okf
---

# Overview

LOKF's specification is a single LinkML schema, created by Nolan Nichols; OKF, the specification it profiles, is Google Cloud's. Plain OKF gives knowledge prose and structure. LOKF adds meaning, which is what lets standard, schema-generated tooling - JSON Schema, SHACL, SPARQL - validate and query a bundle instead of scripts that only work in the repository that grew them. This project invents no field, format or validator of its own: a bundle can be read by people, agents and any tool that speaks OKF, JSON Schema, JSON-LD, SHACL or another format LinkML generates.
