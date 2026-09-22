---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/lokf-specification
title: LOKF specification
description: The canonical definition of the Linked Open Knowledge Format - a semantic profile of OKF binding every field, type, and relationship to schema.org, DCAT, and PROV-O.
genre: reference
resource: https://lokf.nolan-nichols.com/specification/
generated:
  by: process:ktl-librarian
  at: "2026-09-09T10:00:00Z"
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/references/okf-specification
verified:
- by: process:ktl-librarian
  at: "2026-09-17T14:02:11Z"
- by: human:noelmcloughlin
  at: "2026-09-09T18:38:00Z"
stale_after: 2027-09-09
---

# Overview

The site is the authority for what LOKF *means*: the Golden Rules the
librarian skill carries, the type vocabulary, the typed-relation predicates,
and the trust families. The format itself is defined once in LinkML
(`lokf.yaml`); the JSON Schema, JSON-LD context, SHACL shapes, and OWL
ontology are all **generated** from it and must not be hand-edited.

Distinct from the [toolkit](lokf-toolkit.md) that implements it: the site
defines meaning, the PyPI package does the validating and projecting. The
skills cite each for its own role.
