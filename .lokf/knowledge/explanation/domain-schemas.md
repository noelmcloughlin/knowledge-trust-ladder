---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/domain-schemas
title: When the built-in vocabulary stops fitting - domain schemas
description: How a bundle in a specialised or regulated domain goes beyond LOKF's core classes - the signs a domain schema is due, a LinkML schema importing LOKF's and checked with `lokf validate --schema`, reusing a domain's existing vocabulary (the AI Risk Ontology for AI governance), and who raises, decides and applies it.
genre: explanation
resource: skills/ktl-curator/references/domain-schemas.md
sources:
- resource: skills/ktl-curator/references/domain-schemas.md
- resource: skills/ktl-librarian/references/domain-schema.md
- resource: README.md
generated:
  by: process:ktl-librarian
  at: "2026-09-24T10:52:00Z"
status: draft
about:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
references:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
- https://knowledge-trust-ladder.example/knowledge/references/linkml
- https://knowledge-trust-ladder.example/knowledge/references/lokf-toolkit
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/explanation/three-lines-of-defence
---

# Overview

LOKF ships a small vocabulary on purpose: a short list of classes, the typed relations and a handful of trust fields, which keeps bundles portable. OKF puts "replacing domain-specific schemas" out of scope; the README says that here it is in scope by construction, because a domain's own types get a schema of their own and go from merely tolerated to checked.

**The signs.** The curator's *vocabulary fit* line keeps growing (concepts whose `type` is outside the known classes, tolerated under Golden Rule 7 but carrying no agreed meaning); concepts sprout producer-defined keys such as `dosage`, `jurisdiction` or `failure_mode` that no validator checks; or the domain is one where a wrong field has consequences - medicine, law, finance, safety engineering, anything regulated.

**The mechanism.** Keep the OKF/LOKF mechanics and give the domain a LinkML schema of its own that imports LOKF's, validated with `lokf validate --schema <slug>.yaml`. Every class is closed, so a built-in class plus an extra key fails: subclass it (`is_a: Reference`) or add a class of its own (`is_a: Concept`), and have frontmatter name the subclass exactly. The recipe keeps a pinned copy of `lokf.yaml` beside the domain schema and wires the flag into the justfile and both workflows; the two Obsidian plugins learn the new classes through their *Known LOKF types* setting. The sidecar already depends on `lokf[build]`, so the LinkML generators are installed and a domain schema costs one file, nothing new to install. What it does not change is the graph: `convert`, `serve` and `query` take no `--schema`, so domain keys project in LOKF's namespace.

**When the domain already has a vocabulary**, reuse it rather than re-describe it. For AI governance, the curator's guidance names IBM AI Atlas Nexus's [AI Risk Ontology](https://ibm.github.io/ai-atlas-nexus/ontology/), a LinkML vocabulary covering risks, controls, obligations, taxonomies, incidents and evaluations, and [ai-linkmo](https://github.com/noelmcloughlin/ai-linkmo) as a reference implementation over it with a LOKF sidecar beside it. A domain schema can import that vocabulary beside LOKF's, so a concept names a control or an obligation by the identifier the domain already uses; confirm the import path the toolkits support first. Such a vocabulary usually lacks the bundle's half - who encoded a record, from which edition, who confirmed it, when to look again - and whether those fields belong on the domain's own records is left to the domain's owners and to OKF as it evolves.

Where a domain schema binds a slot to an external code list (SNOMED CT, say), neither LOKF's schema nor `lokf validate` checks that the term still exists; `linkml-term-validator` can, as an optional extra gate whose "service unreachable" counts as not passing.

**Roles stay as they are.** The curator raises it, as a report line and a conversation; the team decides whether a domain schema, a small piece of governed software, is worth owning; the librarian applies it. Until then a misfit concept is still knowledge, just not yet checkable knowledge.
