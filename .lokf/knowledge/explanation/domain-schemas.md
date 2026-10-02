---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/domain-schemas
title: "When the built-in vocabulary stops fitting: domain schemas"
description: "How a bundle in a specialised or regulated domain goes beyond LOKF's core classes: the signs that a domain schema is due, a LinkML schema that imports LOKF's, what it costs, and how the curator, the team and the librarian divide the work."
genre: explanation
resource: skills/ktl-curator/references/domain-schemas.md
sources:
- resource: skills/ktl-curator/references/domain-schemas.md
- resource: skills/ktl-librarian/references/domain-schema.md
- resource: docs/for-the-curious.md
- resource: README.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
references:
  - https://knowledge-trust-ladder.example/knowledge/references/lokf-specification
  - https://knowledge-trust-ladder.example/knowledge/references/lokf-toolkit
about:
  - https://knowledge-trust-ladder.example/knowledge/references/linkml
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
  - https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
---

# Overview

LOKF's vocabulary is a short list of classes and typed relations. `docs/for-the-curious.md` says it is kept small, which is what keeps bundles portable, and that when concepts stop fitting those classes it is typically in a deep or safety-critical domain: medicine, law, finance, safety engineering. The answer is a domain schema written in LinkML that extends LOKF's, not a looser bundle.

# The signs

The curator's `references/domain-schemas.md` lists three. The report's vocabulary-fit line keeps growing, because it counts concepts whose `type` is none of the core classes. Concepts sprout producer-defined keys, such as `dosage` or `jurisdiction`, that no validator checks and no other bundle understands. And the domain is one where a wrong or ambiguous field has consequences.

# What a domain schema is

A LinkML schema of the host's own, `.lokf/<slug>.yaml`, that imports LOKF's schema and adds classes and slots. A class `is_a: Concept` joins the bundle's concept union, so the core classes become the core plus the host's. `lokf validate --schema <slug>.yaml` then checks a bundle against both. The validator treats every class as closed, so a built-in class plus one key of the host's own is not valid; the host subclasses it and declares the key, and a record of the subclass writes the subclass name.

It costs no new tooling. The sidecar depends on `lokf[build]`, whose extra pulls in the full LinkML generator suite. Where the domain already has a LinkML vocabulary of its own, such as the AI Risk Ontology from IBM AI Atlas Nexus, the schema imports it beside LOKF's rather than re-describing the domain.

# Who does what

The roles stay as they are. The curator raises it: a rising vocabulary-fit count is a report line and a conversation with the team. The team decides whether a domain schema is worth owning, since it is a small piece of governed software. The librarian applies it, through the recipe in its `references/domain-schema.md`, and treats every `Concept` descendant in the schema the justfile names as a class it may choose. The two Obsidian plugins cannot read a schema outside the vault, so they are told the classes by hand in their Known LOKF types setting.

Until a schema exists, the misfits are tolerated: the specification says consumers must not reject unknown types. A misfit concept is still knowledge. It is not yet checkable knowledge.
