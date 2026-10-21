---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/okf
title: OKF
description: The Open Knowledge Format, Google's specification for a folder of Markdown concept files with YAML frontmatter, which LOKF profiles.
definition: Open Knowledge Format - Google's specification for a folder of Markdown concept files with YAML frontmatter, where the file path is the concept ID and `type` is the only strictly required field.
abbreviation: OKF
genre: reference
resource: skills/ktl-librarian/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-13T15:08:54Z"
status: draft
definedBy:
  - https://w3id.org/ktl/knowledge/references/okf-specification
verified:
  - by: process:ktl-librarian
    at: "2026-10-20T23:23:33Z"
sources:
  - resource: docs/architecture.md
---

# Overview

OKF is the specification that LOKF profiles. Its defining trait is permissiveness: a consumer must not reject a bundle for missing optional fields, unknown types, unknown keys, or broken cross-links. Every LOKF bundle is also a valid OKF bundle.
