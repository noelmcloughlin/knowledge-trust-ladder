---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/lokf
title: "LOKF"
description: "The Linked Open Knowledge Format: a semantic profile of OKF that binds every field, type and relationship to a public vocabulary, so a bundle projects losslessly to JSON-LD and RDF."
definition: "A semantic profile of OKF, written as one LinkML schema, in which every frontmatter field, concept type and typed relationship maps to a public vocabulary such as schema.org, DCAT or PROV-O."
abbreviation: LOKF
genre: reference
resource: README.md
sources:
- resource: README.md
- resource: skills/ktl-librarian/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/glossary/okf
  - https://knowledge-trust-ladder.example/knowledge/references/lokf-toolkit
  - https://knowledge-trust-ladder.example/knowledge/references/linkml
definedBy:
  - https://knowledge-trust-ladder.example/knowledge/references/lokf-specification
---

# Overview

LOKF stands for Linked Open Knowledge Format. The README calls a bundle written in it "prose a person reads, structure a schema checks, meaning a graph can query, and tools that come with the standard rather than with this project". LOKF is the same directory of Markdown files with YAML frontmatter that OKF defines, but every field, type and relationship is bound to a public vocabulary. So the bundle expands to JSON, JSON-LD and RDF without loss, and a SPARQL engine can query it.

# Why this family uses it

The README states the position as "specification first, schema first, interoperability first". Nothing in this repository invents a field, a format or a validator. The whole format is one LinkML schema, `lokf.yaml`, and the JSON Schema, JSON-LD context, SHACL shapes and OWL ontology are generated from it. A folder of Markdown can therefore be validated, queried as a graph, and read by people, agents and any tool that speaks OKF, JSON Schema, JSON-LD or SHACL.

The librarian skill lists what LOKF adds over plain OKF. It adds a type vocabulary of fifteen core classes, and ten typed relationships that each map to a fixed RDF predicate. It makes the trust fields of OKF v0.2 (`generated`, `verified`, `sources`, `status`, `stale_after`) queryable.

# Where it is defined

The canonical site is lokf.nolan-nichols.com, which carries the specification and the Golden Rules. The `lokf` package on PyPI carries the toolkit that validates, converts and serves a bundle. This repository's sidecar pins the toolkit at the 0.8.0 floor, and the raw schema at the matching tag is the fallback for an audit with no Python.
