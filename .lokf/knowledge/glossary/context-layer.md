---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/context-layer
title: Context layer
description: A governed layer between an organisation's sources and whoever consumes them, person or agent, that persists from one task to the next. One knowledge bundle is one repository's context layer, and KTL federates many bundles into one layer through domains.
definition: A governed layer between an organisation's sources (code, documents, diagrams, policies, operational records) and whoever consumes them, a person or an agent, that persists from one task to the next.
genre: reference
resource: docs/architecture.md
sources:
  - resource: docs/architecture.md
  - resource: docs/context-layer.md
  - resource: docs/federation.md
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/context-layer
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
generated:
  by: process:ktl-librarian
  at: "2026-10-19T12:30:15Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-20T23:23:33Z"
---

# Overview

The architecture page says that knowledge already exists, in code, documents, diagrams, policies and operational records. What is missing is a **context layer**: a governed layer between those sources and whoever consumes them, that persists from one task to the next. Without it every task starts the same way: find the material, connect it, judge what is still true. The next person or assistant pays for that work again. `docs/context-layer.md` speaks of an organisation's sources, and of whoever consumes them as a person or an agent.

One bundle is one repository's context layer. `docs/context-layer.md` places Knowledge Trust Ladder in the industry's talk of context layers, and says why KTL federates bundles through domains: a domain selects released bundles, and one accountable owner confirms each bundle it admits. `docs/federation.md` says how a federation is built and run, and what exists and what remains a design ([the curated context layer](../explanation/context-layer.md)).
