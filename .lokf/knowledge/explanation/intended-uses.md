---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/intended-uses
title: What Knowledge Trust Ladder is for, and what it is not
description: Placeholder for a reader's question the sources do not settle - which uses KTL fits (such as DevSecOps or technology governance) and which it does not. Today the README states the purpose, a governed context layer over a repository's knowledge, but names no use cases or non-goals.
genre: explanation
resource: README.md
sources:
- resource: README.md
generated:
  by: process:ktl-librarian
  at: "2026-09-24T10:52:00Z"
status: draft
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/explanation/three-lines-of-defence
- https://knowledge-trust-ladder.example/knowledge/policies/threat-model
- https://knowledge-trust-ladder.example/knowledge/explanation/domain-schemas
---

# Overview

The README states what the project is: it keeps a repository's scattered knowledge as a collection - catalogued, authenticated and explained, with the trust in every claim visible. It calls that a **context layer**, a governed layer between the sources (code, documents, diagrams, policies, operational records) and whoever consumes them, person or agent, and frames it around one question: who is responsible for the quality of this context? An agent derives the bundle, deterministic tools check it, a named person vouches for it, and the bundle records which of the three happened to every claim.

No source in the repository goes further and says which kinds of use this fits and which it does not. Two neighbouring concepts cover parts of the ground: [three lines of defence](three-lines-of-defence.md) places the roles in a governance model, and [domain schemas](domain-schemas.md) covers modelling a regulated domain (AI governance among them). Neither states intended uses or non-goals.

## Open questions

- 2026-09-24, process:ktl-librarian: Readers asked whether KTL can be used for DevSecOps and for technology governance (ktl-docent feedback, 2026-09-24). No repository source states which uses KTL is meant for and which it is not - for example, that it keeps knowledge about systems rather than scanning or enforcing anything. A maintainer should either write that in a source (README or a docs page) for this concept to follow, or retire this placeholder.
