---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/desk
title: Desk
description: "The library word for the place where a role does its work with the bundle: the registrar is `knowledge-apply.sh` at the librarian's desk, and `knowledge-report.sh` at the reader's and the curator's."
definition: In the project's library and museum terms, the place where a role does its work with the bundle. A program does the registrar's work at each desk.
genre: reference
resource: docs/architecture.md
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://w3id.org/ktl/knowledge/glossary/the-pen
  - https://w3id.org/ktl/knowledge/explanation/why-a-registrar-role
generated:
  by: process:ktl-librarian
  at: "2026-11-13T14:41:35Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-29T00:48:33Z"
sources:
  - resource: docs/architecture.md
  - resource: docs/cast/registrar.md
    id: cast-registrar.md
    excerpt: at the librarian's desk | Applies the librarian's patch, and is the only way the librarian writes the bundle. It refuses an operation that would fake or change a person's record, and an excerpt its file does not hold ... at the reader's desk and the curator's | Computes every trust label and the bundle's health line, so that neither is a model's arithmetic
---

# Overview

The architecture page uses *desk* in its library and museum terms, for the place where a role does its work with the bundle. It names a part of the registrar at each one: `knowledge-apply.sh`, *the pen*, at the librarian's desk, and `knowledge-report.sh` at the reader's desk and the curator's. The registrar's own page says what each part does there.[^cast-registrar.md] The pen applies the librarian's patch, and is the only way the librarian writes the bundle. It refuses an operation that would fake or change a person's record, and an excerpt its file does not hold. `knowledge-report.sh` computes every trust label and the bundle's health line, so that neither is a model's arithmetic.

In Obsidian there is no CI, so KTL Registrar does the registrar's work inside the editor, checking each record as it is typed. KTL Curator, the other optional plugin, is the curator's assistant.

[^cast-registrar.md]: docs/cast/registrar.md, the table under *Its parts*
