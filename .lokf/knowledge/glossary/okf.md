---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/okf
title: OKF
definition: Open Knowledge Format - Google's specification for a folder of Markdown concept files with YAML frontmatter, where the file path is the concept ID and `type` is the only strictly required field.
abbreviation: OKF
genre: reference
resource: skills/lokf-librarian/SKILL.md
generated:
  by: process:lokf-librarian
  at: "2026-09-09T10:00:00Z"
status: draft
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/okf-specification
verified:
- by: process:lokf-librarian
  at: "2026-09-17T14:02:11Z"
---

# Overview

The substrate LOKF profiles. Its defining trait is permissiveness: a consumer
must not reject a bundle for missing optional fields, unknown types, unknown
keys, or broken cross-links. Every LOKF bundle is also a valid OKF bundle.
