---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/lokf-specification
title: "LOKF specification"
description: "The canonical definition of the Linked Open Knowledge Format: a semantic profile of OKF that binds every field, type and relationship to schema.org, DCAT and PROV-O terms."
genre: reference
resource: https://lokf.nolan-nichols.com/specification/
sources:
- resource: https://lokf.nolan-nichols.com/specification/
- resource: skills/ktl-librarian/SKILL.md
- resource: README.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
references:
  - https://knowledge-trust-ladder.example/knowledge/references/okf-specification
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/references/lokf-toolkit
  - https://knowledge-trust-ladder.example/knowledge/references/linkml
  - https://knowledge-trust-ladder.example/knowledge/glossary/lokf
---

# Overview

lokf.nolan-nichols.com is, in the librarian skill's words, the canonical site for what LOKF means. The specification and the Golden Rules come from it. The format itself is one LinkML schema, published in the `nicholsn/lokf` repository on GitHub, and the README links the schema at tag v0.8.0.

# What the specification fixes

The librarian skill draws seven Golden Rules from it. Among them:

- the bundle-root `index.md` carries the semantic header;
- a concept uses a class from the type vocabulary, one of `Dataset`, `Table`, `Metric`, `Service`, `Playbook`, `Tutorial`, `Explanation`, `Policy`, `GlossaryTerm`, `Reference`, `Document`, `Role`, `Person`, `Organization` and `AttestedComputation`;
- typed relationships are preferred over bare links, each mapping to a fixed RDF predicate;
- core fields map to ontology terms;
- trust, provenance and lifecycle are recorded only where the source attests them;
- consumers stay permissive.

# How this repository tracks it

The sidecar pins the toolkit at the 0.8.0 floor. The raw schema at the matching tag, never `main`, is the fallback for an audit with no Python. Where a page says a field is proposed for lokf 0.9.0, such as `revision` on an event and `excerpt` on a source, the 0.8.0 validator rejects it, and the skills leave it out until the floor moves.
