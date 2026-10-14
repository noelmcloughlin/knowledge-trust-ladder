---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/desk
title: Desk
description: "The library word for the place where a role does its work with the bundle: the registrar is `knowledge-apply.sh` at the librarian's desk, and `knowledge-report.sh` at the reader's and the curator's."
definition: In the project's library and museum terms, the place where a role does its work with the bundle. A program does the registrar's work at each desk.
genre: reference
resource: docs/architecture.md
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/glossary/the-pen
- https://knowledge-trust-ladder.example/knowledge/explanation/why-a-registrar-role
generated:
  by: process:ktl-librarian
  at: "2026-10-13T15:08:54Z"
status: draft
verified:
- by: process:ktl-librarian
  at: "2026-10-14T00:35:00Z"
---

# Overview

The architecture page uses *desk* in its library and museum terms, for the place where a role does its work with the bundle. It says which program is the registrar at each one. At the librarian's desk the registrar is `knowledge-apply.sh`, called *the pen* because the librarian writes the bundle only through it. At the reader's desk and the curator's it is `knowledge-report.sh`, which computes each trust label and the bundle's health line, so that neither is a model's arithmetic.

In Obsidian there is no CI, so KTL Registrar does the registrar's work inside the editor, checking each record as it is typed. KTL Curator, the other optional plugin, is the curator's assistant.
