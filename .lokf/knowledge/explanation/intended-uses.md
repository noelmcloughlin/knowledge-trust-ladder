---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/intended-uses
title: What Knowledge Trust Ladder is for, and what it is not
description: "A draft placeholder for a reader's question no source settles: which uses Knowledge Trust Ladder is meant for, such as DevSecOps or technology governance, and which it is not. The README and `docs/context-layer.md` state the purpose and name no use case or non-goal, and `docs/skills-repositories.md` answers it only for a repository whose content is Agent Skills."
genre: explanation
resource: README.md
sources:
- resource: README.md
- resource: docs/skills-repositories.md
- resource: docs/context-layer.md
generated:
  by: process:ktl-librarian
  at: "2026-10-12T16:08:20Z"
status: draft
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/explanation/three-lines-of-defence
- https://knowledge-trust-ladder.example/knowledge/policies/threat-model
- https://knowledge-trust-ladder.example/knowledge/explanation/domain-schemas
- https://knowledge-trust-ladder.example/knowledge/explanation/context-layer
verified:
- by: process:ktl-librarian
  at: "2026-10-12T23:54:05Z"
---

# Overview

The README states what the project is. It keeps a repository's scattered knowledge as a collection: catalogued, authenticated and explained, with the trust in every claim visible. It says what is missing is a **context layer**: a governed layer between the sources (code, documents, diagrams, policies, operational records) and whoever consumes them, person or agent, and that a knowledge bundle is the catalogue. The layer persists from one task to the next. The README's term now links `docs/context-layer.md`, which sets it beside the industry's and says one bundle is one repository's context layer ([the context layer](context-layer.md)).

The README frames it around one question: who is responsible for the quality of this context? An agent derives the bundle, deterministic tools check it, a named person vouches for it, and the bundle records which of the three happened to every claim.

One page now answers this for one kind of repository. `docs/skills-repositories.md` says that in a repository whose content is Agent Skills, KTL helps with the knowledge around the skills and leaves the skills as they are. It leaves whether a skill works to an evaluation, since KTL's checks cover the form and the provenance of what the bundle says.

No source says in general which kinds of use KTL fits and which it does not. Two neighbouring concepts cover parts of the ground: [three lines of defence](three-lines-of-defence.md) places the roles in a governance model, and [domain schemas](domain-schemas.md) covers modelling a regulated domain (AI governance among them). Neither states intended uses or non-goals.

## Open questions

- 2026-09-24, process:ktl-librarian: Readers asked whether KTL can be used for DevSecOps and for technology governance (ktl-docent feedback, 2026-09-24). No repository source states which uses KTL is meant for and which it is not - for example, that it keeps knowledge about systems rather than scanning or enforcing anything. A maintainer should either write that in a source (README or a docs page) for this concept to follow, or retire this placeholder.
