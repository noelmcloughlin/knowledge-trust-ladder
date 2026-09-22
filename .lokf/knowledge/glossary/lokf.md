---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/lokf
title: LOKF
definition: Linked Open Knowledge Format - a semantic profile of OKF in which every field, type, and relationship is bound to a public vocabulary, so the same Markdown expands losslessly to JSON-LD and RDF.
abbreviation: LOKF
genre: reference
resource: README.md
generated:
  by: process:ktl-librarian
  at: "2026-09-09T10:00:00Z"
status: draft
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/lokf-specification
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/glossary/okf
verified:
- by: process:ktl-librarian
  at: "2026-09-16T09:10:00Z"
---

# Overview

Plain OKF gives knowledge prose and structure. LOKF adds **meaning**, and that
is what lets standard, schema-generated tooling - JSON Schema, SHACL, SPARQL -
validate and query a bundle instead of bespoke per-repository scripts.
