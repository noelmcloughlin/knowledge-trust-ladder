---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/okf-specification
title: OKF specification (v0.2)
description: Google's Open Knowledge Format - a folder of Markdown concept files with YAML frontmatter, requiring only `type`, plus the v0.2 provenance, trust, and lifecycle families.
genre: reference
resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
generated:
  by: process:ktl-librarian
  at: "2026-09-09T00:13:37Z"
verified:
- by: process:ktl-librarian
  at: "2026-09-24T00:55:04Z"
- by: human:noelmcloughlin
  at: "2026-09-09T16:35:55Z"
stale_after: 2027-09-09
---

# Overview

Every LOKF bundle is also a valid OKF bundle. OKF supplies the substrate the
skills depend on: one concept per file with path as concept ID, `type` as the
only strictly required field, and permissive consumption - unknown types,
unknown keys, and broken cross-links must never cause rejection.

Sections 5.1-5.5 define the trust vocabulary this repository's whole thesis
rests on: `sources` and `generated` (provenance), `verified` (trust events),
`status` and `stale_after` (lifecycle), and section 5.3's trust tiers - derived
from the actor strings, never stored. Section 7 fixes the actor convention
(`human:<id>`, `process:<id>`, `<producer>/<version>`) that makes
"confirmed by a person" a machine-checkable distinction.
