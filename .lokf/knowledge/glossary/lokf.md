---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/lokf
title: LOKF
description: The Linked Open Knowledge Format, the semantic profile of OKF this bundle is written in, which binds every field to a public vocabulary so the bundle projects to RDF.
definition: Linked Open Knowledge Format - a semantic profile of OKF in which every field, type, and relationship is bound to a public vocabulary, so the same Markdown expands losslessly to JSON-LD and RDF.
abbreviation: LOKF
genre: reference
resource: docs/architecture.md
sources:
- resource: docs/architecture.md
- resource: skills/ktl-librarian/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-13T15:08:54Z"
status: draft
definedBy:
- https://w3id.org/ktl/knowledge/references/lokf-specification
relatedTo:
- https://w3id.org/ktl/knowledge/glossary/okf
- https://w3id.org/ktl/knowledge/glossary/linkml
verified:
- by: process:ktl-librarian
  at: "2026-10-14T00:35:00Z"
---

# Overview

LOKF's specification is a single LinkML schema, created by Nolan Nichols. OKF, the specification it profiles, is Google Cloud's. Plain OKF gives knowledge prose and structure. LOKF adds meaning, which lets standard, schema-generated tooling (JSON Schema, SHACL, SPARQL) validate and query a bundle, instead of scripts that only work in the repository they were written for. The tools come with the standard rather than with this project. A bundle can be read by people, agents and any tool that speaks OKF, JSON Schema, JSON-LD, SHACL or another format LinkML generates.
